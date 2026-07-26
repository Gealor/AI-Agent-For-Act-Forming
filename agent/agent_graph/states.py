from langgraph.graph import MessagesState


class AgentState(MessagesState):
    summary: str  # Поле для хранения краткого содержания