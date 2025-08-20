from typing import Dict, List  # Added import

class CareerAgent:
    def __init__(self, groq_agent):
        self.groq = groq_agent

    def suggest_skills(self, domain: str) -> str:
        prompt = f"Suggest top 5 in-demand skills for {domain} in 2024 with brief explanations."
        return self.groq.generate(prompt, [])

    def roadmap(self, role: str) -> str:
        prompt = f"Create a 3-month learning roadmap for {role} with weekly milestones."
        return self.groq.generate(prompt, [])