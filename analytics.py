import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import re
from database import (
    get_user_softskill_interviews,
    get_user_conceptual_interviews,
    get_user_coding_interviews
)
from openai import OpenAI

# Initialize OpenAI client (using local server for example, replace with your OpenAI API key)
client = OpenAI(
    base_url = "http://localhost:8000/v1",
    api_key = "token-abc123"
)

def parse_analysis_results(analysis_text):
    """Parse the Mistral model output to extract score, strengths and weaknesses"""
    score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', analysis_text)
    score = float(score_match.group(1)) if score_match else 5.0  # Default if parsing fails
    
    # Extract strengths
    strengths = []
    strengths_section = re.search(r'STRENGTHS:(.*?)WEAKNESSES:', analysis_text, re.DOTALL)
    if strengths_section:
        strength_text = strengths_section.group(1).strip()
        # Extract bullet points
        strengths = [s.strip().lstrip('•').strip() for s in strength_text.split('\n') if s.strip()]
    
    # Extract weaknesses
    weaknesses = []
    weaknesses_section = re.search(r'WEAKNESSES:(.*?)(?:$|ADDITIONAL)', analysis_text, re.DOTALL)
    if weaknesses_section:
        weakness_text = weaknesses_section.group(1).strip()
        # Extract bullet points
        weaknesses = [w.strip().lstrip('•').strip() for w in weakness_text.split('\n') if w.strip()]
    
    return score, strengths, weaknesses

def format_interview_data(interview, interview_type):
    """Format interview data for analysis by Mistral model"""
    formatted_data = f"Interview Date: {interview['date']}\n\n"
    
    if interview_type == "softskill":
        if "qa_pairs" in interview["results"]:
            formatted_data += "Questions and Answers:\n\n"
            for i, qa in enumerate(interview["results"]["qa_pairs"]):
                formatted_data += f"Question {i+1}: {qa['question']}\n"
                formatted_data += f"Answer: {qa['answer']}\n\n"
            
            if "evaluation" in interview["results"]:
                formatted_data += f"Previous Evaluation: {interview['results']['evaluation']}\n"
    
    elif interview_type == "conceptual":
        if "results" in interview["results"]:
            formatted_data += "Questions and Answers:\n\n"
            for i, result in enumerate(interview["results"]["results"]):
                formatted_data += f"Question {i+1}: {result['question']}\n"
                formatted_data += f"Answer: {result['answer']}\n"
                formatted_data += f"Previous Evaluation: {result['evaluation']}\n\n"
    
    elif interview_type == "coding":
        if "results" in interview["results"]:
            formatted_data += "Coding Problems and Solutions:\n\n"
            for i, result in enumerate(interview["results"]["results"]):
                formatted_data += f"Problem {i+1}: {result['question']}\n"
                formatted_data += f"Solution:\n{result['answer']}\n"
                formatted_data += f"Previous Evaluation: {result['evaluation']}\n\n"
    
    return formatted_data

def get_mistral_analysis(interview_data, interview_type):
    """
    Sends interview data to Mistral model for analysis.
    """
    if interview_type == "softskill":
        system_prompt = """
        You are an expert HR interviewer. Analyze this soft skills interview data and provide:
        1. A score from 1-10 (where 10 is excellent)
        2. A bullet-point list of 2-3 key strengths
        3. A bullet-point list of 2-3 key areas for improvement
        
        Format your response exactly as:
        SCORE: [number]
        STRENGTHS:
        • [strength 1]
        • [strength 2]
        WEAKNESSES:
        • [weakness 1]
        • [weakness 2]
        """
    elif interview_type == "conceptual":
        system_prompt = """
        You are an expert technical interviewer. Analyze this conceptual interview data and provide:
        1. A score from 1-10 (where 10 is excellent)
        2. A bullet-point list of 2-3 key strengths in technical understanding
        3. A bullet-point list of 2-3 key areas for improvement
        
        Format your response exactly as:
        SCORE: [number]
        STRENGTHS:
        • [strength 1]
        • [strength 2]
        WEAKNESSES:
        • [weakness 1]
        • [weakness 2]
        """
    elif interview_type == "coding":
        system_prompt = """
        You are an expert coding assessor. Analyze this coding interview data and provide:
        1. A score from 1-10 (where 10 is excellent)
        2. A bullet-point list of 2-3 key strengths in coding ability
        3. A bullet-point list of 2-3 key areas for improvement
        
        Format your response exactly as:
        SCORE: [number]
        STRENGTHS:
        • [strength 1]
        • [strength 2]
        WEAKNESSES:
        • [weakness 1]
        • [weakness 2]
        """
    
    messages_send = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze this interview data:\n\n{interview_data}"}
    ]
    
    response = client.chat.completions.create(
        model = "mistralai/Mistral-7B-Instruct-v0.3",
        messages = messages_send,
        temperature = 0.01,
        top_p = 0.1,
        max_tokens = 2048
    )
    
    return response.choices[0].message.content.strip()

