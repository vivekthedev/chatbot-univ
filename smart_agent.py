"""
smart_agent.py — LangChain ReAct Agent with Gemini 1.5 Pro + Tools + Memory
University Chatbot — Smart Backend
"""

import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_classic.memory import ConversationBufferWindowMemory
from db_config import get_connection

load_dotenv()

# ─────────────────────────────────────────────
# 🔧 TOOL DEFINITIONS
# ─────────────────────────────────────────────

@tool
def search_faculty_tool(query: str) -> str:
    """
    Search for faculty/professors at BBAU university.
    Use this when user asks about a teacher, professor, faculty member,
    their email, designation, department, school, phone, qualification, 
    specialization or experience.
    Input can be a name, department name, school name, or subject area.
    Examples: "Dr. Sharma", "computer science", "biotechnology department"
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Clean the query
    remove_words = [
        "who is", "tell me about", "show me", "details of",
        "faculty", "faculties", "professor", "sir", "mam", "madam",
        "department", "school", "of", "the", "in", "ka", "ki", "ke",
        "batao", "dikhao", "hai", "hain", "kya", "kaun", "list"
    ]
    q = query.lower().strip()
    for word in remove_words:
        q = re.sub(r'\b' + re.escape(word) + r'\b', '', q)
    q = q.strip()

    words = q.split()
    if not words:
        cursor.close()
        conn.close()
        return "Please specify a faculty name or department to search."

    conditions = []
    values = []
    for word in words:
        if len(word) < 2:
            continue
        conditions.append("""
        (
            LOWER(name) LIKE %s
            OR LOWER(department) LIKE %s
            OR LOWER(school) LIKE %s
            OR LOWER(specialization) LIKE %s
        )
        """)
        values.extend([f"%{word}%", f"%{word}%", f"%{word}%", f"%{word}%"])

    if not conditions:
        cursor.close()
        conn.close()
        return "Could not parse the query. Please try with a name or department."

    sql = "SELECT name, designation, department, school, email, phone, specialization, qualification FROM faculty WHERE " + " AND ".join(conditions) + " LIMIT 10"
    cursor.execute(sql, values)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    if not results:
        return f"No faculty found matching '{query}'. Try a different name or department."

    output = f"Found {len(results)} faculty member(s):\n\n"
    for f in results:
        output += f"👤 **{f['name']}**\n"
        output += f"   • Designation: {f['designation'] or 'N/A'}\n"
        output += f"   • Department: {f['department'] or 'N/A'}\n"
        output += f"   • School: {f['school'] or 'N/A'}\n"
        output += f"   • Email: {f['email'] or 'N/A'}\n"
        output += f"   • Phone: {f['phone'] or 'N/A'}\n"
        if f['specialization']:
            output += f"   • Specialization: {f['specialization']}\n"
        if f['qualification']:
            output += f"   • Qualification: {f['qualification']}\n"
        output += "\n"
    return output


@tool
def search_programme_tool(query: str) -> str:
    """
    Search for academic programmes/courses offered at BBAU university.
    Use this when user asks about programmes like B.Tech, M.Tech, MBA, M.Sc, 
    B.Sc, M.A, Ph.D, BBA, LLM, M.Phil, M.Pharm etc.
    Also use when asked about fees, duration, intake, or level of a programme.
    Examples: "btech", "MBA fees", "phd programme", "computer science programmes"
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    q = query.lower().strip()

    # Map common variations
    prog_map = {
        "btech": "b.tech", "b.tech": "b.tech", "b tech": "b.tech",
        "mtech": "m.tech", "m.tech": "m.tech", "m tech": "m.tech",
        "msc": "m.sc", "m.sc": "m.sc", "m sc": "m.sc",
        "bsc": "b.sc", "b.sc": "b.sc", "b sc": "b.sc",
        "mba": "mba", "ma": "m.a", "m.a": "m.a",
        "phd": "ph.d", "ph.d": "ph.d", "p.h.d": "ph.d",
        "mphil": "m.phil", "m.phil": "m.phil",
        "llm": "llm", "mpharm": "m.pharm", "m.pharm": "m.pharm",
        "bba llb": "bba-llb", "bba-llb": "bba-llb", "bba": "bba"
    }

    matched_prog = None
    for key, val in prog_map.items():
        if key in q:
            matched_prog = val
            break

    if matched_prog:
        cursor.execute(
            "SELECT * FROM programme WHERE LOWER(programme_name) LIKE %s LIMIT 15",
            (f"%{matched_prog}%",)
        )
    else:
        cursor.execute(
            """SELECT * FROM programme
               WHERE LOWER(programme_name) LIKE %s
               OR LOWER(department_name) LIKE %s
               OR LOWER(level) LIKE %s LIMIT 15""",
            (f"%{q}%", f"%{q}%", f"%{q}%")
        )

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    if not results:
        return f"No programme found matching '{query}'. Try 'btech', 'mba', 'msc', 'phd' etc."

    output = f"Found {len(results)} programme(s):\n\n"
    for p in results:
        output += f"📚 **{p['programme_name']}**\n"
        output += f"   • Department: {p.get('department_name', 'N/A')}\n"
        output += f"   • Level: {p.get('level', 'N/A')}\n"
        output += f"   • Duration: {p.get('duration', 'N/A')}\n"
        output += f"   • Intake: {p.get('intake', 'N/A')}\n"
        output += f"   • Fees: {p.get('fees', 'N/A')}\n"
        output += "\n"
    return output


