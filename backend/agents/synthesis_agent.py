from agents.base_agent import BaseAgent

class SynthesisAgent(BaseAgent):
    """
    Agent specializing in cross-domain synthesis bridging multiple collections.
    """
    def __init__(self):
        # Specifying 'synthesis' disables primary collection filters so search queries the entire DB
        super().__init__(name="synthesis", collection_name="synthesis")
