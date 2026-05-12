import asyncio
import streamlit as st
from agent import stream_response

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BBAU Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & base ──────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    min-height: 100vh;
}

/* ── Hide Streamlit chrome ─────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ───────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #1a1a2e 100%);
    border-right: 1px solid rgba(99, 102, 241, 0.2);
}

[data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem !important; }

.sidebar-logo {
    text-align: center;
    padding: 1.5rem 0 2rem;
    border-bottom: 1px solid rgba(99,102,241,0.2);
    margin-bottom: 2rem;
}

.sidebar-logo .uni-name {
    font-size: 1.1rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-top: 0.5rem;
    line-height: 1.3;
}

.sidebar-logo .uni-sub {
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 0.25rem;
    letter-spacing: 0.05em;
}

.section-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: #475569;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}

.tool-card {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 10px;
    padding: 0.65rem 0.9rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.tool-card .tool-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22c55e;
    flex-shrink: 0;
    box-shadow: 0 0 6px #22c55e;
}

.tool-card .tool-name {
    font-size: 0.78rem;
    font-weight: 500;
    color: #cbd5e1;
}

.tool-card .tool-desc {
    font-size: 0.68rem;
    color: #64748b;
    margin-top: 1px;
}

/* ── Chat area wrapper ─────────────────────────────────────────────── */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 0;
}

