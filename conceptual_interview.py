import streamlit as st
import pandas as pd
import re
import random
from openai import OpenAI
from database import save_conceptual_results, save_complete_interview
import time

# Initialize OpenAI client (using local server for example, replace with your OpenAI API key)
client = OpenAI(
    base_url = "http://localhost:8000/v1",
    api_key = "token-abc123"
)

# Load questions from CSV or create sample questions
try:
    df = pd.read_csv("/kaggle/input/conceptual/Conceptual_questions_final.csv")
except:
    # Create sample dataframe if file doesn't exist
    data = {
        'question': [
            'What is the difference between supervised and unsupervised learning?',
            'Explain the bias-variance tradeoff in machine learning.',
            'What is regularization and why is it important?',
            'Explain the difference between bagging and boosting.',
            'What is the curse of dimensionality?',
            'Explain the difference between precision and recall.'
        ],
        'correct_answer': [
            'Supervised learning uses labeled data where the model learns to map inputs to known outputs, while unsupervised learning works with unlabeled data to find patterns or structure without predetermined outputs.',
            'The bias-variance tradeoff represents the balance between underfitting (high bias) and overfitting (high variance). High bias models are too simple and miss important patterns, while high variance models are too complex and capture noise in the training data.',
            'Regularization is a technique used to prevent overfitting by adding a penalty term to the loss function that discourages complex models. It helps create models that generalize better to unseen data.',
            'Bagging (Bootstrap Aggregating) trains multiple models in parallel on random subsets of data and averages predictions to reduce variance. Boosting trains models sequentially, where each new model focuses on the mistakes of previous models, reducing bias.',
            'The curse of dimensionality refers to various phenomena that arise when analyzing data in high-dimensional spaces that do not occur in low-dimensional settings. As dimensions increase, the volume of the space increases exponentially, making data sparse and distance metrics less meaningful.',
            'Precision measures the accuracy of positive predictions (true positives / all positive predictions), while recall measures the ability to find all positive instances (true positives / all actual positives). Precision focuses on minimizing false positives, while recall focuses on minimizing false negatives.'
        ]
    }
    df = pd.DataFrame(data)

def check_conceptual_answer(user_answer):
    """
    Checks if the user's input is a valid English conceptual explanation
    and not just random letters, code, or gibberish.
    """
    # Minimum length check
    if len(user_answer.strip()) < 10:
        return False

    # Check for minimum English content
    english_letters = re.findall(r'[A-Za-z]', user_answer)
    if len(english_letters) < 0.3 * len(user_answer):
        return False

    # Basic gibberish detection
    meaningful_words = re.findall(r'\b\w{3,}\b', user_answer)
    if len(meaningful_words) < 2:
        return False

    return True

def get_ground_truth_answer(question):
    system_prompt = "You are a subject matter expert. Provide a clear and concise answer to the following conceptual question."

    messages_send = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    
    response = client.chat.completions.create(
        model = "mistralai/Mistral-7B-Instruct-v0.3",
        messages = messages_send,
        temperature = 0.01,
        top_p = 0.1,
        max_tokens = 2048
    )
    
    return response.choices[0].message.content.strip()

def retrieve_question():
    sampled_question = df.sample(n=1)
    question = sampled_question['question'].values[0]
    
    # Check if we have a stored ground truth answer
    ground_truth = sampled_question['correct_answer'].values[0]
    if pd.isna(ground_truth) or not str(ground_truth).strip():
        # Generate ground truth answer if not available
        ground_truth = get_ground_truth_answer(question)
        
        # Save back to dataframe
        row_index = sampled_question.index[0]
        df.at[row_index, 'correct_answer'] = ground_truth
        try:
            df.to_csv("Conceptual_questions_final.csv", index=False, encoding="utf-8")
        except:
            pass  # Silently fail if we can't save back to CSV
    
    return question, ground_truth

