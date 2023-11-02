import customtkinter
from CTkListbox import *

# Create the main application window
root = customtkinter.CTk()

# Function to move the selected item up in the list
def moveup():
    index = animalBox.curselection()
    if index > 0:
        animalBox.move_up(index)
        animalList[index - 1], animalList[index] = animalList[index], animalList[index - 1]

# Function to move the selected item down in the list
def movedown():
    index = animalBox.curselection()
    if index < animalBox.size() - 1:
        animalBox.move_down(index)
        animalList[index], animalList[index + 1] = animalList[index + 1], animalList[index]

# Function to handle the selection event in the listbox
def show_value(selected_option):
    print(selected_option)

# Initial list of animals
animalList = ['Cat', 'Dog', 'Bear', 'Dolphin', 'Kangaroo']

# Create a Tkinter StringVar with the initial list
animalString = customtkinter.StringVar(value=animalList)

# Create a custom listbox using CTkListbox
animalBox = CTkListbox(root, command=show_value, listvariable=animalString)
animalBox.grid(row=1, column=0, padx=20, pady=10)

# Create buttons for moving items up and down
moveupButton = customtkinter.CTkButton(root, text="Move Up", command=moveup, width=200, height=35)
moveupButton.grid(row=2, column=0, padx=20, pady=10)

movedownButton = customtkinter.CTkButton(root, text="Move Down", command=movedown, width=200, height=35)
movedownButton.grid(row=3, column=0, padx=20, pady=10)

# Start the Tkinter main loop
root.mainloop()
