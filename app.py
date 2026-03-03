import streamlit as st
from fpdf import FPDF
import datetime
import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()


# ---------------- API ----------------

# 🔥 Set HF TOKEN in terminal
# Windows:
# setx HF_TOKEN "your_token_here"

HF_TOKEN = os.getenv("HF_TOKEN")

# Debug check
if not HF_TOKEN:
    st.error("HF TOKEN NOT FOUND")

client = InferenceClient(

    api_key=HF_TOKEN

)


# ---------------- PAGE ----------------

st.set_page_config(

    page_title="AI Study Buddy Pro",
    layout="wide"

)


# ---------------- SESSION ----------------

if "history" not in st.session_state:
    st.session_state.history=[]

if "count" not in st.session_state:
    st.session_state.count=0

if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]


# ---------------- STYLE ----------------

st.markdown("""

<style>

.main{
background-color:#0e1117;
color:white;
}

.block-container{
padding-top:2rem;
}

</style>

""",unsafe_allow_html=True)



# ---------------- HEADER ----------------

st.title("🚀 AI Study Buddy — Pro Tutor")

st.caption(

"AI Based Intelligent Study Assistant"

)



# ---------------- SIDEBAR ----------------

st.sidebar.title("📊 Dashboard")

st.sidebar.metric(

"Topics Generated",
st.session_state.count

)

st.sidebar.write("Recent Topics")

for h in st.session_state.history[-5:]:

    st.sidebar.write("⭐ "+h)



# ---------------- INPUT ----------------

col1,col2,col3=st.columns(3)

with col1:

    topic=st.text_input("Study Topic")

with col2:

    difficulty=st.selectbox(

        "Difficulty",

        ["Beginner","Intermediate","Advanced"]

    )

with col3:

    study_mode=st.selectbox(

        "Study Mode",

        [

        "Semester Exam",

        "Unit Test",

        "Last Day Revision"

        ]

    )



# ---------------- BACKUP AI ----------------

def backup_ai(topic):

    return f"""

### 🧠 AI Explanation

{topic.title()} introduces core academic concepts.

Focus on clarity and understanding.

---

### ⭐ Key Points

⭐ Fundamentals

⭐ Applications

⭐ Advantages

⭐ Challenges

---

### 🧩 MCQs

Which is purpose of {topic}?

A Problem Solving

Answer : A

---

### 📒 Flashcards

Definition :

{topic.title()} helps analyse systems.

---

### 🎯 AI Exam Strategy

Revise diagrams and previous papers.

"""



# ---------------- AI GENERATOR ----------------

def generate_ai(topic,difficulty,mode):

    try:

        prompt=f"""
You are an AI Tutor helping engineering students.

Topic : {topic}

Difficulty : {difficulty}

Study Mode : {mode}

Generate:

AI Explanation
Key Points
MCQs
Flashcards
Exam Strategy.

Make answer clear and exam friendly.
"""

        completion = client.chat.completions.create(

            model="meta-llama/Meta-Llama-3-8B-Instruct",

            messages=[

                {"role":"user","content":prompt}

            ],

            max_tokens=800

        )

        return completion.choices[0].message.content

    except Exception as e:

        st.error(f"AI Error : {e}")

        return backup_ai(topic)



# ---------------- CHAT ----------------

def tutor_chat(question):

    try:

        completion = client.chat.completions.create(

            model="meta-llama/Meta-Llama-3-8B-Instruct",

            messages=[

                {

                    "role":"user",

                    "content":f"""
You are AI Tutor.

Student doubt:

{question}

Explain simply with example.
"""

                }

            ],

            max_tokens=400

        )

        return completion.choices[0].message.content

    except:

        return "AI offline. Revise fundamentals."



# ---------------- PDF ----------------

def create_pdf(text):

    pdf=FPDF()

    pdf.add_page()

    pdf.set_font("Arial",size=12)

    replace_map={

        "🧠":"",
        "⭐":"-",
        "📒":"",
        "🎯":"",
        "🧩":"",
        "→":"->",
        "###":"",
        "---":"\n"

    }

    for k,v in replace_map.items():

        text=text.replace(k,v)

    text=text.encode("latin-1","ignore").decode("latin-1")

    pdf.multi_cell(0,10,text)

    file="StudyNotes.pdf"

    pdf.output(file)

    return file



# ---------------- GENERATE ----------------

if st.button("✨ Generate AI Study Content"):

    if topic:

        with st.spinner("🤖 AI Thinking..."):

            result=generate_ai(

                topic,

                difficulty,

                study_mode

            )

            st.success("Generated Successfully")

            st.markdown(result)

            st.session_state.count+=1

            st.session_state.history.append(topic)

            st.toast("AI Ready 🚀")

            st.info(

f"Generated : {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}"

            )

            pdf=create_pdf(result)

            with open(pdf,"rb") as f:

                st.download_button(

                "⬇ Download PDF",

                f,

                file_name="StudyNotes.pdf"

                )

    else:

        st.warning("Enter topic")



# ---------------- CHAT SECTION ----------------

st.divider()

st.subheader("🤖 AI Tutor Chat")

question=st.text_input("Ask Doubt")

if st.button("Ask Tutor"):

    if question:

        reply=tutor_chat(question)

        st.session_state.chat_history.append(

            ("You",question)

        )

        st.session_state.chat_history.append(

            ("Tutor",reply)

        )


# CHAT HISTORY DISPLAY

for role,msg in st.session_state.chat_history:

    if role=="You":

        st.write("🧑 :",msg)

    else:

        st.success("🤖 Tutor : "+msg)
