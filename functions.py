
FILEPATH = "extra.txt"  # This is the path to the file where the todos are stored. It is used to read and write the todos from/to the file.

def get_todos(filepath=FILEPATH):  # def function is used for repetitive tasks, so that we can call it whenever we need it.
    """Read the todos from a file and return them as a list."""   #docstring is used to describe the function and its purpose.
   # This function reads the todos from a file and returns them as a list.
    
    with open(FILEPATH, "r") as file_local:     #with statement is used to open a file and automatically close it after the block of code is executed.
            todos_local = file_local.readlines()                  ##readlines() method reads all the lines in a file and returns them as a list.
    return todos_local
#return statement is used to return the value of todos_local to the caller of the function.
# This function is used to read the todos from the file and return them as a list.    


#todos_arg = get_todos()   non default parameters before default parameter todo_arg is non def # This line is commented out because we are not using it now. It was used to get the todos from the file.
def write_todos(todos_arg, filepath=FILEPATH):  #it needs to know what to write in the file i.e todo so todo_arg and its filepath  # This function is used to write the todos to the file.
    """Write the todos to a text file."""
    # This function takes a list of todos and writes them to a file.
    
    with open(filepath, "w") as file_local:  #with statement is used to open a file and automatically close it after the block of code is executed.
        file_local.writelines(todos_arg)     #writelines() method is used to write a list of strings to a file.
# no return statement is needed here because we are writing the todos to the file, not returning anything.


#print(__name__)  # This line is used to check if the file is being executed or imported. If it is being executed, it will print "__main__". If it is being imported, it will print the name of the module.
#__name__ is a special variable in Python that is set to "__main__" when the file is being executed directly, and to the name of the module when it is being imported.
#and it is function in main programme as in import functions


if __name__ == "__main__":  # This line is used to check if the file is being executed or imported. If it is being executed, it will run the code inside this block.
    print("hello from functions.py")  # This line is used to check if the file is being executed or imported. If it is being executed, it will print this message.
    print(get_todos())  # This line is used to check if the get_todos() function is working properly. It will print the todos from the file.
























