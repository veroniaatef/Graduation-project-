import streamlit as st
import time
import re
import os

# Import components from other files
from utils import apply_custom_styling, render_home_page
from auth import render_login_page, render_register_page
from database import init_database, get_user_complete_interviews, get_user_softskill_interviews, get_user_conceptual_interviews, get_user_coding_interviews
from softskill_interview import render_softskill_interview
from conceptual_interview import render_conceptual_interview
from coding_interview import render_coding_interview
from analytics import render_analytics_dashboard

# Apply custom styling
apply_custom_styling()

# Initialize database
init_database()

def render_initial_page():
    st.markdown("""
    <div class="interview-card">
        <h2 style="text-align: center; color: #2C3E50;">Welcome to the Complete Interview Platform</h2>
        <p style="text-align: center; margin-bottom: 30px;">Practice soft skills, conceptual, and coding interviews in one place</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="interview-card">
            <h3 style="text-align: center;">New User?</h3>
            <p style="text-align: center;">Create an account to track your progress</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Registration", key="register_btn"):
            st.session_state.page = "register"
            st.rerun()
    with col2:
        st.markdown("""
        <div class="interview-card">
            <h3 style="text-align: center;">Returning User?</h3>
            <p style="text-align: center;">Sign in to continue your journey</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Login", key="login_btn"):
            st.session_state.page = "login"
            st.rerun()

def render_results_page():
    st.markdown("""
    <div class="interview-card">
        <h2 style="text-align: center;">Interview Results</h2>
        <p style="text-align: center;">Thank you for completing the interview!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for each interview type
    softskill_tab, conceptual_tab, coding_tab = st.tabs(["Soft Skills Interview", "Technical Conceptual Interview", "Coding Interview"])
    
    with softskill_tab:
        if "interview_complete" in st.session_state and "softskill" in st.session_state.interview_complete:
            softskill_data = st.session_state.interview_complete["softskill"]
            
            if "skipped" in softskill_data and softskill_data["skipped"]:
                st.info("You skipped the soft skills interview section.")
            else:
                st.markdown("""
                <div class="interview-card">
                    <h3>Your Responses</h3>
                </div>
                """, unsafe_allow_html=True)
                
                for i, result in enumerate(softskill_data["qa_pairs"]):
                    st.markdown(f"""
                    <div class="interview-card">
                        <div class="question-header">Question {i+1}</div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**Question:** {result['question']}")
                    st.markdown(f"**Your Answer:** {result['answer']}")
                    
                    st.markdown("""
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="interview-card">
                    <h3>Soft Skills Evaluation</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(softskill_data["evaluation"])
        else:
            st.info("No soft skills interview data available.")
    
    with conceptual_tab:
        if "interview_complete" in st.session_state and "conceptual" in st.session_state.interview_complete:
            conceptual_data = st.session_state.interview_complete["conceptual"]
            
            if "skipped" in conceptual_data and conceptual_data["skipped"]:
                st.info("You skipped the technical conceptual interview section.")
            else:
                # Extract and display scores
                total_score = 0
                max_possible = 0
                
                for i, result in enumerate(conceptual_data["results"]):
                    st.markdown(f"""
                    <div class="interview-card">
                        <div class="question-header">Question {i+1}</div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**Question:** {result['question']}")
                    st.markdown("**Your Answer:**")
                    st.markdown(f"_{result['answer']}_")
                    
                    # Extract scores from evaluation
                    eval_text = result['evaluation']
                    
                    # Parse scores using regex if possible
                    accuracy_match = re.search(r"Accuracy:\s*(\d+)/5", eval_text)
                    clarity_match = re.search(r"Clarity:\s*(\d+)/5", eval_text)
                    completeness_match = re.search(r"Completeness:\s*(\d+)/5", eval_text)
                    final_score_match = re.search(r"Final Score:\s*(\d+)/5", eval_text)
                    
                    if accuracy_match and clarity_match and completeness_match and final_score_match:
                        accuracy = int(accuracy_match.group(1))
                        clarity = int(clarity_match.group(1))
                        completeness = int(completeness_match.group(1))
                        final_score = int(final_score_match.group(1))
                        
                        # Display scores in a nice format
                        st.markdown("""
                        <div class="feedback-card">
                            <h4>Scores:</h4>
                            <table style="width:100%">
                                <tr>
                                    <td><span class="score-label">Accuracy:</span></td>
                                    <td><span class="score-value">{}/5</span></td>
                                </tr>
                                <tr>
                                    <td><span class="score-label">Clarity:</span></td>
                                    <td><span class="score-value">{}/5</span></td>
                                </tr>
                                <tr>
                                    <td><span class="score-label">Completeness:</span></td>
                                    <td><span class="score-value">{}/5</span></td>
                                </tr>
                                <tr>
                                    <td><span class="score-label">Final Score:</span></td>
                                    <td><span class="score-value">{}/5</span></td>
                                </tr>
                            </table>
                        </div>
                        """.format(accuracy, clarity, completeness, final_score), unsafe_allow_html=True)
                        
                        total_score += final_score
                        max_possible += 5
                    
                    st.markdown("**Detailed Evaluation:**")
                    st.markdown(eval_text)
                    
                    st.markdown("""
                    </div>
                    """, unsafe_allow_html=True)
                
                # Overall performance summary
                if max_possible > 0:
                    percentage = (total_score / max_possible) * 100
                    st.markdown(f"""
                    <div class="interview-card">
                        <h3 style="text-align: center;">Overall Technical Conceptual Performance</h3>
                        <h1 style="text-align: center; color: #0066cc;">{total_score}/{max_possible} ({percentage:.1f}%)</h1>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No technical conceptual interview data available.")
    
    with coding_tab:
        if "interview_complete" in st.session_state and "coding" in st.session_state.interview_complete:
            coding_data = st.session_state.interview_complete["coding"]
            
            if "skipped" in coding_data and coding_data["skipped"]:
                st.info("You skipped the coding interview section.")
            else:
                # Extract and display results
                for i, result in enumerate(coding_data["results"]):
                    st.markdown(f"""
                    <div class="interview-card">
                        <div class="question-header">Question {i+1}</div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**Problem:** {result['question']}")
                    st.markdown("**Your Solution:**")
                    st.code(result['answer'], language='python')
                    st.markdown("**Evaluation:**")
                    st.write(result['evaluation'])
                    
                    st.markdown("""
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No coding interview data available.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Home", key="back_to_home_results"):
            # Clear interview data
            if "softskill" in st.session_state:
                del st.session_state.softskill
            if "conceptual" in st.session_state:
                del st.session_state.conceptual
            if "coding" in st.session_state:
                del st.session_state.coding
            if "interview_complete" in st.session_state:
                del st.session_state.interview_complete
            if "softskill_id" in st.session_state:
                del st.session_state.softskill_id
            if "conceptual_id" in st.session_state:
                del st.session_state.conceptual_id
            if "interview_type" in st.session_state:
                del st.session_state.interview_type
                
            st.session_state.page = "home"
            st.rerun()
    
    with col2:
        if st.button("Logout", key="logout_results"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key != "page":
                    del st.session_state[key]
            st.session_state.page = "initial"
            st.success("You have been logged out successfully!")
            time.sleep(1)
            st.rerun()

def render_history_page():
    st.markdown("""
    <div class="interview-card">
        <h2 style="text-align: center;">Your Interview History</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all types of interviews
    complete_interviews = get_user_complete_interviews(st.session_state.user)
    softskill_interviews = get_user_softskill_interviews(st.session_state.user)
    conceptual_interviews = get_user_conceptual_interviews(st.session_state.user)
    coding_interviews = get_user_coding_interviews(st.session_state.user)
    
    # Create tabs for different interview types
    complete_tab, softskill_tab, conceptual_tab, coding_tab = st.tabs(["Complete Interviews", "Soft Skills Only", "Conceptual Only", "Coding Only"])
    
    with complete_tab:
        if not complete_interviews:
            st.info("You haven't completed any full interviews yet.")
        else:
            for i, interview in enumerate(complete_interviews):
                with st.expander(f"Full Interview {i+1} - {interview['date']}"):
                    # Create tabs within the expander
                    soft_tab, tech_tab, code_tab = st.tabs(["Soft Skills", "Technical Conceptual", "Coding"])
                    
                    with soft_tab:
                        st.markdown("<h3 class='tab-subheader'>Soft Skills Results</h3>", unsafe_allow_html=True)
                        
                        # Display soft skills QA pairs
                        if "qa_pairs" in interview["softskill"]["results"]:
                            for j, qa_pair in enumerate(interview["softskill"]["results"]["qa_pairs"]):
                                st.markdown(f"#### Question {j+1}")
                                st.markdown(f"**Question:** {qa_pair['question']}")
                                st.markdown(f"**Your Answer:** {qa_pair['answer']}")
                                if j < len(interview["softskill"]["results"]["qa_pairs"]) - 1:
                                    st.divider()
                            
                            # Display evaluation
                            st.markdown("### Evaluation")
                            st.markdown(interview["softskill"]["results"]["evaluation"])
                    
                    with tech_tab:
                        st.markdown("<h3 class='tab-subheader'>Technical Conceptual Interview Results</h3>", unsafe_allow_html=True)
                        
                        # Display technical results
                        if "results" in interview["conceptual"]["results"]:
                            for j, result in enumerate(interview["conceptual"]["results"]["results"]):
                                st.markdown(f"#### Question {j+1}")
                                st.markdown(f"**Question:** {result['question']}")
                                st.markdown("**Your Answer:**")
                                st.markdown(f"_{result['answer']}_")
                                st.markdown("**Evaluation:**")
                                st.markdown(result['evaluation'])
                                if j < len(interview["conceptual"]["results"]["results"]) - 1:
                                    st.divider()
                    
                    with code_tab:
                        st.markdown("<h3 class='tab-subheader'>Coding Interview Results</h3>", unsafe_allow_html=True)
                        
                        # Display coding results if available
                        if "coding" in interview and "results" in interview["coding"]["results"]:
                            for j, result in enumerate(interview["coding"]["results"]["results"]):
                                st.markdown(f"#### Question {j+1}")
                                st.markdown(f"**Problem:** {result['question']}")
                                st.markdown("**Your Solution:**")
                                st.code(result['answer'], language='python')
                                st.markdown("**Evaluation:**")
                                st.markdown(result['evaluation'])
                                if j < len(interview["coding"]["results"]["results"]) - 1:
                                    st.divider()
                        else:
                            st.info("No coding interview data available for this session.")
    
    with softskill_tab:
        if not softskill_interviews:
            st.info("You haven't completed any soft skills interviews yet.")
        else:
            for i, interview in enumerate(softskill_interviews):
                with st.expander(f"Soft Skills Interview {i+1} - {interview['date']}"):
                    if "qa_pairs" in interview["results"]:
                        for j, qa_pair in enumerate(interview["results"]["qa_pairs"]):
                            st.markdown(f"#### Question {j+1}")
                            st.markdown(f"**Question:** {qa_pair['question']}")
                            st.markdown(f"**Your Answer:** {qa_pair['answer']}")
                            if j < len(interview["results"]["qa_pairs"]) - 1:
                                st.divider()
                        
                        st.markdown("### Evaluation")
                        st.markdown(interview["results"]["evaluation"])
    
    with conceptual_tab:
        if not conceptual_interviews:
            st.info("You haven't completed any technical conceptual interviews yet.")
        else:
            for i, interview in enumerate(conceptual_interviews):
                with st.expander(f"Technical Conceptual Interview {i+1} - {interview['date']}"):
                    if "results" in interview["results"]:
                        for j, result in enumerate(interview["results"]["results"]):
                            st.markdown(f"#### Question {j+1}")
                            st.markdown(f"**Question:** {result['question']}")
                            st.markdown("**Your Answer:**")
                            st.markdown(f"_{result['answer']}_")
                            st.markdown("**Evaluation:**")
                            st.markdown(result['evaluation'])
                            if j < len(interview["results"]["results"]) - 1:
                                st.divider()
    
    with coding_tab:
        if not coding_interviews:
            st.info("You haven't completed any coding interviews yet.")
        else:
            for i, interview in enumerate(coding_interviews):
                with st.expander(f"Coding Interview {i+1} - {interview['date']}"):
                    if "results" in interview["results"]:
                        for j, result in enumerate(interview["results"]["results"]):
                            st.markdown(f"#### Question {j+1}")
                            st.markdown(f"**Problem:** {result['question']}")
                            st.markdown("**Your Solution:**")
                            st.code(result['answer'], language='python')
                            st.markdown("**Evaluation:**")
                            st.markdown(result['evaluation'])
                            if j < len(interview["results"]["results"]) - 1:
                                st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Home", key="back_to_home_history"):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("Logout", key="logout_history"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key != "page":
                    del st.session_state[key]
            st.session_state.page = "initial"
            st.success("You have been logged out successfully!")
            time.sleep(1)
            st.rerun()

def main():
    st.title("Complete Interview Practice Platform")
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "initial"
    
    # Navigation based on current page
    if st.session_state.page == "initial":
        render_initial_page()
    elif st.session_state.page == "register":
        render_register_page()
    elif st.session_state.page == "login":
        render_login_page()
    elif st.session_state.page == "home":
        if "user" in st.session_state and st.session_state.user:
            render_home_page(st.session_state.user)
        else:
            st.warning("Please login first")
            st.session_state.page = "login"
            st.rerun()
    elif st.session_state.page == "interview":
        if "user" not in st.session_state or not st.session_state.user:
            st.warning("Please login first")
            st.session_state.page = "login"
            st.rerun()
        
        # Determine which interview type to render
        if "interview_type" in st.session_state:
            if st.session_state.interview_type == "softskill":
                render_softskill_interview()
            elif st.session_state.interview_type == "conceptual":
                render_conceptual_interview()
            elif st.session_state.interview_type == "coding":
                render_coding_interview()
        else:
            st.session_state.interview_type = "softskill"
            st.rerun()
            
    elif st.session_state.page == "results":
        if "user" not in st.session_state or not st.session_state.user:
            st.warning("Please login first")
            st.session_state.page = "login"
            st.rerun()
        render_results_page()
    elif st.session_state.page == "history":
        if "user" not in st.session_state or not st.session_state.user:
            st.warning("Please login first")
            st.session_state.page = "login"
            st.rerun()
        render_history_page()
    elif st.session_state.page == "analytics":
        if "user" not in st.session_state or not st.session_state.user:
            st.warning("Please login first")
            st.session_state.page = "login"
            st.rerun()
        render_analytics_dashboard()

if __name__ == "__main__":
    main()
