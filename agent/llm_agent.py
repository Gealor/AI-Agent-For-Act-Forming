import hashlib
from pathlib import Path
from typing import Sequence

from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage, RemoveMessage, SystemMessage
from langchain.tools import BaseTool
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from agent.utils import debug_print_history_messages, find_last_human_message, get_num_tokens, get_summary_prompt
from file_uploaders.uploaders import FileUploaderFactory
from config import settings


class AgentState(MessagesState):
    summary: str  # Поле для хранения краткого содержания


def build_agent(model: BaseChatModel, tools_list: Sequence[BaseTool], checkpointer, system_prompt: str | None = None):
    """Собирает граф агента с ToolNode, который умеет обрабатывать ошибки."""
    
    model_with_tools = model.bind_tools(tools_list)
    tool_node = ToolNode(tools=tools_list, handle_tool_errors=True)

    summary_model = model 
    
    def call_model(state: AgentState):
        messages = state["messages"] # Вся история сообщений
        summary = state.get("summary", "")
        print("SUMMARY: ", summary)

        sys_content = system_prompt or "You are a helpful assistant."
        if summary:
            sys_content += f"\n\nSummary of previous conversation:\n{summary}"

        sys_message = SystemMessage(content=sys_content)

        if not messages or not isinstance(messages[0], SystemMessage):
            messages_to_pass = [sys_message] + messages
        else:
            messages_to_pass = [sys_message] + messages[1:]

        debug_print_history_messages(messages_to_pass)

        response = model_with_tools.invoke(messages_to_pass)
        return {"messages": [response]}
    
    def summarize_conversation(state: AgentState):
        """Узел, который обновляет саммари и удаляет старые сообщения."""
        print("\033[96m[SYSTEM]: ЗАПУЩЕНА СУММАРИЗАЦИЯ...\033[0m")
        summary = state.get("summary", "")
        messages = state["messages"]

        last_human_index = find_last_human_message(messages)

        if last_human_index <= 0:
            print("Нечего суммаризировать (слишком мало сообщений)")
            return {}
        
        # Берем на суммаризацию всё, что было ДО последнего запроса пользователя
        # Также исключаем SystemMessage, если оно есть в начале
        messages_to_summarize = [m for m in messages[:last_human_index] if not isinstance(m, SystemMessage)]
        
        if not messages_to_summarize:
            return {} # Нечего суммаризировать

        # Формируем промпт для суммаризации
        summary_prompt = get_summary_prompt(summary)
            
        messages_for_llm = messages_to_summarize + [HumanMessage(content=summary_prompt)]
        response = summary_model.invoke(messages_for_llm)
        
        # ВАЖНО: Удаляем старые сообщения из состояния графа
        # LangGraph использует RemoveMessage(id=...) чтобы понять, что сообщение нужно стереть
        delete_messages = [RemoveMessage(id=m.id) for m in messages_to_summarize if m.id]
        
        return {
            "summary": response.content,
            "messages": delete_messages # используется метод add_messages и к истории В КОНЕЦ добавляются указанные здесь сообщения
            # при этом, если передан список RemoveMessage, то наоборот, сообщения с такими id УДАЛЯТСЯ из истории сообщений
        }
    
    # узел ветвления
    def should_continue(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls: # type: ignore
            return "tools"

        num_tokens = get_num_tokens(last_message)   
        
        print(f"\033[90m[Tokens Used: {num_tokens}]\033[0m")
        
        if num_tokens > settings.MAX_CONTEXT_WINDOW:
            return "summarize"
        
        return END
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("summarize", summarize_conversation)
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", "summarize", END])
    workflow.add_edge("tools", "agent") # Нужно, чтобы ИИ-агент смог финализировать/объяснить результат на естественном языке
    # а также обеспечивал возможность многошаговых цепочек вызовов инструментов
    workflow.add_edge("summarize", END) # Суммаризация это внутреннее действие модели, результат не должен отправляться обратно в агента, для "человекточитаемости"
    
    return workflow.compile(checkpointer=checkpointer)



class LLMAgent:
    def __init__(
        self,
        model: BaseChatModel,
        tools: Sequence[BaseTool],
        temperature: float = 0.1,
        system_prompt: str | None = None,
    ):
        self._model = model.model_copy(update={"temperature": temperature})
        # self._model = model

        self._agent = build_agent(self._model, tools, InMemorySaver(), system_prompt) # type: ignore
        self._config: RunnableConfig = {
            "configurable": {"thread_id": hashlib.sha256().hexdigest()}
        }

    def process_file(self, file: Path | str) -> dict:
        print(f"Обработка файла {file} для LLM...")
        uploader = FileUploaderFactory.get_uploader(file)
        return uploader.upload_file(file)

    def invoke(
        self,
        content: str,
        file_paths: list[str | Path] | None = None,
    ) -> str:
        """Отправляет сообщение в чат"""
        message_content: list[dict] = []
        if content:
            message_content.append({"type": "text", "text": content})

        message_content: list[dict] = [{"type": "text", "text": content}]
        if file_paths:
            for path in file_paths:
                file_dict = self.process_file(path)
                message_content.append(file_dict)

        messages = MessagesState(messages=[HumanMessage(content=message_content)]) # type: ignore
        print("Сообщение отправлено в LLM...")
        response = self._agent.invoke(
            messages,
            config=self._config,
        )
        print(response["messages"][-1])

        return response["messages"][-1].content