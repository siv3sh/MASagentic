# 🤖 Career Placement Assistant

A powerful, context-aware chatbot that helps students with career guidance, placement analysis, and skill recommendations using AI and real placement data.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-00FF00?style=for-the-badge&logo=groq&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

## 🚀 Features

### 🤖 Multi-Agent System
- **General Chat Agent**: Context-aware conversations with memory
- **Career Advisor Agent**: Skill recommendations and learning roadmaps
- **Placement Analysis Agent**: Company and role-specific insights
- **Data Query Agent**: Advanced data analysis and statistics

### 📊 Data Analysis Capabilities
- **Real-time Statistics**: Placement rates, salary analysis, company rankings
- **Program-wise Analytics**: MCA, MSc, B.Tech specific insights
- **Compensation Analysis**: Highest, average, and lowest packages
- **Trend Analysis**: Placement patterns and market insights

### 🎯 Student-Friendly Features
- **Easy-to-Read Format**: Emoji-based visual output
- **Quick Action Buttons**: One-click access to common queries
- **Context Continuity**: Remembers conversation history
- **Personalized Advice**: Tailored recommendations based on queries

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Groq API account (free tier available)
- Placement data in CSV/Excel format

### Step-by-Step Setup

1. **Clone or Download the Project**
   ```bash
   # If using git
   git clone <your-repo-url>
   cd career-placement-assistant
   
   # Or simply download and extract the project files
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Activate on Windows:
   venv\Scripts\activate
   
   # Activate on Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install streamlit groq pandas sentence-transformers openpyxl scikit-learn
   ```

