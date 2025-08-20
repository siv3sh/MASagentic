from typing import Dict, List  # Added import

class PlacementAgent:
    def __init__(self, groq_agent):
        self.groq = groq_agent

    def interview_questions(self, company: str, role: str) -> str:
        prompt = f"Generate 5 technical and 3 behavioral questions for {role} interviews at {company}."
        return self.groq.generate(prompt, [])

    def resume_feedback(self, resume_text: str) -> str:
        prompt = f"Provide constructive feedback on this resume:\n{resume_text}"
        return self.groq.generate(prompt, [])