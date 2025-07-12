import streamlit as st
import time
import sqlite3
from database import get_db_connection

def register_user(username, password):
    if not username or not password:
        return False, "Please fill all fields"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another username."
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(username, password):
    if not username or not password:
        return False, "Please fill all fields"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, "Login successful!"
        else:
            return False, "Invalid credentials"
    except Exception as e:
        return False, f"Login error: {str(e)}"

def render_login_page():
    st.markdown("""
    <div class="interview-card">
        <h2 style="text-align: center;">Login to Your Account</h2>
        <p style="text-align: center;">Continue your interview practice</p>
    </div>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Login", key="login_submit"):
            success, message = login_user(username, password)
            if success:
                st.success(message)
                st.session_state.user = username
                st.session_state.page = "home"
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)
            
    if st.button("Back", key="back_to_initial_login"):
        st.session_state.page = "initial"
        st.rerun()

def render_register_page():
    st.markdown("""
    <div class="interview-card">
        <h2 style="text-align: center;">Create New Account</h2>
        <p style="text-align: center;">Join our community of interviewees</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        username = st.text_input("Username", placeholder="Choose a unique username")
        password = st.text_input("Password", type="password", placeholder="Enter a secure password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Register", key="register_submit"):
                success, message = register_user(username, password)
                if success:
                    st.success(message + " Redirecting to login...")
                    time.sleep(1)
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(message)
            
    if st.button("Back", key="back_to_initial"):
        st.session_state.page = "initial"
        st.rerun()
