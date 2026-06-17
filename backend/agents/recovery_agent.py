from agents.base_agent import BaseAgent

class RecoveryAgent(BaseAgent):
    """
    Agent specializing in Addiction Recovery and the 12 Steps.
    """
    def __init__(self):
        super().__init__(name="recovery", collection_name="addiction_recovery")
