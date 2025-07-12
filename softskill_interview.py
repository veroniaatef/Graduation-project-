import streamlit as st
import random
import tempfile
import os
import time
from openai import OpenAI
from audio_recorder_streamlit import audio_recorder
import google.generativeai as genai
from database import save_softskill_results

# API setup - replace with your actual API keys
OPENAI_API_KEY = "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"
GOOGLE_API_KEY = "AIzaSyDy8QTMxDUwoVv17y_xodMtFdINKWaBQH4"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# HR interview questions
hr_questions = [
    "Tell me about yourself and your professional background.",
    "What are your greatest strengths and weaknesses?",
    "Why do you want to work for our company?",
    "Describe a challenging situation at work and how you handled it.",
    "Where do you see yourself in five years?",
    "How do you handle stress and pressure?",
    "Tell me about a time you failed and what you learned from it.",
    "How would your colleagues describe you?",
    "What motivates you to do your best work?",
    "Do you have any questions for us about the position or company?"
]

# Generate speech from text using OpenAI
def generate_speech(text):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Save to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.close()
        
        with open(temp_file.name, "wb") as f:
            response.stream_to_file(temp_file.name)
            
        return temp_file.name
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

# Transcribe audio using OpenAI Whisper
def transcribe_audio(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

# Evaluate HR interview responses using Google Generative AI
def evaluate_interview(interview_data):
    try:
        evaluation_prompt = "You are an HR expert. Evaluate this interview:\n\n"
        
        for i, qa_pair in enumerate(interview_data, 1):
            evaluation_prompt += f"Q{i}: {qa_pair['question']}\n"
            evaluation_prompt += f"A{i}: {qa_pair['answer']}\n\n"
        
        evaluation_prompt += "\nProvide a detailed evaluation with these sections:\n"
        evaluation_prompt += "1. Communication Skills\n"
        evaluation_prompt += "2. Content of Responses\n"
        evaluation_prompt += "3. Overall Impression\n"
        evaluation_prompt += "4. Strengths\n"
        evaluation_prompt += "5. Areas for Improvement\n"
        evaluation_prompt += "6. Final Rating (1-5 scale)"
        
        response = model.generate_content(evaluation_prompt)
        return response.text
    except Exception as e:
        st.error(f"Error evaluating interview: {str(e)}")
        return "Unable to generate evaluation. Please try again."

def init_softskill_interview():
    if "softskill" not in st.session_state:
        # Initialize new interview
        st.session_state.softskill = {
            "count": 0,
            "current_question": "",
            "audio_path": None,
            "results": [],
            "conversation_started": False
        }
        
        # Select 3 random questions for this interview
        selected_questions = random.sample(hr_questions, 3)
        st.session_state.softskill["selected_questions"] = selected_questions
        
        # Set the first question
        st.session_state.softskill["current_question"] = selected_questions[0]
        st.session_state.softskill["conversation_started"] = True
        
        # Generate audio for the first question
        with st.spinner("Generating question audio..."):
            audio_path = generate_speech(selected_questions[0])
            if audio_path:
                st.session_state.softskill["audio_path"] = audio_path
            else:
                st.error("Failed to generate audio. Please try again.")

def render_softskill_interview():
    # Initialize interview if needed
    if "softskill" not in st.session_state:
        init_softskill_interview()
    
    st.markdown(f"""
    <div class="interview-card">
        <h2 style="text-align: center;">Soft Skills Interview</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="interview-card">
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="question-header">Question {st.session_state.softskill['count']+1}/3</div>
    """, unsafe_allow_html=True)
    
    # Display the current question
    st.markdown(f"**Question:** {st.session_state.softskill['current_question']}")
    
    # Audio playback of the question
    if st.session_state.softskill["audio_path"] and os.path.exists(st.session_state.softskill["audio_path"]):
        st.audio(st.session_state.softskill["audio_path"])
    
    # Audio recording section
    st.markdown("""
    <div class="audio-recorder">
        <h4>Record Your Answer</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Add tabs for recording vs uploading
    record_tab, upload_tab = st.tabs(["Record Answer", "Upload Answer"])
    
    with record_tab:
        st.markdown("""
        <div class="recording-instructions">
            Click the microphone button below to start recording. Click again to stop.
        </div>
        """, unsafe_allow_html=True)
        
        # Audio recorder component
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e8b62c", 
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="2x"
        )
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            
            submit_recorded = st.button("Submit Recorded Answer", key="submit_recorded")
            
            if submit_recorded:
                process_audio_submission(audio_bytes, is_file=False)
    
    with upload_tab:
        audio_file = st.file_uploader("Upload your audio response (WAV format)", type=["wav"])
        
        if audio_file:
            st.audio(audio_file, format="audio/wav")
            
            submit_button = st.button("Submit Answer", key="submit_answer")
            
            if submit_button:
                process_audio_submission(audio_file, is_file=True)
    
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)

def process_audio_submission(audio_data, is_file=False):
    with st.spinner("Processing your response..."):
        # Save audio to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        if is_file:
            temp_file.write(audio_data.getvalue())
        else:
            temp_file.write(audio_data)
        temp_file.close()
        
        # Transcribe the audio
        transcript = transcribe_audio(temp_file.name)
        os.unlink(temp_file.name)  # Delete the temp file
        
        if transcript:
            st.success("Your answer has been recorded.")
            
            # Save question and answer
            st.session_state.softskill['results'].append({
                "question": st.session_state.softskill['current_question'],
                "answer": transcript
            })
            
            st.session_state.softskill['count'] += 1
            
            # Check if interview is complete
            if st.session_state.softskill['count'] < 3:
                # Move to next question
                next_question = st.session_state.softskill["selected_questions"][st.session_state.softskill['count']]
                st.session_state.softskill["current_question"] = next_question
                
                # Generate audio for the next question
                with st.spinner("Generating next question audio..."):
                    audio_path = generate_speech(next_question)
                    if audio_path:
                        # Clean up previous audio file
                        if st.session_state.softskill["audio_path"] and os.path.exists(st.session_state.softskill["audio_path"]):
                            os.unlink(st.session_state.softskill["audio_path"])
                            
                        st.session_state.softskill["audio_path"] = audio_path
                        st.rerun()
                    else:
                        st.error("Failed to generate audio. Please try again.")
            else:
                # Interview complete, evaluate
                with st.spinner("Evaluating your interview..."):
                    evaluation = evaluate_interview(st.session_state.softskill['results'])
                    
                    # Store the evaluation
                    interview_data = {
                        "qa_pairs": st.session_state.softskill['results'],
                        "evaluation": evaluation
                    }
                    
                    # Save to database
                    softskill_id = save_softskill_results(st.session_state.user, interview_data)
                    
                    # Store ID for later combining with conceptual interview
                    st.session_state.softskill_id = softskill_id
                    
                    # Clean up audio file
                    if st.session_state.softskill["audio_path"] and os.path.exists(st.session_state.softskill["audio_path"]):
                        os.unlink(st.session_state.softskill["audio_path"])
                        st.session_state.softskill["audio_path"] = None
                    
                    # Move to conceptual interview
                    st.session_state.interview_type = "conceptual"
                    st.session_state.interview_complete = {
                        "softskill": interview_data
                    }
                    st.rerun()
        else:
            st.error("Failed to transcribe your answer. Please try again.")