@tool
def search_administration_tool(query: str) -> str:
    """
    Search for university administration officials at BBAU.
    Use this when user asks about Vice Chancellor, Chancellor, Registrar,
    Finance Officer, Dean, Proctor, Librarian, IQAC Director, Ombudsman,
    Board of Management, Academic Council, Planning Board etc.
    Returns their contact info (email, phone) and official page link.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT position_name, content, page_link FROM administration ORDER BY LENGTH(position_name) DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    q = query.lower().strip()
    for row in rows:
        position = row["position_name"].lower().strip()
        if q == position or q in position or position in q:
            content = row.get("content") or ""
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", content)
            phone_match = re.search(r"(\+91[-\s]?\d{10}|0522[-\s]?\d{6,10}|1800[-\s]?\d{3}[-\s]?\d{4})", content)
            return (
                f"🏛️ **{row['position_name']}**\n"
                f"   • Email: {email_match.group() if email_match else 'Not Available'}\n"
                f"   • Phone: {phone_match.group() if phone_match else 'Not Available'}\n"
                f"   • Official Page: {row['page_link']}\n"
            )

    return f"Administration info for '{query}' not found. Try: vice chancellor, registrar, dean, proctor, librarian."


@tool
def get_schools_and_departments_tool(query: str) -> str:
    """
    Get list of all schools or departments at BBAU university.
    Use this when user asks 'show all schools', 'list departments', 
    'kitne schools hain', 'sabhi departments', 'kitne departments'.
    Input: 'schools' or 'departments'
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    q = query.lower().strip()

    if "school" in q:
        cursor.execute("SELECT DISTINCT school_name FROM school ORDER BY school_name")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        if not rows:
            return "No school data found in the database."
        output = f"🏫 **BBAU has {len(rows)} Schools:**\n\n"
        for i, s in enumerate(rows, 1):
            output += f"{i}. {s['school_name']}\n"
        return output
    else:
        cursor.execute("SELECT DISTINCT department_name FROM department ORDER BY department_name")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        if not rows:
            return "No department data found in the database."
        output = f"🏢 **BBAU has {len(rows)} Departments:**\n\n"
        for i, d in enumerate(rows, 1):
            output += f"{i}. {d['department_name']}\n"
        return output


@tool
def search_university_web_tool(query: str) -> str:
    """
    Search the web for real-time information about BBAU university.
    Use this when the user asks about:
    - Latest news, notifications, or announcements
    - Admission dates, last dates, exam schedules
    - Events, results, cutoffs
    - Anything not found in the local database
    Always append 'BBAU' or 'Babasaheb Bhimrao Ambedkar University' to the search.
    """
    tavily = TavilySearchResults(max_results=3)
    enhanced_query = f"BBAU Babasaheb Bhimrao Ambedkar University Lucknow {query}"
    results = tavily.invoke(enhanced_query)

    if not results:
        return "No web results found. Please check the official BBAU website: https://www.bbau.ac.in"

    output = "🌐 **Web Search Results:**\n\n"
    for r in results:
        output += f"**{r.get('title', 'Result')}**\n"
        output += f"{r.get('content', '')[:400]}\n"
        output += f"🔗 {r.get('url', '')}\n\n"
    return output


# ─────────────────────────────────────────────
# 🤖 AGENT BUILDER
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are a smart, helpful university chatbot for **Babasaheb Bhimrao Ambedkar University (BBAU)**, Lucknow.

You can understand both **Hindi, Hinglish (Hindi+English mix), and English** queries.
Always respond in the same language the user writes in — if they write in Hinglish, reply in Hinglish.

**About BBAU:**
- Full Name: Babasaheb Bhimrao Ambedkar University
- Location: Lucknow, Uttar Pradesh, India
- Type: Central University
- NAAC Grade: A++
- Established: 1996
- Website: https://www.bbau.ac.in

**You have access to these tools:**
1. `search_faculty_tool` — Faculty/professor search by name or department
2. `search_programme_tool` — Academic programmes (B.Tech, M.Tech, MBA, PhD etc.)
3. `search_administration_tool` — Admin officials (Vice Chancellor, Registrar, Dean etc.)
4. `get_schools_and_departments_tool` — List all schools or departments
5. `search_university_web_tool` — Real-time web search for news, admissions, notifications

**Instructions:**
- ALWAYS use a tool when the user asks about specific data (faculty, programmes, admin)
- Use `search_university_web_tool` for admission dates, news, results, or anything not in DB
- Be conversational, friendly, and helpful
- If a user says "uska email" or "us faculty ki details", look at conversation history
- Keep responses clean and well-formatted with emojis for readability
- If asked something completely unrelated to BBAU, politely redirect

{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Previous conversation history:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}"""


def build_agent():
    """Build and return the LangChain ReAct agent with memory."""
    
    # llm = ChatGoogleGenerativeAI(
    #     model=os.getenv("LLM_MODEL", "gemini-1.5-pro"),
    #     google_api_key=os.getenv("GOOGLE_API_KEY"),
    #     temperature=float(os.getenv("LLM_TEMPERATURE", 0)),
    #     convert_system_message_to_human=True
    # )

    llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2
)

    tools = [
        search_faculty_tool,
        search_programme_tool,
        search_administration_tool,
        get_schools_and_departments_tool,
        search_university_web_tool,
    ]

    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=10,  # Remember last 10 messages
        return_messages=False
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        early_stopping_method="generate"
    )

    return agent_executor
