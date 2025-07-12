import streamlit as st
import pandas as pd
import re
import random
from openai import OpenAI
from database import save_coding_results, save_complete_interview
import time

# Initialize OpenAI client (using local server for example, replace with your OpenAI API key)
client = OpenAI(
    base_url = "http://localhost:8000/v1",
    api_key = "token-abc123"
)

# Load questions from CSV or create sample questions
try:
    df = pd.read_csv("/kaggle/input/python-code-instruction-dataset/train.csv")
except:
    # Create sample dataframe if file doesn't exist
    data = {
        'instruction': ['Write a function to reverse a string', 
                        'Implement bubble sort in Python',
                        'Create a function to calculate factorial',
                        'Write a function to check if a string is a palindrome',
                        'Create a function to find the maximum value in a list',
                        'Write a function to count the frequency of elements in a list'],
        'input': ['"hello"', '[3,1,2]', '5', '"racecar"', '[4,2,9,7,1]', '[1,2,2,3,1,4,1]'],
        'output': ['"olleh"', '[1,2,3]', '120', 'True', '9', '{1: 3, 2: 2, 3: 1, 4: 1}']
    }
    df = pd.DataFrame(data)
    # Try to save for future use
    try:
        df.to_csv("python_coding_questions.csv", index=False)
    except:
        pass

def extract_final_decision(text):
    matches = re.findall(r"<decision>(.*?)</decision>", text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1].strip().lower()
    return None

def check_question(user_answer):
    """Checks if the user's input is valid Python code without natural language explanations"""
    system_prompt = """##Instructions: You are a grader evaluating whether a user's response is valid Python code **without any additional natural language explanations or context outside the code block**.
- The response should contain only Python code — it may include normal Python elements such as function docstrings, inline comments, and print statements, as these are part of standard Python code.
- Do not consider function docstrings, inline code comments (lines starting with #), or print statements as natural language explanations **if they are embedded within the code as normal documentation or logging**.
- If there is any text **before or after the code block** that is an explanation, summary, or context **outside the code**, respond with "False".
- If the response is only valid Python code (including docstrings, comments, and print statements) **with no additional explanation**, respond with "True".
- Provide only "True" or "False" as your answer.
## Output Format: Your final decision must be provided within tags <decision></decision>, such as <decision>True</decision>, or <decision>False</decision>.
"""
    messages_send = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"User response: {user_answer}"},
    ]
    response = client.chat.completions.create(
    model = "mistralai/Mistral-7B-Instruct-v0.3",
    messages = messages_send,
    temperature = 0.01,
    top_p=0.1,
    max_tokens = 2048)
    return extract_final_decision(response.choices[0].message.content.strip())

def off_topic_response():
    st.markdown("""
    <div class="error-message">
        <h4>Code Format Required</h4>
        <p>Your answer should be Python code only. Please provide a code solution without additional text explanations outside the code.</p>
    </div>
    """, unsafe_allow_html=True)

def retrieve_question():
    sampled_question = df.sample(n=1)
    question = sampled_question['instruction'].values[0]
    question_inputs = sampled_question['input'].values[0]
    question_ground_truth = sampled_question['output'].values[0]
    return question, question_inputs, question_ground_truth

