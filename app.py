import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BBAU Smart Chatbot",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── CSS Styling ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Main title */
.main-title {
    text-align: center;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
    padding-top: 20px;
}

.sub-title {
    text-align: center;
    color: rgba(255,255,255,0.5);
    font-size: 1rem;
    margin-bottom: 30px;
    font-weight: 400;
}

/* Chat container */
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 10px 0;
}

/* Message rows */
.chat-row {
    display: flex;
    align-items: flex-end;
    margin: 14px 0;
    gap: 10px;
    animation: fadeUp 0.3s ease;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

.user-row { flex-direction: row-reverse; }
.bot-row  { flex-direction: row; }

/* Avatars */
.avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.user-avatar {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
}

.bot-avatar {
    background: linear-gradient(135deg, #0ea5e9, #06b6d4);
}

/* Bubbles */
.bubble {
    max-width: 72%;
    padding: 14px 18px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.75;
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    word-wrap: break-word;
}

.user-bubble {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white;
    border-bottom-right-radius: 4px;
}

.bot-bubble {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.92);
    border-bottom-left-radius: 4px;
}

/* Typing indicator */
.typing-dots {
    display: flex;
    gap: 5px;
    padding: 14px 18px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    width: fit-content;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #60a5fa;
    animation: bounce 1.2s ease infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); }
    30%            { transform: translateY(-8px); }
}

/* Feature badges */
.feature-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 3px;
    background: rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.8);
    border: 1px solid rgba(255,255,255,0.15);
}

/* Hide Streamlit default elements */
#MainMenu, footer { visibility: hidden; }

/* Chat input box */
.stChatInput > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    color: white !important;
}

/* Sidebar text */
.sidebar-text {
    color: rgba(255,255,255,0.85);
    font-size: 14px;
    line-height: 1.8;
}

.sidebar-heading {
    color: white;
    font-weight: 700;
    font-size: 16px;
    margin: 15px 0 8px 0;
}

.info-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 12px 15px;
    margin: 8px 0;
    color: rgba(255,255,255,0.8);
    font-size: 13px;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:white; font-weight:800;'>🎓 BBAU Chatbot</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,0.5); font-size:13px;'>Powered by Gemini 1.5 Pro + LangChain</p>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("<div class='sidebar-heading'>✨ Kya pooch sakte ho?</div>", unsafe_allow_html=True)

    examples = [
        ("👨‍🏫", "Faculty Search", "Computer science ke professors kaun hain?"),
        ("📚", "Programmes", "BTech mein kitni seats hain?"),
        ("🏛️", "Administration", "Vice Chancellor ka email kya hai?"),
        ("🌐", "Live Search", "BBAU admission 2024 last date?"),
        ("🏫", "Schools", "BBAU mein kitne schools hain?"),
    ]

    for icon, title, example in examples:
        st.markdown(f"""
        <div class='info-card'>
            <b>{icon} {title}</b><br>
            <i style='color:rgba(255,255,255,0.55); font-size:12px;'>e.g. "{example}"</i>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        if "agent" in st.session_state:
            del st.session_state.agent
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='color:rgba(255,255,255,0.35); font-size:11px; text-align:center;'>
        BBAU, Lucknow | Central University<br>
        NAAC A++ | Est. 1996
    </div>
    """, unsafe_allow_html=True)

# ── Main UI ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='main-title'>🎓 BBAU Smart Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>AI-powered chatbot — Hindi, Hinglish & English mein baat karo</div>", unsafe_allow_html=True)

# ── Session State Init ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    with st.spinner("🤖 AI Agent initialize ho raha hai..."):
        from smart_agent import build_agent
        st.session_state.agent = build_agent()

# ── Welcome Message ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    welcome = (
        "Namaste! 🙏 Main BBAU ka Smart Assistant hoon.\n\n"
        "Aap mujhse Hindi, Hinglish ya English mein baat kar sakte hain!\n\n"
        "**Main help kar sakta hoon:**\n"
        "- 👨‍🏫 Faculty & Professors ki information\n"
        "- 📚 Programmes, Fees & Duration\n"
        "- 🏛️ Administration & Officials\n"
        "- 🏫 Schools & Departments\n"
        "- 🌐 Latest news & admissions (live web search)\n\n"
        "Kuch bhi poochho! 😊"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# ── Display Chat History ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-row user-row">
            <div class="bubble user-bubble">{msg["content"]}</div>
            <div class="avatar user-avatar">👤</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Convert markdown-style bold to HTML for rendering
        content = msg["content"].replace("**", "<b>", 1)
        import re as _re
        content = _re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg["content"])
        content = content.replace("\n", "<br>")
        st.markdown(f"""
        <div class="chat-row bot-row">
            <div class="avatar bot-avatar">🤖</div>
            <div class="bubble bot-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Chat Input ──────────────────────────────────────────────────────────────────
question = st.chat_input("Kuch bhi poochho... (Hindi ya English mein)")

if question:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})

    # Show user message immediately
    st.markdown(f"""
    <div class="chat-row user-row">
        <div class="bubble user-bubble">{question}</div>
        <div class="avatar user-avatar">👤</div>
    </div>
    """, unsafe_allow_html=True)

    # Show typing indicator
    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div class="chat-row bot-row">
        <div class="avatar bot-avatar">🤖</div>
        <div class="typing-dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Get AI response
    try:
        result = st.session_state.agent.invoke({"input": question})
        response = result.get("output", "Sorry, kuch problem aa gayi. Dobara try karo.")
    except Exception as e:
        response = f"⚠️ Error: {str(e)[:200]}\n\nPlease try again ya thoda alag tarike se poochho."

    # Clear typing indicator
    typing_placeholder.empty()

    # Add and display bot response
    st.session_state.messages.append({"role": "assistant", "content": response})

    import re as _re
    content = _re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
    content = content.replace("\n", "<br>")

    st.markdown(f"""
    <div class="chat-row bot-row">
        <div class="avatar bot-avatar">🤖</div>
        <div class="bubble bot-bubble">{content}</div>
    </div>
    """, unsafe_allow_html=True)