/* ── Header bar ────────────────────────────────────────────────────── */
.chat-header {
    background: rgba(13,13,26,0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(99,102,241,0.2);
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    position: sticky;
    top: 0;
    z-index: 100;
}

.chat-header .header-title {
    font-size: 1.15rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.chat-header .header-sub {
    font-size: 0.75rem;
    color: #64748b;
}

.status-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 8px #22c55e;
    flex-shrink: 0;
}

/* ── Messages container ────────────────────────────────────────────── */
.messages-area {
    flex: 1;
    overflow-y: auto;
    padding: 2rem 3rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* ── Message bubbles ───────────────────────────────────────────────── */
.msg-row {
    display: flex;
    align-items: flex-end;
    gap: 0.75rem;
    animation: fadeUp 0.25s ease;
}

.msg-row.user { flex-direction: row-reverse; }
.msg-row.bot  { flex-direction: row; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}

.avatar.user { background: linear-gradient(135deg,#6366f1,#8b5cf6); }
.avatar.bot  { background: linear-gradient(135deg,#0ea5e9,#6366f1); }

.bubble {
    max-width: 68%;
    padding: 0.85rem 1.1rem;
    border-radius: 18px;
    font-size: 0.9rem;
    line-height: 1.65;
    word-break: break-word;
}

.bubble.user {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    border-bottom-right-radius: 4px;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35);
}

.bubble.bot {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    color: #e2e8f0;
    border-bottom-left-radius: 4px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* ── Welcome card ──────────────────────────────────────────────────── */
.welcome-card {
    text-align: center;
    padding: 3rem 2rem;
    animation: fadeUp 0.4s ease;
}

.welcome-card .wc-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
}

.welcome-card h2 {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg,#818cf8,#c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.welcome-card p {
    color: #64748b;
    font-size: 0.88rem;
    margin-bottom: 2rem;
}

.chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
}

.chip {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 0.4rem 0.9rem;
    font-size: 0.78rem;
    color: #a5b4fc;
    cursor: default;
}

/* ── Input area ────────────────────────────────────────────────────── */
[data-testid="stChatInput"] {
    background: rgba(13,13,26,0.9) !important;
    border-top: 1px solid rgba(99,102,241,0.2) !important;
    padding: 1rem 2rem !important;
}

[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(99,102,241,0.7) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* ── Scrollbar ─────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 3px; }

/* ── Sidebar clear button ──────────────────────────────────────────── */
.stButton > button {
    width: 100%;
    background: rgba(239,68,68,0.12) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    color: #fca5a5 !important;
    border-radius: 10px !important;
    font-size: 0.8rem !important;
    padding: 0.5rem !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: rgba(239,68,68,0.22) !important;
    border-color: rgba(239,68,68,0.5) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:2.5rem">🎓</div>
        <div class="uni-name">Babasaheb Bhimrao Ambedkar University</div>
        <div class="uni-sub">LUCKNOW · CENTRAL UNIVERSITY</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Active Tools</div>', unsafe_allow_html=True)

    tools_info = [
        ("🗄️", "Database Schema", "Inspects table structures"),
        ("👩‍🏫", "Faculty Query", "Name, dept, designation search"),
        ("🌐", "Web Search", "Tavily — live university info"),
    ]
    for icon, name, desc in tools_info:
        st.markdown(f"""
        <div class="tool-card">
            <div class="tool-dot"></div>
            <div>
                <div class="tool-name">{icon} {name}</div>
                <div class="tool-desc">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Session</div>', unsafe_allow_html=True)

    if st.button("🗑️  Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.65rem;color:#334155;text-align:center">Powered by LangGraph · BBAU v1.0</div>',
        unsafe_allow_html=True,
    )


# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-header">
    <div class="status-dot"></div>
    <div>
        <div class="header-title">BBAU AI Assistant</div>
        <div class="header-sub">Ask me anything about the university</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Render chat history ─────────────────────────────────────────────────────────
def render_message(role: str, content: str):
    if role == "user":
        st.markdown(f"""
        <div class="msg-row user">
            <div class="avatar user">👤</div>
            <div class="bubble user">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row bot">
            <div class="avatar bot">🤖</div>
            <div class="bubble bot">{content}</div>
        </div>
        """, unsafe_allow_html=True)


if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <div class="wc-icon">🎓</div>
        <h2>Welcome to BBAU Assistant</h2>
        <p>Your AI-powered guide to Babasaheb Bhimrao Ambedkar University</p>
        <div class="chips">
            <span class="chip">👩‍🏫 Faculty in Computer Science</span>
            <span class="chip">🏫 All schools at BBAU</span>
            <span class="chip">📋 M.Tech programmes</span>
            <span class="chip">🏆 BBAU rankings</span>
            <span class="chip">📞 Vice Chancellor contact</span>
            <span class="chip">🎓 PhD admission process</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"])


# ── Handle new input ────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything about BBAU...", key="chat_input"):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)

    # Stream assistant response
    response_container = st.empty()
    full_response = ""

    # async def run_stream():
    #     nonlocal full_response
    #     async for chunk in stream_response(
    #         user_message=prompt,
    #         history=st.session_state.messages[:-1],  # exclude the message just added
    #     ):
    #         full_response += chunk
    #         response_container.markdown(f"""
    #         <div class="msg-row bot">
    #             <div class="avatar bot">🤖</div>
    #             <div class="bubble bot">{full_response}▌</div>
    #         </div>
    #         """, unsafe_allow_html=True)

    #     # Final render without cursor
    #     response_container.markdown(f"""
    #     <div class="msg-row bot">
    #         <div class="avatar bot">🤖</div>
    #         <div class="bubble bot">{full_response}</div>
    #     </div>
    #     """, unsafe_allow_html=True)

    # asyncio.run(run_stream())

    # # Persist to session state
    # st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    async def run_stream():
        # 1. Initialize the variable LOCALLY inside the function
        full_response = "" 
        
        async for chunk in stream_response(
            user_message=prompt,
            history=st.session_state.messages[:-1],  # exclude the message just added
        ):
            full_response += chunk
            response_container.markdown(f"""
            <div class="msg-row bot">
                <div class="avatar bot">🤖</div>
                <div class="bubble bot">{full_response}▌</div>
            </div>
            """, unsafe_allow_html=True)

        # Final render without cursor
        response_container.markdown(f"""
        <div class="msg-row bot">
            <div class="avatar bot">🤖</div>
            <div class="bubble bot">{full_response}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Return the completed string
        return full_response 

    # 3. Capture the returned value from asyncio.run()
    full_response = asyncio.run(run_stream())

    # Persist to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})