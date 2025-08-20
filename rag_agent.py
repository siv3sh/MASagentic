import pandas as pd
import numpy as np
from typing import List, Dict, Any
import os
import re
from sentence_transformers import SentenceTransformer
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RAGAgent:
    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")
        
        # Load data
        if file_path.endswith('.csv'):
            self.df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            self.df = pd.read_excel(file_path)
        
        print(f"Loaded data with columns: {self.df.columns.tolist()}")
        print(f"Data shape: {self.df.shape}")
        
        # Clean data
        self._clean_data()
        self._create_combined_text()
        
        # Create TF-IDF vectors
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_text'])
        print(f"Created TF-IDF matrix with shape: {self.tfidf_matrix.shape}")

    def query(self, question: str, top_k=1) -> List[Dict[str, Any]]:
        """Query using TF-IDF cosine similarity - return only the most relevant result"""
        try:
            question_vec = self.vectorizer.transform([question])
            similarities = cosine_similarity(question_vec, self.tfidf_matrix).flatten()
            
            # Get only the most relevant result
            top_index = np.argmax(similarities)
            
            result = {
                'similarity': float(similarities[top_index]),
                'data': self.df.iloc[top_index].to_dict(),
                'text': self.df.iloc[top_index]['combined_text']
            }
            
            return [result] if result['similarity'] > 0.1 else []  # Only return if relevant
            
        except Exception as e:
            print(f"Error in query: {e}")
            return []

    def _clean_data(self):
        """Clean and preprocess the placement data"""
        self.df = self.df.replace('', pd.NA)
        
        # Clean specific columns
        text_columns = ['Company', 'Role', 'Compensation: CTC', 'Stiepend (per month)', 'Placement Origin']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('Not specified').astype(str).str.strip()

    def _create_combined_text(self):
        """Combine all relevant columns into a single text field"""
        text_parts = []
        
        for _, row in self.df.iterrows():
            row_text = []
            for col, value in row.items():
                if col != 'combined_text' and pd.notna(value) and str(value).strip() != '':
                    row_text.append(f"{col}: {value}")
            
            combined = " | ".join(row_text)
            text_parts.append(combined)
        
        self.df['combined_text'] = text_parts

    def get_placement_stats(self) -> Dict[str, Any]:
        """Get comprehensive placement statistics in student-friendly format"""
        stats = {}
        
        # Overall placement stats
        stats['total_placements'] = len(self.df)
        stats['companies_count'] = self.df['Company'].nunique() if 'Company' in self.df.columns else 0
        stats['roles_count'] = self.df['Role'].nunique() if 'Role' in self.df.columns else 0
        
        # Top Companies (simplified)
        if 'Company' in self.df.columns:
            company_counts = self.df['Company'].value_counts().head(5)
            stats['top_companies'] = [
                {'company': company, 'placements': count} 
                for company, count in company_counts.items() 
                if company != 'Not specified'
            ]
        
        # Top Roles (simplified)
        if 'Role' in self.df.columns:
            role_counts = self.df['Role'].value_counts().head(5)
            stats['top_roles'] = [
                {'role': role, 'count': count} 
                for role, count in role_counts.items() 
                if role != 'Not specified'
            ]
        
        # Compensation Statistics
        if 'Compensation: CTC' in self.df.columns:
            comp_stats = self._analyze_compensation()
            stats['compensation'] = comp_stats
        
        # Placement Type Analysis
        if 'Placement Origin' in self.df.columns:
            origin_counts = self.df['Placement Origin'].value_counts()
            stats['placement_types'] = [
                {'type': origin, 'count': count} 
                for origin, count in origin_counts.items() 
                if origin != 'Not specified'
            ]
        
        # Success Rate (assuming non-empty Company means successful placement)
        successful_placements = len(self.df[self.df['Company'] != 'Not specified'])
        stats['success_rate'] = (successful_placements / len(self.df)) * 100 if len(self.df) > 0 else 0
        
        return stats

    def _analyze_compensation(self) -> Dict[str, Any]:
        """Analyze compensation data for student understanding"""
        comp_data = self.df[self.df['Compensation: CTC'] != 'Not specified']['Compensation: CTC']
        numeric_values = []
        
        for comp in comp_data:
            if isinstance(comp, str):
                numbers = re.findall(r'(\d+\.?\d*)', comp.replace(',', ''))
                if numbers:
                    nums = [float(num) for num in numbers]
                    if len(nums) > 1 and any(char in comp for char in ['-', 'to']):
                        numeric_values.append(sum(nums) / len(nums))  # Average of range
                    else:
                        numeric_values.extend(nums)
        
        if numeric_values:
            return {
                'average': round(sum(numeric_values) / len(numeric_values), 2),
                'max': round(max(numeric_values), 2),
                'min': round(min(numeric_values), 2),
                'count': len(numeric_values),
                'common_range': self._get_common_range(numeric_values)
            }
        return {}

    def _get_common_range(self, values: List[float]) -> str:
        """Get the most common compensation range"""
        if not values:
            return "Not available"
        
        # Create ranges
        ranges = {
            '0-5 LPA': len([v for v in values if v <= 5]),
            '5-10 LPA': len([v for v in values if 5 < v <= 10]),
            '10-15 LPA': len([v for v in values if 10 < v <= 15]),
            '15+ LPA': len([v for v in values if v > 15])
        }
        
        most_common = max(ranges.items(), key=lambda x: x[1])
        return most_common[0] if most_common[1] > 0 else "Not available"

    def analyze_data_with_groq(self, question: str, groq_agent) -> str:
        """Use Groq to analyze the data and answer complex questions"""
        try:
            # Create a data summary for Groq to analyze
            data_summary = self._create_data_summary()
            
            prompt = f"""
            You are a data analyst. Analyze the following placement data and answer the question.

            PLACEMENT DATA SUMMARY:
            {data_summary}

            QUESTION: {question}

            REQUIREMENTS:
            1. Analyze the actual data to provide accurate statistics
            2. Be specific and quantitative
            3. Include numbers and percentages where possible
            4. Provide insights based on the data
            5. If the question can't be answered from the data, explain why

            ANSWER:
            """
            
            response = groq_agent.generate(prompt, [], {})
            return response
            
        except Exception as e:
            return f"Error analyzing data: {str(e)}"

    def _create_data_summary(self) -> str:
        """Create a comprehensive summary of the data for Groq analysis"""
        summary = f"Total Records: {len(self.df)}\n\n"
        
        # Company analysis
        if 'Company' in self.df.columns:
            company_counts = self.df['Company'].value_counts()
            summary += "TOP COMPANIES:\n"
            for company, count in company_counts.head(5).items():
                if company != 'Not specified':
                    summary += f"- {company}: {count} placements\n"
            summary += "\n"
        
        # Role analysis
        if 'Role' in self.df.columns:
            role_counts = self.df['Role'].value_counts()
            summary += "TOP ROLES:\n"
            for role, count in role_counts.head(5).items():
                if role != 'Not specified':
                    summary += f"- {role}: {count} roles\n"
            summary += "\n"
        
        # Compensation analysis
        if 'Compensation: CTC' in self.df.columns:
            comp_stats = self._analyze_compensation()
            summary += "COMPENSATION STATS:\n"
            summary += f"- Average: {comp_stats.get('average', 'N/A')} LPA\n"
            summary += f"- Highest: {comp_stats.get('max', 'N/A')} LPA\n"
            summary += f"- Lowest: {comp_stats.get('min', 'N/A')} LPA\n"
            summary += "\n"
        
        # Class/Program analysis (if available)
        if 'Class' in self.df.columns:
            class_counts = self.df['Class'].value_counts()
            summary += "PROGRAM DISTRIBUTION:\n"
            for program, count in class_counts.items():
                summary += f"- {program}: {count} students\n"
            summary += "\n"
        
        # Gender analysis (if available)
        if 'Gender' in self.df.columns:
            gender_counts = self.df['Gender'].value_counts()
            summary += "GENDER DISTRIBUTION:\n"
            for gender, count in gender_counts.items():
                percentage = (count / len(self.df)) * 100
                summary += f"- {gender}: {count} students ({percentage:.1f}%)\n"
            summary += "\n"
        
        # Placement origin analysis
        if 'Placement Origin' in self.df.columns:
            origin_counts = self.df['Placement Origin'].value_counts()
            summary += "PLACEMENT SOURCES:\n"
            for origin, count in origin_counts.items():
                if origin != 'Not specified':
                    percentage = (count / len(self.df)) * 100
                    summary += f"- {origin}: {count} placements ({percentage:.1f}%)\n"
        
        return summary

    def get_program_stats(self, program_name: str) -> Dict[str, Any]:
        """Get statistics for specific program (MCA, MSc, etc.)"""
        if 'Class' not in self.df.columns:
            return {}
        
        program_data = self.df[self.df['Class'].str.contains(program_name, case=False, na=False)]
        
        if len(program_data) == 0:
            return {}
        
        stats = {
            'total_students': len(program_data),
            'placement_rate': 0,
            'top_companies': [],
            'top_roles': [],
            'average_salary': 0
        }
        
        # Calculate placement rate (students with company assigned)
        placed_students = program_data[program_data['Company'] != 'Not specified']
        stats['placement_rate'] = (len(placed_students) / len(program_data)) * 100 if len(program_data) > 0 else 0
        
        # Top companies for this program
        if 'Company' in program_data.columns:
            company_counts = program_data['Company'].value_counts().head(3)
            stats['top_companies'] = [{'company': comp, 'count': count} for comp, count in company_counts.items() if comp != 'Not specified']
        
        # Top roles for this program
        if 'Role' in program_data.columns:
            role_counts = program_data['Role'].value_counts().head(3)
            stats['top_roles'] = [{'role': role, 'count': count} for role, count in role_counts.items() if role != 'Not specified']
        
        # Average salary for this program
        if 'Compensation: CTC' in program_data.columns:
            comp_values = []
            for comp in program_data['Compensation: CTC']:
                if comp != 'Not specified':
                    numbers = re.findall(r'(\d+\.?\d*)', str(comp).replace(',', ''))
                    if numbers:
                        nums = [float(num) for num in numbers]
                        comp_values.append(sum(nums) / len(nums))
            
            if comp_values:
                stats['average_salary'] = sum(comp_values) / len(comp_values)
        
        return stats

    def get_columns(self) -> List[str]:
        return self.df.columns.tolist()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_rows': len(self.df),
            'columns': self.get_columns(),
            'companies': self.df['Company'].dropna().unique().tolist() if 'Company' in self.df.columns else [],
            'roles': self.df['Role'].dropna().unique().tolist() if 'Role' in self.df.columns else []
        }

    def search_by_company(self, company_name: str) -> List[Dict]:
        if 'Company' not in self.df.columns:
            return []
        
        results = self.df[self.df['Company'].str.contains(company_name, case=False, na=False)]
        return results.to_dict('records')

    def search_by_role(self, role_name: str) -> List[Dict]:
        if 'Role' not in self.df.columns:
            return []
        
        results = self.df[self.df['Role'].str.contains(role_name, case=False, na=False)]
        return results.to_dict('records')