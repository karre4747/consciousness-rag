from agents.base_agent import BaseAgent

class TherapyAgent(BaseAgent):
    """
    Agent specializing in Healing Modalities and Psychotherapeutic models.
    """
    def __init__(self):
        super().__init__(name="therapy", collection_name="healing_modalities")
