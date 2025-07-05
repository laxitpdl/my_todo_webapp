import streamlit as st                      # Importing Streamlit
import functions                            # Importing your custom module

todos = functions.get_todos()               # Load existing todos from file


def add_todo():                             # Add new todo from input box
    todo = st.session_state["new_todo"] + "\n"
    todos.append(todo)
    functions.write_todos(todos)


st.title("My Todo App")                     # Title of the app
st.subheader("This app is to increase productivity")  # Subheading

for todo in todos:                          # Loop through all todos
    checkbox = st.checkbox(todo, key=todo)  # Create checkbox with todo as key
    if checkbox:                            # If checkbox is ticked
        todos.remove(todo)                  # Remove todo from list
        functions.write_todos(todos)        # Save updated list
        del st.session_state[todo]          # Reset checkbox state
        st.rerun()             # Refresh the app immediately

st.text_input(                              # Text box to input new todo
    label="",
    placeholder="Add a new todo.......",
    on_change=add_todo,
    key="new_todo"
)
