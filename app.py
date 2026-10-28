"""
🌿 Prakriti Determine — Ayurvedic Body Type Chatbot  (Big Data edition)

Streamlit UI  +  PySpark MLlib model  +  HDFS storage
  * model is loaded from HDFS  (trained by train_model.py)
  * predictions are computed with Spark ML
  * every completed quiz is appended to HDFS (Parquet) for Spark SQL analytics
"""

import logging
import uuid

import streamlit as st

import analytics
import config
import predictor
import train_model
from content import *  # noqa: F401,F403  (PRAKRITI_INFO, DIET_SUGGESTIONS, QUESTIONS, chatbot_respond…)
from spark_utils import ensure_dataset, get_spark

st.set_page_config(
    page_title="Prakriti Determine",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Spark + model bootstrap (runs once per server process) ───────────────────
@st.cache_resource(show_spinner="⚡ Starting Spark and loading the model from HDFS…")
def get_runtime():
    spark = get_spark("AyurBot-App")
    if not predictor.model_exists(spark):
        # First run: make sure data is in HDFS, then train and store the model there
        ensure_dataset(spark)
        train_model.train_and_save(spark, run_cv=False)
    return spark, predictor.load_model(spark)


try:
    SPARK, MODEL = get_runtime()
except Exception as exc:
    st.error(
        "Could not start Spark / reach HDFS.\n\n"
        f"**HDFS_URI** = `{config.HDFS_URI}`  ·  **base dir** = `{config.HDFS_BASE_DIR}`\n\n"
        f"`{type(exc).__name__}: {str(exc)[:400]}`\n\n"
        "Check that the NameNode is running (`hdfs dfsadmin -report`) and that "
        "`HDFS_URI` is correct."
    )
    st.stop()



# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    .main { background: linear-gradient(135deg, #f5f0eb 0%, #e8f5e9 100%); }
    
    .chat-bubble-bot {
        background: rgba(91, 158, 110, 0.12);
        color: inherit;
        border-radius: 18px 18px 18px 4px;
        padding: 14px 18px;
        margin: 8px 0 8px 0;
        max-width: 85%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        border-left: 4px solid #5B9E6E;
        font-size: 15px;
        line-height: 1.6;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0 8px auto;
        max-width: 80%;
        text-align: right;
        box-shadow: 0 2px 8px rgba(102,126,234,0.35);
        font-size: 15px;
    }
    .chat-container { max-width: 700px; margin: 0 auto; }
    
    .prakriti-card {
        border-radius: 20px;
        padding: 28px;
        margin: 16px 0;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    .prakriti-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 8px 0;
    }
    .section-card {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.10);
    }
    .food-item {
        padding: 4px 0;
        font-size: 15px;
    }
    .progress-text {
        font-size: 13px;
        color: #666;
        text-align: center;
        margin-top: 4px;
    }
    .stButton > button {
        border-radius: 12px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    .header-banner {
        background: linear-gradient(135deg, #2D5016 0%, #5B9E6E 50%, #A8D5B5 100%);
        border-radius: 20px;
        padding: 30px 24px;
        text-align: center;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(43,80,22,0.25);
    }
    .header-banner h1 { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .header-banner p { font-size: 1rem; opacity: 0.9; margin: 8px 0 0 0; }
</style>
""", unsafe_allow_html=True)

# ─── Session state init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": [],          # list of {"role": "bot"|"user", "text": str}
        "q_index": 0,            # current question index
        "answers": [],           # collected answers (0/1/2 per question)
        "phase": "welcome",      # welcome | quiz | result
        "prediction": None,
        "probabilities": None,
        "show_diet": False,
        "session_id": uuid.uuid4().hex,   # identifies this quiz run in HDFS
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def add_message(role, text):
    st.session_state.messages.append({"role": role, "text": text})

def reset_app():
    for k in ["messages", "q_index", "answers", "phase", "prediction", "probabilities", "show_diet", "session_id"]:
        del st.session_state[k]
    init_state()

def predict_prakriti(answers):
    """Run the Spark ML pipeline (loaded from HDFS) on the 15 answers."""
    return predictor.predict(SPARK, MODEL, answers)


@st.cache_data(ttl=30, show_spinner=False)
def population_summary():
    """Spark SQL over all stored quiz responses in HDFS (cached for 30 s)."""
    return analytics.population_summary(SPARK)


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <h1>🌿 Prakriti Determine</h1>
    <p>Discover your Ayurvedic body type through a guided conversation</p>
</div>
""", unsafe_allow_html=True)

# ─── Welcome phase ────────────────────────────────────────────────────────────
if st.session_state.phase == "welcome":
    if not st.session_state.messages:
        add_message("bot", (
            "Namaste! 🙏 Welcome to **Prakriti Determine**.\n\n"
            "In Ayurveda, *Prakriti* is your unique mind-body constitution — "
            "a blend of three life forces called **Doshas**: "
            "🌬️ **Vata** (Air & Space), 🔥 **Pitta** (Fire & Water), and 🌊 **Kapha** (Earth & Water).\n\n"
            "I'll ask you **15 simple questions** about your body, mind, and habits. "
            "Answer honestly based on your *natural tendencies*, not how you feel today.\n\n"
            "At the end, our AI model will predict your Prakriti and suggest a personalised diet! 🌱"
        ))

    # Display messages
    for msg in st.session_state.messages:
        cls = "chat-bubble-bot" if msg["role"] == "bot" else "chat-bubble-user"
        st.markdown(f'<div class="{cls}">{msg["text"]}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start My Prakriti Journey", use_container_width=True):
            add_message("user", "Let's begin!")
            st.session_state.phase = "quiz"
            st.rerun()

# ─── Quiz phase ───────────────────────────────────────────────────────────────
elif st.session_state.phase == "quiz":
    # Show previous messages
    for msg in st.session_state.messages:
        cls = "chat-bubble-bot" if msg["role"] == "bot" else "chat-bubble-user"
        st.markdown(f'<div class="{cls}">{msg["text"]}</div>', unsafe_allow_html=True)

    q_idx = st.session_state.q_index
    total = len(QUESTIONS)

    if q_idx < total:
        q = QUESTIONS[q_idx]

        # Progress bar
        progress = q_idx / total
        st.progress(progress)
        st.markdown(f'<p class="progress-text">Question {q_idx + 1} of {total}</p>', unsafe_allow_html=True)

        # Show current question as bot bubble
        st.markdown(f'<div class="chat-bubble-bot">❓ {q["text"]}</div>', unsafe_allow_html=True)

        # Option buttons
        for i, option in enumerate(q["options"]):
            if st.button(option, key=f"opt_{q_idx}_{i}", use_container_width=True):
                # Save answer
                add_message("bot", f"❓ {q['text']}")
                add_message("user", option)
                st.session_state.answers.append(i)
                st.session_state.q_index += 1

                if st.session_state.q_index >= total:
                    # All answered — predict
                    prakriti, proba = predict_prakriti(st.session_state.answers)
                    st.session_state.prediction = prakriti
                    st.session_state.probabilities = proba
                    try:  # persist the submission to HDFS for analytics
                        predictor.log_response(SPARK, st.session_state.session_id,
                                               st.session_state.answers, prakriti, proba)
                    except Exception as exc:  # never block the user's result
                        logging.getLogger("ayurbot").warning("HDFS logging failed: %s", exc)
                    add_message("bot", (
                        f"✨ Thank you for completing all the questions! "
                        f"Our AI model has analysed your responses…\n\n"
                        f"🔮 Calculating your Prakriti…"
                    ))
                    st.session_state.phase = "result"

                st.rerun()

# ─── Result phase ─────────────────────────────────────────────────────────────
elif st.session_state.phase == "result":
    prakriti = st.session_state.prediction
    proba = st.session_state.probabilities
    info = PRAKRITI_INFO[prakriti]
    diet = DIET_SUGGESTIONS[prakriti]

    # ── Prakriti Result Card ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="prakriti-card" style="background: linear-gradient(135deg, {info['color']}22 0%, {info['color']}44 100%); border: 2px solid {info['color']};">
        <div style="font-size:4rem">{info['emoji']}</div>
        <div class="prakriti-title" style="color:{info['color']};">
            Your Prakriti is {prakriti}
        </div>
        <div style="opacity:0.75; font-size:0.95rem; margin:8px 0;">
            {info['element']} Constitution
        </div>
        <div style="opacity:0.8; font-size:0.9rem; margin-top:12px; font-style:italic;">
            "{info['description']}"
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Dosha Percentages ─────────────────────────────────────────────────────
    st.markdown("### 📊 Your Dosha Breakdown")
    cols = st.columns(3)
    dosha_colors = {"Vata": "#8B7FD4", "Pitta": "#E07B54", "Kapha": "#5B9E6E"}
    dosha_emojis = {"Vata": "🌬️", "Pitta": "🔥", "Kapha": "🌊"}
    for i, (label, p) in enumerate(zip(PRAKRITI_LABELS, proba)):
        with cols[i]:
            pct = int(p * 100)
            c = dosha_colors[label]
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.12);
                        border-radius:14px; padding:16px; text-align:center;
                        box-shadow:0 4px 12px rgba(0,0,0,0.12); border-top:4px solid {c}">
                <div style="font-size:1.8rem">{dosha_emojis[label]}</div>
                <div style="font-weight:600; color:{c}; font-size:1.1rem">{label}</div>
                <div style="font-size:2rem; font-weight:700;">{pct}%</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(p)

    # ── Population analytics (Spark SQL over HDFS) ───────────────────────────
    with st.expander("🌍 How do you compare with other users? (Spark on HDFS)"):
        try:
            summary = population_summary()
        except Exception:
            summary = None
        if not summary:
            st.caption("No stored responses could be read from HDFS yet.")
        else:
            total = summary["total"]
            st.caption(f"Computed by Spark from {total:,} quiz submissions stored in HDFS.")
            pc = st.columns(3)
            for i, label in enumerate(PRAKRITI_LABELS):
                cnt = summary["distribution"].get(label, 0)
                with pc[i]:
                    st.metric(label, f"{cnt / total:.0%}", f"{cnt:,} users", delta_color="off")

    # ── Key Traits ────────────────────────────────────────────────────────────
    with st.expander("🌟 Your Key Traits & Qualities", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**✨ Traits:** {info['traits']}")
        with col2:
            st.markdown(f"**⚡ Qualities:** {info['qualities']}")

    st.markdown("---")

    # ── Diet Suggestions ──────────────────────────────────────────────────────
    st.markdown(f"## 🥗 Diet Recommendations for {prakriti} Prakriti")
    st.markdown(f"""
    <div class="section-card" style="border-left:4px solid {info['color']};">
        <strong>🎯 Core Principle:</strong> {diet['principle']}
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### ✅ Foods to Favour")
        favour_html = "".join(f'<div class="food-item">{item}</div>' for item in diet["favor"])
        st.markdown(f'<div class="section-card">{favour_html}</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown("### ❌ Foods to Avoid")
        avoid_html = "".join(f'<div class="food-item">{item}</div>' for item in diet["avoid"])
        st.markdown(f'<div class="section-card">{avoid_html}</div>', unsafe_allow_html=True)

    st.markdown("### 💡 Meal Tips")
    tips_html = "".join(f'<div class="food-item">{tip}</div>' for tip in diet["meal_tips"])
    st.markdown(f'<div class="section-card">{tips_html}</div>', unsafe_allow_html=True)

    st.markdown("### 🌿 Recommended Herbs & Supplements")
    st.markdown(f"""
    <div class="section-card" style="border-left:4px solid #5B9E6E;">
        <strong>🌱 {diet['herbs']}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Chatbot Follow-up ─────────────────────────────────────────────────────
    st.markdown("### 💬 Ask the Chatbot")
    st.markdown(f"""
    <div class="chat-bubble-bot">
        Wonderful! 🌿 You have discovered your <strong>{prakriti}</strong> Prakriti!<br><br>
        Feel free to ask me anything about your Prakriti, your diet recommendations, 
        Ayurvedic lifestyle tips, or anything else you'd like to know. I'm here to help! 🙏
    </div>
    """, unsafe_allow_html=True)

    # Chat history for Q&A
    if "chat_qa" not in st.session_state:
        st.session_state.chat_qa = []

    for m in st.session_state.chat_qa:
        cls = "chat-bubble-bot" if m["role"] == "bot" else "chat-bubble-user"
        st.markdown(f'<div class="{cls}">{m["text"]}</div>', unsafe_allow_html=True)

    user_q = st.chat_input("Ask about your Prakriti, diet, lifestyle…")
    if user_q:
        st.session_state.chat_qa.append({"role": "user", "text": user_q})
        # Simple rule-based chatbot for Prakriti follow-up
        answer = chatbot_respond(user_q, prakriti, info, diet)
        st.session_state.chat_qa.append({"role": "bot", "text": answer})
        st.rerun()

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Retake the Quiz", use_container_width=True):
            reset_app()
            st.rerun()