4. **Get Groq API Key**
   - Sign up at [Groq.com](https://console.groq.com/)
   - Go to API Keys section
   - Create a new API key

5. **Set Environment Variable**
   ```bash
   # On Windows:
   set GROQ_API_KEY=your-actual-groq-api-key-here
   
   # On Mac/Linux:
   export GROQ_API_KEY="your-actual-groq-api-key-here"
   
   # Or create a .env file in project root:
   # GROQ_API_KEY=your-actual-groq-api-key-here
   ```

6. **Prepare Your Data**
   ```bash
   mkdir data
   # Place your placement_data.csv or placement_data.xlsx in the data/ folder
   ```

## 🏃‍♂️ Quick Start

1. **Add your placement data to the data/ folder**
   - Supported formats: CSV, Excel (.xlsx, .xls)
   - Recommended columns: Company, Role, Compensation: CTC, Class, Gender, Placement Origin

2. **Run the Application**
   ```bash
   streamlit run main.py
   ```

3. **Open your browser**
   - Application will automatically open at: `http://localhost:8501`
   - If not, manually navigate to the URL

4. **Start Chatting!**
   - Select your data file from the sidebar
   - Choose conversation mode
   - Ask questions about placements, careers, or skills

## 📁 Project Structure

```
career-placement-assistant/
├── main.py                 # Main Streamlit application
├── agno_agent.py          # Context management system
├── groq_agent.py          # Groq API integration
├── rag_agent.py           # Data analysis and query system
├── career_agent.py        # Career guidance module
├── placement_agent.py     # Placement analysis module
├── data/                  # Placement data storage
│   └── your_data.csv      # Your placement data file
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
└── README.md             # This documentation file
```

## 🎮 Usage Examples

### 💬 General Conversation
```
"Hello! What can you help me with?"
"Tell me about yourself"
"Explain how you work"
```

### 🎯 Career Guidance
```
"skills needed for data science"
"roadmap to become frontend developer"
"career options for computer science"
```

### 📊 Placement Analysis
```
"show placement statistics"
"companies hiring at Google"
"roles available for developers"
```

### 🔍 Advanced Data Queries
```
"highest package this year"
"how many MCA students placed"
"average salary for MSc students"
"placement rate percentage"
"gender distribution in placements"
```

## 🏆 Sample Outputs

### Statistical Report
```
📊 Placement Statistics Report

👥 Total Students: 150
🎯 Placement Rate: 85.3%
💰 Average Package: 8.5 LPA
🏆 Highest Package: 15.0 LPA

TOP COMPANIES:
• Google: 15 placements
• Amazon: 12 placements
• Microsoft: 10 placements

TOP ROLES:
• Software Engineer: 25 offers
• Data Analyst: 18 offers
• Frontend Developer: 15 offers
```

### Company Analysis
```
🏢 Google Placement Analysis

📊 Total Placements: 15 students
💰 Average Package: 12.5 LPA
🎯 Placement Rate: 100%

ROLES OFFERED:
• Data Scientist - 12-15 LPA
• Software Engineer - 10-13 LPA
• ML Engineer - 13-15 LPA

💡 Insights: Google offers competitive packages with focus on technical roles
```

### Program-wise Analysis
```
🎓 MCA Program Statistics

👥 Total Students: 45
✅ Placed: 40 students (88.9%)
💰 Average Salary: 8.2 LPA

TOP HIRERS:
• Google: 8 placements
• Amazon: 6 placements
• Microsoft: 5 placements

POPULAR ROLES:
• Software Engineer: 15 offers
• Data Analyst: 8 offers
• DevOps Engineer: 5 offers
```

## ⚙️ Configuration

### Data Format Requirements
Your CSV/Excel should include these columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| `Company` | Hiring company name | Google, Amazon |
| `Role` | Job position | Software Engineer, Data Analyst |
| `Compensation: CTC` | Salary package | 10-12 LPA, 8.5 LPA |
| `Class` | Student program | MCA A, MSc AIML, B.Tech CSE |
| `Gender` | Student gender | Male, Female |
| `Placement Origin` | Placement source | Department, CPCG, Off Campus |
| `Stiepend (per month)` | Monthly stipend | 30,000, 25,000 |

### Environment Variables
Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
MODEL_NAME=mixtral-8x7b-32768
```

## 🛠️ Customization

### Adding New Analysis Types
Edit `rag_agent.py` to add custom analysis functions:

```python
def analyze_custom_metric(self):
    # Add your custom analysis logic
    pass
```

### Modifying Response Format
Update templates in `main.py`:

```python
# Customize output format
response = f"🎯 Your Custom Format\n\n• Metric: {value}\n• Insight: {insight}"
```

## 📊 Supported Analysis Types

### Statistical Analysis
- ✅ Student count by program
- ✅ Placement rates and percentages
- ✅ Salary distribution analysis
- ✅ Company participation statistics
- ✅ Role popularity trends

### Comparative Analysis
- ✅ Program-wise comparison (MCA vs MSc)
- ✅ Company-wise placement patterns
- ✅ Gender distribution analysis
- ✅ Placement source effectiveness

### Trend Analysis
- ✅ Compensation trends over time
- ✅ Role demand patterns
- ✅ Company hiring trends
- ✅ Program performance analysis

## 🚀 Performance Optimization

1. **Data Size**: Optimal performance with 100-5,000 records
2. **Column Names**: Maintain consistent naming conventions
3. **API Usage**: Groq has rate limits - optimize query frequency
4. **Caching**: Streamlit caching improves performance for repeated queries

## 🐛 Troubleshooting

### Common Issues & Solutions

1. **"Error loading file"**
   - Ensure file is in `data/` folder
   - Check file format (CSV/Excel)
   - Verify column names match expected format

2. **"No API key found"**
   - Set GROQ_API_KEY environment variable
   - Restart the application after setting variable

3. **"No data found"**
   - Check if data file is selected in sidebar
   - Verify data file contains required columns

4. **Slow responses**
   - Reduce data size if possible
   - Check internet connection for API calls

### Debug Mode
Enable debug information by setting:
```python
# In agno_agent.py
self.debug = True
```

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/AmazingFeature`
3. **Commit** changes: `git commit -m 'Add AmazingFeature'`
4. **Push** to branch: `git push origin feature/AmazingFeature`
5. **Open** a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install black flake8 pytest

# Run code formatting
black .

# Run linting
flake8 .

# Run tests
pytest
```

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
1. **Check Documentation**: This README file
2. **Browse Issues**: Check existing issues for solutions
3. **Create New Issue**: For bugs or feature requests
4. **Email Support**: siv3sh@gmail.com

### Community
- **GitHub Discussions**: For questions and ideas
- **Discord Channel**: Community support
- **Weekly Office Hours**: Live help sessions

## 🙏 Acknowledgments

- **Groq Team** for powerful LLM inference API
- **Streamlit Team** for amazing web app framework
- **SentenceTransformers** for semantic search capabilities
- **Open Source Community** for continuous improvements
- **Beta Testers** for valuable feedback and testing

## 📞 Contact

- **Project Maintainer**: Sivesh Pb
- **Email**: siv3sh@gmail.com


---

**⭐ If this project helped you, please give it a star on GitHub!**

**🐛 Found a bug? Please open an issue so we can fix it!**

**💡 Have an idea? We'd love to hear your suggestions!**
