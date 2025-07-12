import streamlit as st

def apply_custom_styling():
    """Apply custom CSS styling to the application"""
    st.markdown("""
    <style>
        .main {
            background-color: #f5f7f9;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px 20px;
            transition: all 0.3s;
        }
        .stButton button:hover {
            background-color: #45a049;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .interview-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .question-header {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2C3E50;
        }
        .code-editor {
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f8f8f8;
            font-family: monospace;
        }
        .success-message {
            padding: 10px;
            background-color: #d4edda;
            color: #155724;
            border-radius: 5px;
            border-left: 5px solid #28a745;
            margin: 10px 0;
        }
        .error-message {
            padding: 10px;
            background-color: #f8d7da;
            color: #721c24;
            border-radius: 5px;
            border-left: 5px solid #dc3545;
            margin: 10px 0;
        }
        .feedback-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .score-label {
            font-weight: bold;
            color: #495057;
        }
        .score-value {
            color: #0066cc;
            font-weight: bold;
        }
        .tab-subheader {
            color: #2C3E50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .stButton.skip-button button {
            background-color: #6c757d;
            color: white;
            font-size: 0.9rem;
            padding: 8px 16px;
        }
        .stButton.skip-button button:hover {
            background-color: #5a6268;
        }
        
        /* Analytics Dashboard Styling */
        .metric-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            text-align: center;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #0066cc;
        }
        .metric-label {
            font-size: 1rem;
            color: #6c757d;
        }
        .strength-item {
            background-color: #e8f4ea;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #28a745;
        }
        .weakness-item {
            background-color: #fff4e6;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #fd7e14;
        }
        .chart-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin: 15px 0;
        }
        .info-box {
            background-color: rgba(240, 240, 240, 0.8);
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_home_page(username):
    """Render the home page after login"""
    st.markdown(f"""
    <div class="interview-card">
        <h2 style="text-align: center;">Welcome, {username}! 👋</h2>
        <p style="text-align: center;">What would you like to do today?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Interview section
    st.markdown("""
    <div class="interview-card">
        <h3 style="text-align: center;">Interview Practice</h3>
        <p style="text-align: center;">Prepare for your next job interview</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="interview-card">
            <h4 style="text-align: center;">Start New Interview</h4>
            <p style="text-align: center;">Begin a complete interview session</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Interview", key="start_interview"):
            # Initialize new interview
            # Clear any existing interview data
            if "softskill" in st.session_state:
                del st.session_state.softskill
            if "conceptual" in st.session_state:
                del st.session_state.conceptual
            if "coding" in st.session_state:
                del st.session_state.coding
            if "interview_complete" in st.session_state:
                del st.session_state.interview_complete
                
            # Start with soft skills interview
            st.session_state.interview_type = "softskill"
            st.session_state.page = "interview"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="interview-card">
            <h4 style="text-align: center;">Practice Specific Skills</h4>
            <p style="text-align: center;">Focus on one interview type</p>
        </div>
        """, unsafe_allow_html=True)
        practice_type = st.selectbox(
            "Select interview type to practice", 
            ["Soft Skills", "Technical Conceptual", "Coding"],
            key="practice_type"
        )
        
        if st.button("Start Practice", key="start_practice"):
            # Map selection to interview type
            if practice_type == "Soft Skills":
                interview_type = "softskill"
            elif practice_type == "Technical Conceptual":
                interview_type = "conceptual"
            else:
                interview_type = "coding"
                
            # Clear any existing interview data
            if "softskill" in st.session_state:
                del st.session_state.softskill
            if "conceptual" in st.session_state:
                del st.session_state.conceptual
            if "coding" in st.session_state:
                del st.session_state.coding
            if "interview_complete" in st.session_state:
                del st.session_state.interview_complete
                
            # Start selected interview type
            st.session_state.interview_type = interview_type
            st.session_state.page = "interview"
            st.rerun()
    
    # Analytics and History section
    st.markdown("""
    <div class="interview-card">
        <h3 style="text-align: center;">Track Your Progress</h3>
        <p style="text-align: center;">View your performance and history</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="interview-card">
            <h4 style="text-align: center;">Performance Analytics</h4>
            <p style="text-align: center;">View your strengths and areas for improvement</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Analytics", key="view_analytics"):
            st.session_state.page = "analytics"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="interview-card">
            <h4 style="text-align: center;">Interview History</h4>
            <p style="text-align: center;">Review your past interviews</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View History", key="view_history"):
            st.session_state.page = "history"
            st.rerun()
    
    # Logout button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Logout", key="logout"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key != "page":
                    del st.session_state[key]
            st.session_state.page = "initial"
            st.rerun()
