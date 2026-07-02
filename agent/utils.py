from langchain.messages import AnyMessage, HumanMessage


def find_last_human_message(messages: list[AnyMessage]) -> int:
    last_human_index = len(messages) - 1
    while last_human_index >= 0 and not isinstance(messages[last_human_index], HumanMessage):
        last_human_index -= 1

    return last_human_index


def debug_print_history_messages(messages: list[AnyMessage]):
    # ==================== DEBUG ====================
    print("\n\033[93m" + "="*40 + " [DEBUG: AGENT INPUT] " + "="*40 + "\033[0m")
    for m in messages:
        m.pretty_print() # Красивый, цветной вывод сообщений!
    print("\033[93m" + "="*102 + "\033[0m\n")
    # ===============================================


def get_summary_prompt(summary: str) -> str:
    if summary:
        summary_prompt = (
            f"This is summary of conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above."
        )
    else:
        summary_prompt = "Create a summary of the conversation above."

    return summary_prompt


def get_num_tokens(message: AnyMessage) -> int:
    num_tokens = 0

    if hasattr(message, "usage_metadata") and message.usage_metadata: # type: ignore
        # Берем total_tokens (входящие + сгенерированные)
        num_tokens = message.usage_metadata.get("total_tokens", 0) # type: ignore

    elif hasattr(message, "response_metadata") and "token_usage" in message.response_metadata:
        # Резервный вариант, если модель вернула токены по старому стандарту
        num_tokens = message.response_metadata["token_usage"].get("total_tokens", 0)

    return num_tokens