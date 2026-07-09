import logging

from langchain.messages import AnyMessage, HumanMessage
from logger import log

# TODO: добавить возможность вытащить индекс не последнего сообщения человека, а N последних сообщений человека.
def find_last_human_message(messages: list[AnyMessage]) -> int:
    last_human_index = len(messages) - 1
    while last_human_index >= 0 and not isinstance(messages[last_human_index], HumanMessage):
        last_human_index -= 1

    return last_human_index


def debug_print_history_messages(messages: list[AnyMessage]):
    # ==================== DEBUG ====================
    log.debug("\n\033[93m" + "="*40 + " [DEBUG: AGENT INPUT] " + "="*40 + "\033[0m")
    if log.isEnabledFor(logging.DEBUG):
        for m in messages:
            m.pretty_print() # Красивый, цветной вывод сообщений!
    log.debug("\033[93m" + "="*102 + "\033[0m\n")
    # ===============================================

# может меняться от одной модели к другой. Стоит вынести в логику конкретной модели (у некоторых провайдеров/моделей может быть другая логика подсчета)
def get_num_tokens(message: AnyMessage) -> int:
    num_tokens = 0

    if hasattr(message, "usage_metadata") and message.usage_metadata: # type: ignore
        # Берем total_tokens (входящие + сгенерированные)
        num_tokens = message.usage_metadata.get("total_tokens", 0) # type: ignore

    elif hasattr(message, "response_metadata") and "token_usage" in message.response_metadata:
        # Резервный вариант, если модель вернула токены по старому стандарту
        num_tokens = message.response_metadata["token_usage"].get("total_tokens", 0)

    return num_tokens