def analyze_interview_performance(username, interview_type):
    """
    Analyzes all interviews of a specific type for a user.
    
    Args:
        username: The user to analyze
        interview_type: "softskill", "conceptual", or "coding"
        
    Returns:
        List of dictionaries with scores, strengths, and weaknesses
    """
    # Get interviews based on type
    if interview_type == "softskill":
        interviews = get_user_softskill_interviews(username)
    elif interview_type == "conceptual":
        interviews = get_user_conceptual_interviews(username)
    elif interview_type == "coding":
        interviews = get_user_coding_interviews(username)
    else:
        return []
    
    # Check if we have any interviews
    if not interviews:
        return []
    
    results = []
    
    # Process each interview
    for idx, interview in enumerate(interviews):
        with st.spinner(f"Analyzing {interview_type} interview {idx+1}..."):
            # Format interview data for analysis
            interview_data = format_interview_data(interview, interview_type)
            
            # Get analysis from Mistral model
            analysis = get_mistral_analysis(interview_data, interview_type)
            
            # Parse results
            score, strengths, weaknesses = parse_analysis_results(analysis)
            
            results.append({
                "interview_number": idx + 1,
                "date": interview["date"],
                "score": score,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "id": interview.get("id", 0)
            })
    
    return results

def create_score_chart(results, title, color_scale=None):
    """
    Creates an interactive horizontal bar chart with hover information
    
    Args:
        results: List of dictionaries with interview analysis
        title: Chart title
        color_scale: Optional plotly color scale
    
    Returns:
        Plotly figure object
    """
    if not results:
        # Return empty figure if no results
        fig = go.Figure()
        fig.update_layout(
            title=title,
            annotations=[dict(
                text="No interview data available",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5
            )]
        )
        return fig
    
    # Sort by interview number
    results = sorted(results, key=lambda x: x["interview_number"])
    
    # Extract data
    interview_numbers = [f"Interview {r['interview_number']}" for r in results]
    scores = [r["score"] for r in results]
    dates = [r["date"] for r in results]
    
    # Create hover text with strengths and weaknesses
    hover_text = []
    for r in results:
        text = f"<b>Date:</b> {r['date']}<br>"
        text += "<b>Strengths:</b><br>"
        for strength in r["strengths"]:
            text += f"• {strength}<br>"
        text += "<b>Areas for Improvement:</b><br>"
        for weakness in r["weaknesses"]:
            text += f"• {weakness}<br>"
        hover_text.append(text)
    
    # Create color gradient based on scores
    if color_scale:
        colors = px.colors.sample_colorscale(color_scale, [s/10 for s in scores])
    else:
        colors = [f"rgba(66, 133, 244, {min(score/10 + 0.3, 1.0)})" for score in scores]
    
    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=interview_numbers,
            x=scores,
            orientation='h',
            marker_color=colors,
            hovertext=hover_text,
            hoverinfo="text",
            text=[f"{s:.1f}" for s in scores],
            textposition='auto',
            customdata=dates
        )
    ])
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Score (1-10)",
            range=[0, 10],
            tickvals=[0, 2, 4, 6, 8, 10],
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title="Interview",
            autorange="reversed"  # Latest interview at top
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        plot_bgcolor='rgba(240, 240, 240, 0.8)',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_skills_radar_chart(username):
    """Creates a radar chart showing skills across different dimensions"""
    # Get latest interview results of each type
    softskill_results = analyze_interview_performance(username, "softskill")
    conceptual_results = analyze_interview_performance(username, "conceptual")
    coding_results = analyze_interview_performance(username, "coding")
    
    softskill = softskill_results[-1] if softskill_results else None
    conceptual = conceptual_results[-1] if conceptual_results else None
    coding = coding_results[-1] if coding_results else None
    
    # Define skill categories and scores
    categories = ['Communication', 'Problem Analysis', 'Technical Knowledge', 
                 'Coding Style', 'Algorithm Efficiency', 'Overall Clarity']
    
    # Calculate scores for each category (logic can be refined)
    comm_score = softskill["score"] if softskill else 0
    
    problem_score = 0
    if conceptual and coding:
        problem_score = (conceptual["score"] + coding["score"]) / 2
    elif conceptual:
        problem_score = conceptual["score"]
    elif coding:
        problem_score = coding["score"]
    
    tech_score = conceptual["score"] if conceptual else 0
    
    code_style = coding["score"] if coding else 0
    
    algo_score = coding["score"] if coding else 0
    
    overall_score = 0
    count = 0
    if softskill:
        overall_score += softskill["score"]
        count += 1
    if conceptual:
        overall_score += conceptual["score"]
        count += 1
    if coding:
        overall_score += coding["score"]
        count += 1
    
    overall_score = overall_score / count if count > 0 else 0
    
    scores = [
        comm_score,
        problem_score,
        tech_score,
        code_style,
        algo_score,
        overall_score
    ]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Skills Assessment',
        line=dict(color='rgb(31, 119, 180)'),
        fillcolor='rgba(31, 119, 180, 0.15)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        title="Skills Radar Chart",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def avg_score(username, interview_type):
    """Calculate average score for a specific interview type"""
    results = analyze_interview_performance(username, interview_type)
    if not results:
        return "N/A"
    
    avg = sum(r["score"] for r in results) / len(results)
    return f"{avg:.1f}"

