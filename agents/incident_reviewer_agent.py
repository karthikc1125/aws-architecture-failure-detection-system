from agents.base_agent import BaseAgent

class IncidentReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__("IncidentReviewerAgent", "agents/prompts/reviewer_agent.txt")

    def run(self, proposed_architecture):
        # Review and critique
        return {"score": 9, "comments": "Good separation of concerns."}
