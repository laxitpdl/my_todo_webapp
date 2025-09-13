import streamlit as st
import os
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts.chat import MessagesPlaceholder

# --- App Configuration ---
st.set_page_config(page_title="AI Todo Assistant", layout="wide")

# --- Agent and LLM Setup (Moved from the old file) ---

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is available
if not gemini_api_key:
    st.error("GEMINI_API_KEY not found. Please set it in your .env file or environment variables.")
    st.stop()

# --- NEW: AI Tools that modify Streamlit's session_state ---

@tool
def add_task(task: str, describe: str = None):
    """Add a new task to the user's to-do list. Use this when the user wants to add or create a task."""
    st.session_state.tasks.append({"task": task, "completed": False})
    return f"Task '{task}' was added successfully!"

@tool
def show_task():
    """Show all tasks from the to-do list. Use this when the user wants to see their tasks."""
    if not st.session_state.tasks:
        return "The to-do list is empty."
    
    task_list = []
    for i, item in enumerate(st.session_state.tasks):
        status = "✓" if item["completed"] else " "
        task_list.append(f"{i+1}. [{status}] {item['task']}")
    
    return "Here is the current to-do list:\n" + "\n".join(task_list)

@tool
def edit_task(current_task_name: str, new_task_name: str):
    """Edit an existing task. Use this to change, update, or edit a task."""
    task_found = False
    for item in st.session_state.tasks:
        if item["task"] == current_task_name:
            item["task"] = new_task_name
            task_found = True
            break
            
    if task_found:
        return f"Successfully updated task from '{current_task_name}' to '{new_task_name}'."
    else:
        return f"Error: Could not find a task named '{current_task_name}'."

# Initialize the LLM and Agent
tools = [add_task, show_task, edit_task]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key, temperature=0.3)
system_prompt = '''You are a helpful assistant integrated into a to-do app.
Help the user manage their tasks by adding, showing, and editing them.
Be concise and confirm when actions are completed.'''
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False) # Set verbose to False for cleaner UI

# --- Main App Interface ---

st.title("✅ My AI-Powered To-Do List")
st.write("Manage your tasks in the main window or use the AI assistant in the sidebar!")

# Initialize the to-do list in session_state if it doesn't exist
if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"task": "Welcome! Add your tasks below.", "completed": False},
        {"task": "Use the sidebar chatbot for help.", "completed": False},
    ]

# Manual task input
new_task = st.text_input("Add a new task manually:", placeholder="e.g., Buy groceries")
if st.button("Add Task", use_container_width=True):
    if new_task:
        add_task.invoke({"task": new_task}) # We can call our tool directly!
        st.rerun() # Rerun the app to show the new task immediately
    else:
        st.warning("Please enter a task.")

# Display the to-do list
st.header("Your Tasks")
for i, item in enumerate(st.session_state.tasks):
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        # Checkbox state is tied to the 'completed' status of the task
        is_completed = st.checkbox("", value=item["completed"], key=f"task_{i}")
        st.session_state.tasks[i]["completed"] = is_completed
    with col2:
        # Display the task name, striked-through if completed
        task_text = f"~~{item['task']}~~" if item["completed"] else item["task"]
        st.markdown(f"<p style='padding-top: 5px;'>{task_text}</p>", unsafe_allow_html=True)


# --- Sidebar Chatbot Interface ---

with st.sidebar:
    st.header("AI Assistant 🤖")
    
    # Initialize chat history
    if "history" not in st.session_state:
        st.session_state.history = []

    # Display past messages
    for message in st.session_state.history:
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(message.content)

    # Chat input
    if user_input := st.chat_input("Ask me to add, show, or edit a task..."):
        # Add user message to history and display it
        st.session_state.history.append(HumanMessage(content=user_input))
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get the AI's response
        with st.spinner("Thinking..."):
            response = agent_executor.invoke({
                "input": user_input,
                "history": st.session_state.history
            })
        
        # Add AI response to history and display it
        st.session_state.history.append(AIMessage(content=response['output']))
        with st.chat_message("assistant"):
            st.markdown(response['output'])
        
        # Rerun the app to instantly update the main to-do list after an AI action
        st.rerun()