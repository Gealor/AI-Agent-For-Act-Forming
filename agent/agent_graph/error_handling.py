from typing import List, Tuple

from langchain.messages import AIMessage
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from agent.agent_graph.states import AgentState


HARD_FIELDS = {"bik", "bank_account", "inn", "current_account"}  # требуют факта, не формата, есть контрольная сумма

def split_errors(e: ValidationError) -> Tuple[List[ErrorDetails], List[ErrorDetails]]:
    hard, soft = [], []
    for err in e.errors():
        field = err["loc"][-1]
        (hard if field in HARD_FIELDS else soft).append(err)
    return hard, soft

def hard_errors_handling(errors: List[ErrorDetails]):
    fields = ", ".join(str(err["loc"][-1]) for err in errors)
    return (
        f"Поля {fields} не прошли проверку контрольной суммы. "
        "Это не форматная ошибка — спроси у пользователя точное значение, "
        "не пытайся подобрать или исправить цифры самостоятельно."
    )


def prepare_error_components(errors: List[ErrorDetails]):
    messages = []
    for err in errors:
        loc = str(err["loc"][-1])
        msg = err["msg"].replace("Value error, ", "")
        messages.append(f"{loc}: {msg}")
    
    return messages

def soft_errors_handling(errors: List[ErrorDetails]):
    errors_text = "\n".join(message for message in prepare_error_components(errors))
    return f"Ошибка формата, попробуй исправить и вызвать инструмент снова:\n{errors_text}"