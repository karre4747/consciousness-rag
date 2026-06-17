from agents.base_agent import BaseAgent

class SponsorAgent(BaseAgent):
    """
    Agent specializing in personal 12-Step sponsorship guidance.
    """
    def __init__(self):
        super().__init__(name="sponsor", collection_name="addiction_recovery")