def render_analytics_dashboard():
    """Renders the full analytics dashboard"""
    st.title("Interview Performance Analytics")
    
    username = st.session_state.user
    
    # Check if user has completed interviews
    has_softskill = get_user_softskill_interviews(username)
    has_conceptual = get_user_conceptual_interviews(username)
    has_coding = get_user_coding_interviews(username)
    
    if not (has_softskill or has_conceptual or has_coding):
        st.info("Complete some interviews to see analytics here!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start an Interview", key="start_from_analytics"):
                st.session_state.page = "home"
                st.rerun()
        with col2:
            if st.button("Back to Home", key="back_to_home_from_analytics"):
                st.session_state.page = "home"
                st.rerun()
        return
    
    # Create metrics at the top
    col1, col2, col3 = st.columns(3)
    
    with col1:
        soft_avg = avg_score(username, "softskill")
        st.metric("Soft Skills", soft_avg if soft_avg != "N/A" else "No data")
    
    with col2:
        concept_avg = avg_score(username, "conceptual")
        st.metric("Technical Concepts", concept_avg if concept_avg != "N/A" else "No data")
    
    with col3:
        coding_avg = avg_score(username, "coding")
        st.metric("Coding", coding_avg if coding_avg != "N/A" else "No data")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Score Progression", "Skills Radar", "Soft Skills", "Technical & Coding"])
    
    with tab1:
        st.subheader("Interview Score Progression")
        
        # Create all three charts if data exists
        if has_softskill:
            softskill_results = analyze_interview_performance(username, "softskill")
            fig = create_score_chart(softskill_results, "Soft Skills Scores", "Blues")
            st.plotly_chart(fig, use_container_width=True)
        
        if has_conceptual:
            conceptual_results = analyze_interview_performance(username, "conceptual")
            fig = create_score_chart(conceptual_results, "Technical Conceptual Scores", "Greens")
            st.plotly_chart(fig, use_container_width=True)
        
        if has_coding:
            coding_results = analyze_interview_performance(username, "coding")
            fig = create_score_chart(coding_results, "Coding Scores", "Reds")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Skills Overview")
        
        if has_softskill or has_conceptual or has_coding:
            radar_fig = create_skills_radar_chart(username)
            st.plotly_chart(radar_fig, use_container_width=True)
            
            st.markdown("""
            <div style="background-color: rgba(240, 240, 240, 0.8); padding: 15px; border-radius: 5px; margin-top: 20px;">
                <h4>Understanding the Skills Radar</h4>
                <ul>
                    <li><strong>Communication</strong>: Based on soft skills interview performance</li>
                    <li><strong>Problem Analysis</strong>: Combined score from conceptual and coding interviews</li>
                    <li><strong>Technical Knowledge</strong>: Based on conceptual interview answers</li>
                    <li><strong>Coding Style</strong>: From coding interview evaluations</li>
                    <li><strong>Algorithm Efficiency</strong>: From coding interview evaluations</li>
                    <li><strong>Overall Clarity</strong>: Average across all interview types</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Complete interviews to see your skills radar.")
    
    with tab3:
        st.subheader("Soft Skills Insights")
        
        if has_softskill:
            softskill_results = analyze_interview_performance(username, "softskill")
            
            # Most recent strengths and weaknesses
            if softskill_results:
                latest = softskill_results[-1]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Strengths")
                    for strength in latest["strengths"]:
                        st.markdown(f"✅ {strength}")
                
                with col2:
                    st.markdown("### Areas for Improvement")
                    for weakness in latest["weaknesses"]:
                        st.markdown(f"📝 {weakness}")
                
                # Detailed breakdown of all interviews
                st.markdown("### Detailed Analysis of All Soft Skills Interviews")
                for interview in softskill_results:
                    with st.expander(f"Interview {interview['interview_number']} - {interview['date']}"):
                        st.markdown(f"**Score:** {interview['score']:.1f}/10")
                        
                        st.markdown("**Strengths:**")
                        for strength in interview["strengths"]:
                            st.markdown(f"- {strength}")
                        
                        st.markdown("**Areas for Improvement:**")
                        for weakness in interview["weaknesses"]:
                            st.markdown(f"- {weakness}")
        else:
            st.info("Complete a soft skills interview to see insights.")
    
    with tab4:
        # Use subtabs for conceptual and coding
        conceptual_tab, coding_tab = st.tabs(["Technical Conceptual", "Coding"])
        
        with conceptual_tab:
            st.subheader("Technical Conceptual Insights")
            
            if has_conceptual:
                conceptual_results = analyze_interview_performance(username, "conceptual")
                
                # Most recent strengths and weaknesses
                if conceptual_results:
                    latest = conceptual_results[-1]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Strengths")
                        for strength in latest["strengths"]:
                            st.markdown(f"✅ {strength}")
                    
                    with col2:
                        st.markdown("### Areas for Improvement")
                        for weakness in latest["weaknesses"]:
                            st.markdown(f"📝 {weakness}")
                    
                    # Detailed breakdown
                    st.markdown("### Detailed Analysis of All Technical Conceptual Interviews")
                    for interview in conceptual_results:
                        with st.expander(f"Interview {interview['interview_number']} - {interview['date']}"):
                            st.markdown(f"**Score:** {interview['score']:.1f}/10")
                            
                            st.markdown("**Strengths:**")
                            for strength in interview["strengths"]:
                                st.markdown(f"- {strength}")
                            
                            st.markdown("**Areas for Improvement:**")
                            for weakness in interview["weaknesses"]:
                                st.markdown(f"- {weakness}")
            else:
                st.info("Complete a technical conceptual interview to see insights.")
        
        with coding_tab:
            st.subheader("Coding Insights")
            
            if has_coding:
                coding_results = analyze_interview_performance(username, "coding")
                
                # Most recent strengths and weaknesses
                if coding_results:
                    latest = coding_results[-1]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Strengths")
                        for strength in latest["strengths"]:
                            st.markdown(f"✅ {strength}")
                    
                    with col2:
                        st.markdown("### Areas for Improvement")
                        for weakness in latest["weaknesses"]:
                            st.markdown(f"📝 {weakness}")
                    
                    # Detailed breakdown
                    st.markdown("### Detailed Analysis of All Coding Interviews")
                    for interview in coding_results:
                        with st.expander(f"Interview {interview['interview_number']} - {interview['date']}"):
                            st.markdown(f"**Score:** {interview['score']:.1f}/10")
                            
                            st.markdown("**Strengths:**")
                            for strength in interview["strengths"]:
                                st.markdown(f"- {strength}")
                            
                            st.markdown("**Areas for Improvement:**")
                            for weakness in interview["weaknesses"]:
                                st.markdown(f"- {weakness}")
            else:
                st.info("Complete a coding interview to see insights.")
    
    # Navigation buttons at bottom
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Home", key="back_to_home_analytics"):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("Start New Interview", key="new_interview_analytics"):
            # Reset interview states
            if "softskill" in st.session_state:
                del st.session_state.softskill
            if "conceptual" in st.session_state:
                del st.session_state.conceptual
            if "coding" in st.session_state:
                del st.session_state.coding
            if "interview_type" in st.session_state:
                del st.session_state.interview_type
                
            st.session_state.page = "interview"
            st.session_state.interview_type = "softskill"
            st.rerun()
