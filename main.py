import streamlit as st
from agno_agent import AgnoAgent
from groq_agent import GroqAgent
from rag_agent import RAGAgent
from career_agent import CareerAgent
from placement_agent import PlacementAgent
import os
import uuid
import pandas as pd
import re

# Initialize agents
agno = AgnoAgent(max_context_length=12)
groq = GroqAgent()

# File selection and data loading
data_files = []
if os.path.exists('data'):
    data_files = [f for f in os.listdir('data') if f.endswith(('.csv', '.xlsx', '.xls'))]

# Initialize RAG agent with error handling
rag = None
data_loaded = False

if data_files:
    selected_file = st.sidebar.selectbox("Select data file", data_files)
    file_path = os.path.join('data', selected_file)
    
    try:
        rag = RAGAgent(file_path)
        data_loaded = True
        st.sidebar.success(f"✅ Loaded: {selected_file}")
        
        # Show data stats
        stats = rag.get_stats()
        st.sidebar.info(f"📊 {stats['total_rows']} rows, {len(stats['columns'])} columns")
        
        if st.sidebar.button("View Data Sample"):
            st.sidebar.dataframe(rag.df.head(3))
            
    except Exception as e:
        st.sidebar.error(f"❌ Error loading file: {str(e)}")
        st.sidebar.info("Using simple text search instead of semantic search")
        data_loaded = False
else:
    st.sidebar.warning("📁 No data files found in 'data' folder")

career_agent = CareerAgent(groq)
placement_agent = PlacementAgent(groq)

# Streamlit UI
st.title("🤖 Career Placement Assistant")
st.caption("With Advanced Context Continuity & Student-Friendly Insights")

# Session management
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
    st.session_state.current_mode = "General Chat"

# Sidebar
st.sidebar.header("🎯 Conversation Control")

# Mode selection
agent_mode = st.sidebar.selectbox(
    "Choose Mode",
    ["General Chat", "Career Advisor", "Placement Analysis", "Data Query"],
    index=0
)

# Display current context
if st.sidebar.button("📋 Show Conversation Context"):
    context_summary = agno.get_conversation_summary(st.session_state.session_id)
    st.sidebar.text_area("Current Context", context_summary, height=200)

# Placement statistics button
if data_loaded and rag and st.sidebar.button("📈 Show Placement Statistics"):
    placement_stats = rag.get_placement_stats()
    st.sidebar.subheader("📊 Placement Statistics Report")
    
    st.sidebar.write("**Overall Overview:**")
    st.sidebar.write(f"• Total Placements: {placement_stats.get('total_placements', 0)} students")
    st.sidebar.write(f"• Companies: {placement_stats.get('companies_count', 0)} companies")
    st.sidebar.write(f"• Different Roles: {placement_stats.get('roles_count', 0)} roles")
    st.sidebar.write(f"• Success Rate: {placement_stats.get('success_rate', 0):.1f}%")
    
    if placement_stats.get('top_companies'):
        st.sidebar.write("**🏆 Top Companies:**")
        for company_data in placement_stats['top_companies']:
            st.sidebar.write(f"• {company_data['company']}: {company_data['placements']} placements")
    
    if placement_stats.get('compensation'):
        comp = placement_stats['compensation']
        st.sidebar.write("**💰 Compensation:**")
        st.sidebar.write(f"• Average: {comp.get('average', 'N/A')} LPA")
        st.sidebar.write(f"• Highest: {comp.get('max', 'N/A')} LPA")
        st.sidebar.write(f"• Common Range: {comp.get('common_range', 'N/A')}")

# Clear context
if st.sidebar.button("🔄 Clear Conversation"):
    agno.clear_context(st.session_state.session_id)
    st.sidebar.success("Conversation cleared!")
    st.rerun()

# Quick actions for students
st.sidebar.header("🚀 Quick Actions")
if st.sidebar.button("🎯 Get Placement Stats"):
    user_input = "show me placement statistics"
elif st.sidebar.button("💼 Top Companies"):
    user_input = "which companies hire the most"
elif st.sidebar.button("💰 Salary Insights"):
    user_input = "what is the average salary"
