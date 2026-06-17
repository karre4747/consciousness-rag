from agents.base_agent import BaseAgent

class ScienceAgent(BaseAgent):
    """
    Agent specializing in the Science Bridge (quantum mechanics and neurobiology).
    """
    def __init__(self):
        super().__init__(name="science", collection_name="science_bridge")