def llm_eval(question, question_inputs, question_ground_truth, user_answer):
    """Evaluates the user's coding solution using LLM"""
    system_prompt = r"""##Instructions: You are a highly experienced and strict Python code reviewer. Your role is to critically analyze a user's solution based on the following assignment. Consider the problem statement, the inputs (such as arrays, strings, etc.), and the user's submitted code. Make sure to address how well the code meets the task goal, handles edge cases, and matches the expected output.
Please examine the code's:
- **Correctness**: Does it return the right result for the given task? Does it handle the inputs and match the expected output/behavior?  
  - If the solution significantly deviates from the ground truth or lacks essential parts/logic needed to implement the correct answer, the final rating should reflect this omission.
- **Code Quality**: Is it readable, logically organized, and does it follow good Python practices?
- **Efficiency**: Does it avoid unnecessary complexity or operations?
- **Suggestions for Improvement**: Provide specific, actionable steps the user can take to improve their solution.

##Use the rubric below for your final rating (1–5). Choose the one that best fits the overall quality and correctness:
1. **Score 1** – The response is entirely incorrect or fails to address the task. Major issues throughout.  
2. **Score 2** – Partially accurate but has significant errors or omissions that affect correctness.  
3. **Score 3** – Mostly correct but lacks clarity or includes minor issues that affect completeness.  
4. **Score 4** – Accurate and clear, with only minor omissions or minor inaccuracies.  
5. **Score 5** – Complete, accurate, and thoroughly addresses every aspect of the task with no errors.

##Provide your structured feedback with all five sections below. **Do not skip or summarize** any section:
1. **Correctness** – Do they solve the problem? Does the code produce the correct output for all required conditions?  
2. **Code Quality** – Is the code well structured, readable, and logically sound?  
3. **Efficiency** – Are there any avoidable complexities or optimizations needed?  
4. **Suggestions for Improvement** – What should the user improve, and why?  
5. **Final Rating (1–5)** – Provide the numeric rating from the rubric above, along with a brief explanation.

#Note: Don't ever include in your answer instructions or any of the inputs provided to you. You must only respond with evaluation.

##Inputs:
###Problem Statement:\n{prp_statement}
###Problem Inputs:\nCode Context(e.g., arrays, strings, constraints, etc.):{prp_inputs}
###Problem Ground Truth Output:\n{prp_gt}\n
"""
    system_prompt = system_prompt.replace("{prp_statement}", str(question))
    system_prompt = system_prompt.replace("{prp_inputs}", str(question_inputs))
    system_prompt = system_prompt.replace("{prp_gt}", str(question_ground_truth))
    
    messages_send = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"User's Answer Code:\n{user_answer}\n"}
    ]
    response = client.chat.completions.create(
    model = "mistralai/Mistral-7B-Instruct-v0.3",
    messages = messages_send,
    temperature = 0.01,
    top_p=0.1,
    max_tokens = 2048)
    return response.choices[0].message.content.strip()

def init_coding_interview():
    if "coding" not in st.session_state:
        # Initialize new interview
        st.session_state.coding = {
            "count": 0,
            "question": "",
            "inputs": "",
            "ground_truth": "",
            "results": [],
            "conversation_started": False
        }
        # Get first question
        question, inputs, gt = retrieve_question()
        st.session_state.coding.update({
            "question": question,
            "inputs": inputs,
            "ground_truth": gt,
            "conversation_started": True
        })

def render_coding_interview():
    # Initialize interview if needed
    if "coding" not in st.session_state:
        init_coding_interview()
    
    st.markdown(f"""
    <div class="interview-card">
        <h2 style="text-align: center;">Coding Interview</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="interview-card">
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="question-header">Question {st.session_state.coding['count']+1}/3</div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Problem:** {st.session_state.coding['question']}")
    if st.session_state.coding['inputs']:
        st.markdown(f"**Inputs:** {st.session_state.coding['inputs']}")
    
    user_answer = st.text_area(
        "Your Python Code:",
        height=300,
        key="code_editor",
        help="Write your Python code solution here",
        placeholder="# Write your Python solution here\n\ndef solution():\n    # Your code here\n    pass"
    )
    
    if user_answer:
        st.code(user_answer, language='python')
    
    col1, col2 = st.columns([4, 1])
    with col2:
        submit_button = st.button("Submit Code", key="submit_code")
        
    if submit_button:
        if user_answer.strip():
            with st.spinner("Evaluating your code..."):
                answer_check = check_question(user_answer)
                
                if answer_check == 'true':
                    evaluation = llm_eval(
                        st.session_state.coding['question'],
                        st.session_state.coding['inputs'],
                        st.session_state.coding['ground_truth'],
                        user_answer
                    )
                    
                    st.session_state.coding['results'].append({
                        "question": st.session_state.coding['question'],
                        "answer": user_answer,
                        "evaluation": evaluation
                    })
                    
                    st.session_state.coding['count'] += 1
                    
                    if st.session_state.coding['count'] < 3:
                        question, inputs, gt = retrieve_question()
                        st.session_state.coding.update({
                            "question": question,
                            "inputs": inputs,
                            "ground_truth": gt
                        })
                        st.success("Code submitted successfully! Moving to next question...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        # Interview complete, evaluate and save
                        interview_data = {
                            "results": st.session_state.coding['results']
                        }
                        
                        # Save to database
                        coding_id = save_coding_results(st.session_state.user, interview_data)
                        
                        # Save complete interview session if all parts are done
                        if 'softskill_id' in st.session_state and 'conceptual_id' in st.session_state:
                            save_complete_interview(
                                st.session_state.user,
                                st.session_state.softskill_id,
                                st.session_state.conceptual_id,
                                coding_id
                            )
                        
                        # Store for results page
                        if 'interview_complete' not in st.session_state:
                            st.session_state.interview_complete = {}
                        
                        st.session_state.interview_complete["coding"] = interview_data
                        
                        # Move to results page
                        st.session_state.page = "results"
                        st.rerun()
                else:
                    off_topic_response()
        else:
            st.warning("Please enter your Python code before submitting.")
    
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)
