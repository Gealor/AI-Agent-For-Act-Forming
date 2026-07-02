from pathlib import Path

from langchain_openai import ChatOpenAI

from agent import LLMAgent, tools
from config import settings

system_prompt = '''
Ты бухгалтер и твоя задача получить из файла/фотографии данные заказчика и составить Акт оказанных услуг.

Для этого тебе надо взять реквизиты заказчика из приложенного файла.
Также тебе надо запросить у пользователя список работ, а также их стоимость в рублях. 
Ничего не выдумывай, все необходимое строго запроси у пользователя. 
Выведи всю информацию для пользователя, которую тебе удалось извлечь, чтобы он видел промежуточный результат того, что ты получил.  
Если во время процесса, возникла ошибка, предупреди об этом пользователя и с чем именно возникла ошибка, но не придумывай новые данные и числа.  

Имя и отчество Подписанта сокращай до первой буквы, фамилию не меняй и не сокращай, например, Иванов И.А. 
Название компании оборачиваем в кавычки ёлочкой, например, ООО «Рога и копыта», то есть до названия компании ставим « и после названия ставим », 
если это ИП, то его фамилию, имя и отчество сохраняй без изменений и сокращений, например, ИП Иванов Иван Иванович, без оборачивания в « и ».
'''

def print_agent_response(llm_response: str) -> None:
    print(f"\033[35m[AI]: {llm_response}\033[0m")

def get_user_prompt() -> str:
    return input("\n[You]: ")

def main():
    llm = ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        base_url=settings.LLM_URL,
        api_key=settings.LLM_API_KEY,
    )

    agent = LLMAgent(llm, tools=tools, system_prompt=system_prompt)

    with open("agent_graph.png", "wb") as f:
        f.write(agent._agent.get_graph().draw_mermaid_png())

    file_paths: list[str | Path] | None = [settings.test_files.DOCX_2_PATH]
        
    while True:
        response = agent.invoke(get_user_prompt(), file_paths=file_paths)
        print_agent_response(response)

        if file_paths is not None:
            file_paths = None


if __name__=="__main__":
    main()