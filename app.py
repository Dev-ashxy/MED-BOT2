import streamlit as st
from transformers import pipeline
import re
#import features  
st.set_page_config(page_title="Doc.AI", layout="wide")
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
    "stomach pain": ["Gastritis", "Food Poisoning", "Appendicitis", "Acid Reflux", "IBS", "Gallstones", "Peptic Ulcer"],
    "diarrhea": ["Food Poisoning", "IBS", "Cholera", "Gastroenteritis", "Crohn’s Disease"],
    "vomiting": ["Food Poisoning", "Gastroenteritis", "Migraine", "Motion Sickness"],
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
    "numbness or tingling": ["Neuropathy", "Multiple Sclerosis", "Stroke", "Diabetes"],
    "bleeding gums": ["Vitamin C Deficiency", "Gingivitis", "Leukemia", "Poor Dental Hygiene"],
    "palpitations": ["Anxiety", "Hyperthyroidism", "Atrial Fibrillation", "Heart Disease"],
    "constipation": ["Irritable Bowel Syndrome (IBS)", "Hypothyroidism", "Dehydration", "Hemorrhoids"],
    "acid reflux": ["GERD", "Gastritis", "Peptic Ulcer", "Hiatal Hernia"],
    "bloating": ["Lactose Intolerance", "Irritable Bowel Syndrome (IBS)", "Celiac Disease", "Gastroparesis"],
    "dark urine": ["Liver Disease", "Dehydration", "Jaundice", "Hepatitis"],
    "yellow skin or eyes": ["Jaundice", "Hepatitis", "Liver Disease", "Gallstones"],
    "difficulty swallowing": ["Esophageal Cancer", "Stroke", "Acid Reflux", "Throat Infection"],
    "sensitivity to cold": ["Hypothyroidism", "Raynaud’s Disease", "Anemia"],
    "sensitivity to heat": ["Hyperthyroidism", "Multiple Sclerosis", "Dehydration"],
    "muscle weakness": ["Myasthenia Gravis", "Multiple Sclerosis", "ALS (Lou Gehrig's Disease)", "Guillain-Barré Syndrome"],
    "seizures": ["Epilepsy", "Brain Tumor", "Stroke", "Meningitis", "Low Blood Sugar"],
    "hallucinations": ["Schizophrenia", "Delirium", "Brain Tumor", "Substance Abuse"],
    "mood swings": ["Bipolar Disorder", "Depression", "Anxiety", "Borderline Personality Disorder"],
    "depression": ["Major Depressive Disorder", "Bipolar Disorder", "Hypothyroidism", "Chronic Fatigue Syndrome"],
    "anxiety": ["Generalized Anxiety Disorder", "Panic Disorder", "PTSD", "Hyperthyroidism"],
    "bruising easily": ["Vitamin K Deficiency", "Leukemia", "Liver Disease", "Bleeding Disorders"],
    "hair loss": ["Alopecia Areata", "Hypothyroidism", "Nutrient Deficiency", "Stress"],
    "delayed wound healing": ["Diabetes", "Vitamin C Deficiency", "Poor Circulation", "Infection"],
    "hot flashes": ["Menopause", "Hyperthyroidism", "Anxiety"],
    "low sex drive": ["Low Testosterone", "Depression", "Medications", "Hypothyroidism"],
    "painful periods": ["Endometriosis", "PCOS", "Fibroids", "Pelvic Inflammatory Disease"],
    "blood in urine": ["Kidney Stones", "Bladder Infection", "Prostate Cancer", "Urinary Tract Infection"],
    "difficulty breathing at night": ["Sleep Apnea", "Congestive Heart Failure", "Asthma"],
    "ringing in ears": ["Tinnitus", "Ear Infection", "Meniere’s Disease", "Hearing Loss"],
    "loss of balance": ["Vertigo", "Multiple Sclerosis", "Parkinson’s Disease", "Brain Tumor"],
    "chronic pain": ["Fibromyalgia", "Arthritis", "Neuropathy", "Multiple Sclerosis"],
    "cold hands and feet": ["Raynaud’s Disease", "Hypothyroidism", "Poor Circulation", "Diabetes"],
    "low blood pressure": ["Dehydration", "Anemia", "Adrenal Insufficiency", "Heart Failure"],
    "high blood pressure": ["Hypertension", "Kidney Disease", "Hyperthyroidism", "Sleep Apnea"],
    "difficulty sleeping": ["Insomnia", "Anxiety", "Depression", "Sleep Apnea"],
    "dry skin": ["Eczema", "Hypothyroidism", "Dehydration", "Vitamin A Deficiency"],
    "pain in penis": ["Erectile dysfunction", "Prostate cancer","Phimosis"]
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


if "page" not in st.session_state:
    st.session_state.page = "chatbot"

def chatbot_page():
    st.markdown("<div class='title'>🩺 Doc.AI - Your Medical Assistant</div>", unsafe_allow_html=True)

 
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "submitted_text" not in st.session_state:
        st.session_state.submitted_text = ""

    def submit_text():
        st.session_state.submitted_text = st.session_state.user_input

    # User input field with Enter key submission
    user_input = st.text_input("Type Hello to start chatting with Doc.AI:", key="user_input", on_change=submit_text)

    if (st.session_state.submitted_text or st.button("Send")) and st.session_state.submitted_text:
        with st.spinner("Thinking... 🤖"):
            response = bot_response(st.session_state.submitted_text)

        st.session_state.chat_history.append(("You", st.session_state.submitted_text))
        st.session_state.chat_history.append(("Doc.AI", response))

        st.session_state.submitted_text = ""

 
    st.markdown("<div class='chat-container chat-box'>", unsafe_allow_html=True)
    for sender, message in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"<div class='user-message'>{message}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-message'>{message}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # # Next Button to navigate to features page
    # if st.button(""):
    #     st.session_state.page = "features"
    #     st.rerun()

    st.write("---")
    st.write("🤖 Powered by Doc.AI")

# Page routing
if st.session_state.page == "chatbot":
    chatbot_page()
elif st.session_state.page == "features":
    features.show_features_page()

elif st.session_state.page == "doctors":
    features.show_doctors_page()
