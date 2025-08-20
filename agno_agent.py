from typing import Dict, List
import re

class AgnoAgent:
    def __init__(self, max_context_length=10):
        self.context: Dict[str, List[Dict]] = {}
        self.max_context_length = max_context_length

    def update_context(self, session_id: str, role: str, content: str):
        if session_id not in self.context:
            self.context[session_id] = []
        
        self.context[session_id].append({"role": role, "content": content})
        
        if len(self.context[session_id]) > self.max_context_length:
            self.context[session_id] = self.context[session_id][-self.max_context_length:]

    def get_context(self, session_id: str) -> List[Dict]:
        return self.context.get(session_id, [])

    def clear_context(self, session_id: str):
        if session_id in self.context:
            self.context[session_id] = []

    def get_conversation_summary(self, session_id: str) -> str:
        """Create a summary of the conversation for context continuity"""
        context = self.get_context(session_id)
        if not context:
            return "No previous conversation."
        
        summary = "Conversation History:\n"
        for msg in context:
            summary += f"{msg['role']}: {msg['content']}\n"
        
        return summary

    def extract_conversation_topics(self, session_id: str) -> Dict[str, List[str]]:
        """Extract topics, companies, and roles from conversation"""
        context = self.get_context(session_id)
        topics = {
            'roles': [],
            'companies': [],
            'skills': [],
            'general_topics': []
        }
        
        for msg in context:
            content = msg['content'].lower()
            
            # Extract roles
            role_keywords = ['data scientist', 'frontend', 'backend', 'developer', 'engineer', 
                           'analyst', 'ml engineer', 'ai engineer', 'software engineer']
            for role in role_keywords:
                if role in content:
                    topics['roles'].append(role)
            
            # Extract companies
            company_keywords = ['google', 'amazon', 'microsoft', 'apple', 'meta', 'netflix',
                              'tech mahindra', 'tcs', 'infosys', 'accenture']
            for company in company_keywords:
                if company in content:
                    topics['companies'].append(company)
            
            # Extract skills
            skill_keywords = ['python', 'java', 'javascript', 'react', 'angular', 'node',
                            'machine learning', 'deep learning', 'sql', 'database']
            for skill in skill_keywords:
                if skill in content:
                    topics['skills'].append(skill)
        
        # Remove duplicates
        for key in topics:
            topics[key] = list(set(topics[key]))
        
        return topics