else:
    user_input = st.chat_input("Ask about placements, careers, skills, or data...")

if user_input:
    # Update context with user message
    agno.update_context(st.session_state.session_id, "user", user_input)
    
    # Get current context and topics
    current_context = agno.get_context(st.session_state.session_id)
    conversation_topics = agno.extract_conversation_topics(st.session_state.session_id)
    
    # Prepare context-enhanced prompt
    context_summary = agno.get_conversation_summary(st.session_state.session_id)
    
    # Generate response based on mode
    response = ""
    
    if agent_mode == "General Chat":
        enhanced_prompt = f"{context_summary}\n\nCurrent question: {user_input}"
        response = groq.generate(enhanced_prompt, current_context, conversation_topics)
    
    elif agent_mode == "Career Advisor":
        if "roadmap" in user_input.lower():
            # Extract role from context if not specified
            role = user_input.lower().replace("roadmap", "").replace("for", "").strip()
            if not role and conversation_topics['roles']:
                role = conversation_topics['roles'][0]
            response = career_agent.roadmap(role)
        elif "skill" in user_input.lower():
            # Use context to enhance skill suggestions
            enhanced_prompt = f"{context_summary}\n\nWhat skills are needed: {user_input}"
            response = groq.generate(enhanced_prompt, current_context, conversation_topics)
        else:
            response = career_agent.suggest_skills(user_input)
    
    elif agent_mode == "Placement Analysis":
        if data_loaded and rag:
            if any(word in user_input.lower() for word in ['stat', 'analys', 'overview', 'summary', 'report']):
                # Enhanced statistics display
                stats = rag.get_placement_stats()
                response = "📊 **Placement Statistics Report** 📊\n\n"
                
                response += f"**📈 Overall Placement Overview:**\n"
                response += f"• Total Students Placed: {stats.get('total_placements', 0)}\n"
                response += f"• Companies Participated: {stats.get('companies_count', 0)}\n"
                response += f"• Different Roles Offered: {stats.get('roles_count', 0)}\n"
                response += f"• Placement Success Rate: {stats.get('success_rate', 0):.1f}%\n\n"
                
                if stats.get('top_companies'):
                    response += "**🏆 Top Hiring Companies:**\n"
                    for company_data in stats['top_companies']:
                        response += f"• {company_data['company']}: {company_data['placements']} placements\n"
                    response += "\n"
                
                if stats.get('top_roles'):
                    response += "**👨‍💼 Most Offered Roles:**\n"
                    for role_data in stats['top_roles']:
                        response += f"• {role_data['role']}: {role_data['count']} offers\n"
                    response += "\n"
                
                if stats.get('compensation'):
                    comp = stats['compensation']
                    response += "**💰 Compensation Insights:**\n"
                    response += f"• Average Package: {comp.get('average', 'N/A')} LPA\n"
                    response += f"• Highest Package: {comp.get('max', 'N/A')} LPA\n"
                    response += f"• Most Common Range: {comp.get('common_range', 'N/A')}\n"
                    response += f"• Based on {comp.get('count', 0)} reported packages\n\n"
                
                if stats.get('placement_types'):
                    response += "**📋 Placement Types:**\n"
                    for type_data in stats['placement_types'][:3]:
                        response += f"• {type_data['type']}: {type_data['count']} students\n"
                
                response += "\n💡 *Pro Tip: Ask about specific companies or roles for detailed information!*"
            
            elif any(word in user_input.lower() for word in ['company', 'at ', 'in ']):
                # Company search
                company = user_input
                for keyword in ['company', 'at ', 'in ']:
                    if keyword in user_input.lower():
                        company = user_input.lower().split(keyword)[-1].strip()
                        break
                
                results = rag.search_by_company(company)
                response = f"🏢 **Placements at {company.title()}:**\n\n"
                if results:
                    for i, result in enumerate(results[:5], 1):
                        role = result.get('Role', 'N/A')
                        comp = result.get('Compensation: CTC', 'N/A')
                        stipend = result.get('Stiepend (per month)', 'N/A')
                        
                        response += f"**{i}. {role}**\n"
                        response += f"   💰 Compensation: {comp}\n"
                        if pd.notna(stipend) and str(stipend) != 'Not specified':
                            response += f"   📍 Stipend: {stipend}/month\n"
                        response += "\n"
                    
                    # Add company insights
                    response += f"**📊 About {company.title()}:**\n"
                    response += f"• {len(results)} placement records found\n"
                    response += f"• Offers various roles in technology sector\n"
                    response += f"• Competitive compensation packages\n"
                else:
                    response = f"❌ No placements found for '{company}'.\n\n**Try these companies instead:**\n• Google\n• Amazon\n• Microsoft\n• Tech Mahindra\n• Infosys"
            
            elif any(word in user_input.lower() for word in ['role', 'position', 'job', 'as a']):
                # Role search
                role_name = user_input
                for keyword in ['role', 'position', 'job', 'as a']:
                    if keyword in user_input.lower():
                        role_name = user_input.lower().split(keyword)[-1].strip()
                        break
                
                results = rag.search_by_role(role_name)
                response = f"👨‍💼 **{role_name.title()} Roles:**\n\n"
                if results:
                    for i, result in enumerate(results[:5], 1):
                        company = result.get('Company', 'N/A')
                        comp = result.get('Compensation: CTC', 'N/A')
                        stipend = result.get('Stiepend (per month)', 'N/A')
                        
                        response += f"**{i}. {company}**\n"
                        response += f"   💰 Package: {comp}\n"
                        if pd.notna(stipend) and str(stipend) != 'Not specified':
                            response += f"   📍 Stipend: {stipend}/month\n"
                        response += "\n"
                    
                    # Add role insights
                    response += f"**🎯 Career Insight for {role_name.title()}:**\n"
                    response += f"• {len(results)} placement records found\n"
                    response += f"• High demand in current market\n"
                    response += f"• Good growth opportunities\n"
                else:
                    response = f"❌ No roles found for '{role_name}'.\n\n**Try these popular roles:**\n• Software Engineer\n• Data Analyst\n• Frontend Developer\n• Backend Developer\n• Data Scientist"
            
            else:
                # General placement question with context
                enhanced_prompt = f"{context_summary}\n\nBased on placement data, answer: {user_input}"
                response = groq.generate(enhanced_prompt, current_context, conversation_topics)
        else:
            response = "📁 Please load a data file first for placement analysis."
    
    elif agent_mode == "Data Query":
        if data_loaded and rag:
            # Handle analytical questions using Groq
            if any(word in user_input.lower() for word in ['how many', 'count of', 'number of', 'statistics of', 'percentage of', 
                                                         'highest', 'lowest', 'average', 'distribution of', 'compare']):
                response = rag.analyze_data_with_groq(user_input, groq)
            
            # Handle program-specific questions (MCA, MSc, etc.)
            elif any(program in user_input.lower() for program in ['mca', 'msc', 'b.tech', 'btech', 'bachelor', 'master']):
                # Extract program name
                program_name = None
                for program in ['mca', 'msc', 'b.tech', 'btech', 'bachelor', 'master']:
                    if program in user_input.lower():
                        program_name = program.upper()
                        break
                
                if program_name:
                    program_stats = rag.get_program_stats(program_name)
                    
                    if program_stats:
                        response = f"📊 **{program_name} Program Statistics**\n\n"
                        response += f"👥 **Total Students:** {program_stats['total_students']}\n"
                        response += f"🎯 **Placement Rate:** {program_stats['placement_rate']:.1f}%\n"
                        response += f"💰 **Average Salary:** {program_stats['average_salary']:.2f} LPA\n\n"
                        
                        if program_stats['top_companies']:
                            response += "🏆 **Top Hiring Companies:**\n"
                            for company in program_stats['top_companies']:
                                response += f"• {company['company']}: {company['count']} placements\n"
                            response += "\n"
                        
                        if program_stats['top_roles']:
                            response += "👨‍💼 **Popular Roles:**\n"
                            for role in program_stats['top_roles']:
                                response += f"• {role['role']}: {role['count']} offers\n"
                        
                        # Add insights
                        response += f"\n**💡 Insights for {program_name} Students:**\n"
                        response += f"• Strong placement opportunities available\n"
                        response += f"• Competitive salary packages\n"
                        response += f"• Diverse role options across companies\n"
                    else:
                        response = f"❌ No data found for {program_name} program.\n\nAvailable programs: {', '.join(rag.df['Class'].unique() if 'Class' in rag.df.columns else 'Not specified')}"
                else:
                    response = "Please specify the program name (e.g., MCA, MSc, B.Tech)."
            
            # Handle compensation questions
            elif any(word in user_input.lower() for word in ['lpa', 'salary', 'package', 'compensation', 'ctc']):
                comp_stats = rag.get_placement_stats().get('compensation', {})
                
                if comp_stats:
                    response = f"💰 **Compensation Analysis**\n\n"
                    response += f"📈 **Highest Package:** {comp_stats.get('max', 'N/A')} LPA\n"
                    response += f"📊 **Average Package:** {comp_stats.get('average', 'N/A')} LPA\n"
                    response += f"📉 **Lowest Package:** {comp_stats.get('min', 'N/A')} LPA\n\n"
                    
                    # Find specific examples
                    high_package = rag.df[rag.df['Compensation: CTC'] != 'Not specified'].nlargest(1, 'Compensation: CTC')
                    if not high_package.empty:
                        response += f"🏆 **Highest Package Example:**\n"
                        response += f"• Company: {high_package.iloc[0]['Company']}\n"
                        response += f"• Role: {high_package.iloc[0]['Role']}\n"
                        response += f"• Package: {high_package.iloc[0]['Compensation: CTC']}\n\n"
                    
                    response += "**💡 Salary Insights:**\n"
                    response += f"• Based on {comp_stats.get('count', 0)} reported packages\n"
                    response += f"• Competitive with industry standards\n"
                    response += f"• Good return on educational investment\n"
                else:
                    response = "❌ No compensation data available in the current dataset."
            
            else:
                # Regular semantic search
                enhanced_prompt = f"{context_summary}\n\nData query: {user_input}"
                results = rag.query(enhanced_prompt)
                
                if results and results[0]['similarity'] > 0.2:
                    result = results[0]
                    data = result['data']
                    response = "🔍 **Relevant Placement Info**\n\n"
                    important_fields = ['Company', 'Role', 'Compensation: CTC', 'Stiepend (per month)', 'Placement Origin', 'Class', 'Gender']
                    field_emojis = {
                        'Company': '🏢', 'Role': '👨‍💼', 'Compensation: CTC': '💰', 
                        'Stiepend (per month)': '📍', 'Placement Origin': '🎯',
                        'Class': '🎓', 'Gender': '👥'
                    }
                    
                    for field in important_fields:
                        if field in data and data[field] and data[field] != 'Not specified':
                            response += f"{field_emojis.get(field, '•')} **{field}:** {data[field]}\n"
                else:
                    response = "❌ No exact match found.\n\n**📊 Try analytical questions like:**\n• \"How many MCA students placed?\"\n• \"Highest package in placements\"\n• \"Average salary for developers\"\n• \"Placement statistics for MSc students\"\n• \"Company-wise placement distribution\""
        else:
            response = "📁 Please load a data file first for data analysis."
    
    # Update context with assistant response
    agno.update_context(st.session_state.session_id, "assistant", response)
    
    # Display response
    with st.chat_message("assistant"):
        st.write(response)

# Display conversation history
st.subheader("💬 Conversation History")
history = agno.get_context(st.session_state.session_id)
if history:
    for msg in history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
else:
    st.info("""
    🎯 **Welcome to Career Placement Assistant!**
    
    **Here's what I can help you with:**
    • 🏢 Company placement information
    • 👨‍💼 Role-specific insights  
    • 📊 Placement statistics and trends
    • 💰 Salary and compensation data
    • 🚀 Career guidance and skill advice
    
    **Try asking:**
    - "Show me placement statistics"
    - "Which companies hire software engineers?"
    - "What is the average salary for data scientists?"
    - "Tell me about Google placements"
    """)

# Footer with quick tips
st.sidebar.markdown("---")
st.sidebar.info("""
**💡 Quick Tips:**
- Use specific company names
- Mention role types clearly  
- Ask for statistics and trends
- Use the quick action buttons!
""")