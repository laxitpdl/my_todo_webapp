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

# --- Agent and LLM Setup ---
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    st.error("GEMINI_API_KEY not found. Please set it in your .env file or environment variables.")
    st.stop()

# --- AI Tools that modify Streamlit's session_state ---
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
    
    task_list = [f"{i+1}. {item['task']}" for i, item in enumerate(st.session_state.tasks)]
    return "Here is your current to-do list:\n" + "\n".join(task_list)

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

# --- Initialize the LLM and Agent with the NEW Conversational Prompt ---
tools = [add_task, show_task, edit_task]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key, temperature=0.7) # Slightly more creative temp

# NEW: This prompt gives the AI a friendlier personality and allows for casual conversation.
system_prompt = '''You are a friendly and helpful AI companion named Sparky.
Your primary role is to help the user manage their to-do list by adding, showing, and editing tasks.
However, you can also engage in casual conversation. Be friendly, encouraging, and natural in your responses.
When managing tasks, be concise and confirm when actions are completed.'''

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

# --- Initialize Session State Variables ---
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "history" not in st.session_state:
    st.session_state.history = []
if "task_to_confirm_delete" not in st.session_state:
    st.session_state.task_to_confirm_delete = None

# --- Main App Interface ---
st.title(" AI-Powered To-Do List")

# --- NEW: Two-Column Layout ---
col1, col2 = st.columns([2, 3]) # Chatbot gets 2/5 of the space, To-Do list gets 3/5

# --- Column 1: AI Chatbot ---
with col1:
    st.header("AI Assistant ✨")
    
    # Chat history display
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.history:
            role = "user" if isinstance(message, HumanMessage) else "assistant"
            with st.chat_message(role):
                st.markdown(message.content)

    # Chat input
    if user_input := st.chat_input("Ask me anything..."):
        st.session_state.history.append(HumanMessage(content=user_input))
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        
        with st.spinner("Thinking..."):
            response = agent_executor.invoke({
                "input": user_input,
                "history": st.session_state.history
            })
        
        st.session_state.history.append(AIMessage(content=response['output']))
        st.rerun()

# --- Column 2: To-Do List ---
with col2:
    st.header("Your Tasks")

    # Manual task input
    new_task = st.text_input("Add a new task manually:", placeholder="e.g., Finish coding project")
    if st.button("Add Task", use_container_width=True):
        if new_task:
            add_task.invoke({"task": new_task})
            st.rerun()
        else:
            st.warning("Please enter a task.")

    st.divider()

    # Display the to-do list
    for i, item in enumerate(st.session_state.tasks):
        # Use a checkbox to trigger the confirmation process
        st.checkbox(
            label=item["task"], 
            key=f"task_{i}", 
            on_change=lambda i=i: st.session_state.update(task_to_confirm_delete=i)
        )
    
    st.divider()

    # --- NEW: Confirmation Logic for Deleting Tasks ---
    if st.session_state.task_to_confirm_delete is not None:
        task_index = st.session_state.task_to_confirm_delete
        task_name = st.session_state.tasks[task_index]["task"]
        
        st.warning(f"Did you complete the task: **'{task_name}'**?")
        
        confirm_col1, confirm_col2 = st.columns(2)
        with confirm_col1:
            if st.button("Yes, Remove It", use_container_width=True, type="primary"):
                st.session_state.tasks.pop(task_index)
                st.session_state.task_to_confirm_delete = None # Reset confirmation
                st.toast(f"Great job on finishing '{task_name}'! 🎉")
                st.rerun()
        with confirm_col2:
            if st.button("No, Keep It", use_container_width=True):
                st.session_state.task_to_confirm_delete = None # Reset confirmation
                st.rerun()