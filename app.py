import streamlit as st
from transformers import pipeline
import re

# Set page config
st.set_page_config(page_title="Doc.AI", layout="wide")

# Load Hugging Face Medical Model (BioGPT)
@st.cache_resource
def load_model():
    try:
        model = pipeline("text-generation", model="microsoft/BioGPT-Large")
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

SYMPTOM_KNOWLEDGE_BASE = {
    "cold": ["Common Cold", "Influenza", "Allergic Rhinitis", "Sinusitis"],
    "fever": ["Viral Fever", "Flu", "Dengue", "Malaria", "Typhoid", "COVID-19", "Heat Stroke"],
    "cough": ["Bronchitis", "Pneumonia", "COVID-19", "Tuberculosis", "Asthma", "Whooping Cough"],
    "headache": ["Migraine", "Tension Headache", "Sinus Infection", "Cluster Headache", "Meningitis", "Hypertension"],
    "stomach pain": ["Gastritis", "Food Poisoning", "Appendicitis", "Acid Reflux", "Irritable Bowel Syndrome (IBS)", "Gallstones", "Peptic Ulcer"],
    "diarrhea": ["Food Poisoning", "Irritable Bowel Syndrome (IBS)", "Cholera", "Gastroenteritis", "Crohn’s Disease"],
    "vomiting": ["Food Poisoning", "Gastroenteritis", "Pregnancy (Morning Sickness)", "Migraine", "Motion Sickness"],
    "chest pain": ["Heart Attack", "Angina", "GERD (Acid Reflux)", "Pulmonary Embolism", "Pneumonia", "Panic Attack"],
    "shortness of breath": ["Asthma", "COPD (Chronic Obstructive Pulmonary Disease)", "Heart Failure", "Pneumonia", "COVID-19", "Anemia"],
    "fatigue": ["Anemia", "Hypothyroidism", "Chronic Fatigue Syndrome", "Diabetes", "Depression"],
    "dizziness": ["Low Blood Pressure", "Anemia", "Vertigo", "Dehydration", "Hypoglycemia"],
    "sore throat": ["Strep Throat", "Tonsillitis", "Common Cold", "Influenza", "Mononucleosis"],
    "joint pain": ["Arthritis", "Lupus", "Gout", "Rheumatoid Arthritis", "Osteoarthritis"],
    "skin rash": ["Allergic Reaction", "Eczema", "Psoriasis", "Chickenpox", "Measles"],
    "back pain": ["Muscle Strain", "Herniated Disc", "Sciatica", "Kidney Stones"],
    "ear pain": ["Ear Infection", "Swimmer’s Ear", "Sinus Infection", "TMJ Disorder"],
    "eye pain": ["Conjunctivitis", "Glaucoma", "Corneal Abrasion", "Sinusitis"],
    "frequent urination": ["Diabetes", "Urinary Tract Infection (UTI)", "Prostate Enlargement", "Overactive Bladder"],
    "burning urination": ["Urinary Tract Infection (UTI)", "Kidney Stones", "Sexually Transmitted Infection (STI)"],
    "swelling in legs": ["Heart Failure", "Kidney Disease", "Lymphedema", "Deep Vein Thrombosis (DVT)"],
    "weight loss": ["Diabetes", "Hyperthyroidism", "Cancer", "Tuberculosis"],
    "weight gain": ["Hypothyroidism", "Cushing’s Syndrome", "PCOS (Polycystic Ovary Syndrome)"],
    "memory loss": ["Alzheimer’s Disease", "Dementia", "Vitamin B12 Deficiency", "Stroke"],
    "night sweats": ["Tuberculosis", "Lymphoma", "Menopause", "Hyperthyroidism"],
    
}

def bot_response(user_input):
    if model is None:
        return "Error: Model failed to load. Please try again later."
    if len(st.session_state.chat_history) == 0:
        return "Hello! I am Doc.AI. Tell me your symptoms, and I'll suggest possible conditions."

    for symptom, conditions in SYMPTOM_KNOWLEDGE_BASE.items():
        if symptom in user_input.lower():
            return f"You may have: {', '.join(conditions)}."

    try:
        prompt = f"A patient reports the following symptoms: {user_input}. Based on medical knowledge, suggest possible conditions without unnecessary text."

        response = model(prompt, max_length=100, do_sample=True, num_return_sequences=1)
        generated_text = response[0]['generated_text']
        cleaned_text = re.sub(r"<.*?>", "", generated_text)  
        cleaned_text = re.sub(r"[\[\]{}]", "", cleaned_text)  
        cleaned_text = cleaned_text.replace("▃", "").strip()  

        if "diabetes" in cleaned_text.lower() and "cold" not in cleaned_text.lower():
            return "That doesn't seem right. If you have a cold, you may have Influenza or a Common Cold."

        return cleaned_text
    except Exception as e:
        return f"Sorry, I couldn't process your request. Error: {e}"

st.markdown("""
    <style>
        .chat-container {
            background-color: #e5f7e9;
            padding: 20px;
            border-radius: 15px;
            max-width: 600px;
            margin: auto;
        }
        .user-message {
            background-color: #dcf8c6;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: right;
            width: fit-content;
            max-width: 70%;
            margin-left: auto;
            color: black;
        }
        .bot-message {
            background-color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: left;
            width: fit-content;
            max-width: 70%;
            color: black;
        }
        .chat-box {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .title {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: #2e7d32;
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='title'>🩺 Doc.AI - Your Medical Assistant</div>", unsafe_allow_html=True)

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "submitted_text" not in st.session_state:
    st.session_state.submitted_text = ""

# Function to update submitted text when Enter is pressed
def submit_text():
    st.session_state.submitted_text = st.session_state.user_input

# User input field with Enter key submission
user_input = st.text_input("Type your message:", key="user_input", on_change=submit_text)

# Check if Enter was pressed or "Send" button was clicked
if (st.session_state.submitted_text or st.button("Send")) and st.session_state.submitted_text:
    with st.spinner("Thinking... 🤖"):
        response = bot_response(st.session_state.submitted_text)

    st.session_state.chat_history.append(("You", st.session_state.submitted_text))
    st.session_state.chat_history.append(("Doc.AI", response))

    # Clear input field safely without modifying `user_input`
    st.session_state.submitted_text = ""

# Display chat history
st.markdown("<div class='chat-container chat-box'>", unsafe_allow_html=True)
for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"<div class='user-message'>{message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-message'>{message}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.write("---")
st.write("🤖 Powered by Doc.AI")