def evaluate_conceptual_answer(question, user_answer, ground_truth):
    system_prompt = """
## Role:
You are an expert evaluator in data science and machine learning. You assess conceptual understanding critically.

## Task:
You will receive:
- A **conceptual question**
- A **user's answer**
- A **ground truth explanation** (reference answer)

You must evaluate how well the **user's answer matches the reference explanation**, not just if it sounds reasonable.

## Evaluation Criteria:

1. **Accuracy (1–5):**
   - 5: Fully accurate — matches the ground truth in logic, terminology, and intent.
   - 4: Mostly accurate — slight issues but no core misunderstandings.
   - 3: Partially correct — some alignment but includes vague or misleading points.
   - 2: Largely incorrect — key misunderstandings or incorrect definitions.
   - 1: Fundamentally flawed — shows a core conceptual error, or contradicts the ground truth.

2. **Clarity (1–5):**
   - 5: Very clear, organized, and well-phrased.
   - 4: Mostly clear, with minor awkwardness.
   - 3: Understandable but imprecise or lacking structure.
   - 2: Hard to follow or poorly expressed.
   - 1: Incoherent or confusing.

3. **Completeness (1–5):**
   - 5: Thorough — covers all key elements from the ground truth.
   - 4: Nearly complete — minor detail missing.
   - 3: Covers the main idea but skips comparisons or examples.
   - 2: Major points or contrasts missing.
   - 1: Superficial or extremely brief.

> ⚠️ Be strict on **Accuracy**: If the user answer contradicts or confuses basic definitions, it must get 1–2.

---

## Output Format (do NOT skip any section):

---
**Question:** {question}

**User Answer:**
"{user_answer}"

**Feedback:**
**Scores:**
- Accuracy: X/5
- Clarity: X/5
- Completeness: X/5

**Strengths:**
- Bullet list of technically correct or partially useful aspects (if any),even if minor.

**Weaknesses & Areas for Improvement:**
- Bullet list of incorrect logic, flawed comparisons, omissions, or confusion.
- Highlight any major contradictions with the ground truth.

**Suggested Improvement:**
- Rewrite or expand the answer accurately.
- Clarify key definitions or use correct terminology.
- Provide examples or diagnostic techniques if the question requires it.

**Final Score:** X/5
---
"""

    messages_send = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"###Question:\n{question}\n\n###User Answer:\n{user_answer}\n\n###Ground Truth:\n{ground_truth}"}
    ]
    
    response = client.chat.completions.create(
        model = "mistralai/Mistral-7B-Instruct-v0.3",
        messages = messages_send,
        temperature = 0.01,
        top_p = 0.1,
        max_tokens = 2048
    )
    
    return response.choices[0].message.content.strip()

def off_topic_response():
    st.markdown("""
    <div class="error-message">
        <h4>Valid Answer Required</h4>
        <p>Your answer should be a thoughtful explanation in English. Please provide a proper answer to the conceptual question.</p>
    </div>
    """, unsafe_allow_html=True)

def init_conceptual_interview():
    if "conceptual" not in st.session_state:
        # Initialize new interview
        st.session_state.conceptual = {
            "count": 0,
            "question": "",
            "ground_truth": "",
            "results": [],
            "conversation_started": False
        }
        # Get first question
        question, ground_truth = retrieve_question()
        st.session_state.conceptual.update({
            "question": question,
            "ground_truth": ground_truth,
            "conversation_started": True
        })

def render_conceptual_interview():
    # Initialize interview if needed
    if "conceptual" not in st.session_state:
        init_conceptual_interview()
    
    st.markdown(f"""
    <div class="interview-card">
        <h2 style="text-align: center;">Technical Conceptual Interview</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="interview-card">
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="question-header">Question {st.session_state.conceptual['count']+1}/3</div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Question:** {st.session_state.conceptual['question']}")
    
    user_answer = st.text_area(
        "Your Answer:",
        height=250,
        key="answer_area",
        help="Write your explanation here",
        placeholder="Type your conceptual explanation here..."
    )
    
    col1, col2 = st.columns([4, 1])
    with col2:
        submit_button = st.button("Submit Answer", key="submit_answer")
        
    if submit_button:
        if user_answer.strip():
            # Validate the answer format
            if check_conceptual_answer(user_answer):
                with st.spinner("Evaluating your answer..."):
                    evaluation = evaluate_conceptual_answer(
                        st.session_state.conceptual['question'],
                        user_answer,
                        st.session_state.conceptual['ground_truth']
                    )
                    
                    st.session_state.conceptual['results'].append({
                        "question": st.session_state.conceptual['question'],
                        "answer": user_answer,
                        "evaluation": evaluation
                    })
                    
                    st.session_state.conceptual['count'] += 1
                    
                    if st.session_state.conceptual['count'] < 3:
                        question, ground_truth = retrieve_question()
                        st.session_state.conceptual.update({
                            "question": question,
                            "ground_truth": ground_truth
                        })
                        st.success("Answer submitted successfully! Moving to next question...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        # Interview complete, evaluate and save
                        interview_data = {
                            "results": st.session_state.conceptual['results']
                        }
                        
                        # Save to database
                        conceptual_id = save_conceptual_results(st.session_state.user, interview_data)
                        
                        # Store ID for later combining with coding interview
                        st.session_state.conceptual_id = conceptual_id
                        
                        # Store for results page
                        if 'interview_complete' not in st.session_state:
                            st.session_state.interview_complete = {}
                        
                        st.session_state.interview_complete["conceptual"] = interview_data
                        
                        # Move to coding interview (third part)
                        st.session_state.interview_type = "coding"
                        st.rerun()
            else:
                off_topic_response()
        else:
            st.warning("Please enter your answer before submitting.")
    
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)
