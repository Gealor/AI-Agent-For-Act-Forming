import hashlib
from pathlib import Path
from typing import Sequence

from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage
from langchain.tools import BaseTool
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

from agent.agent_graph.states import AgentState
from agent.agent_graph.build_agent_graph import build_agent
from file_uploaders.uploaders import FileUploaderFactory
from logger import log

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
        log.debug("Обработка файла %s для LLM...", file)
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

        messages = AgentState(messages=[HumanMessage(content=message_content)]) # type: ignore
        log.debug("Сообщение отправлено в LLM...")
        response = self._agent.invoke(
            messages,
            config=self._config,
        )
        log.debug(response["messages"][-1])

        return response["messages"][-1].content