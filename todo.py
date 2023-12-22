import tkinter as tk
from tkinter import messagebox, font
import json

# Dateiname für die Speicherung der Aufgaben
todo_filename = "todo_data.json"

def load_tasks():
    try:
        with open(todo_filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"todo_list": [], "completed_tasks": []}

def save_tasks():
    with open(todo_filename, "w") as f:
        json.dump({"todo_list": todo_list, "completed_tasks": completed_tasks}, f)

def add_task(*args):
    task = task_var.get()
    if task:
        todo_list.append(task)
        clear_entries()
        save_tasks()
        show_tasks()
    else:
        messagebox.showwarning("Fehler", "Bitte geben Sie eine Aufgabe ein.")

def complete_task(event):
    current_selection = listbox.curselection()
    if current_selection:
        completed_task = listbox.get(current_selection)
        listbox.delete(current_selection)
        todo_list.remove(completed_task)
        completed_tasks.append(completed_task)
        save_tasks()
        show_tasks()
        show_completed_tasks()

def restore_task(event):
    current_selection = completed_listbox.curselection()
    if current_selection:
        restored_task = completed_listbox.get(current_selection)
        completed_listbox.delete(current_selection)
        completed_tasks.remove(restored_task)
        todo_list.append(restored_task)
        save_tasks()
        show_tasks()
        show_completed_tasks()

def show_tasks():
    listbox.delete(0, tk.END)
    for task in todo_list:
        listbox.insert(tk.END, task)

def show_completed_tasks():
    completed_listbox.delete(0, tk.END)
    for task in completed_tasks:
        completed_listbox.insert(tk.END, task)

def clear_entries():
    task_var.set("")

# Lade Aufgaben beim Start
data = load_tasks()
todo_list = data["todo_list"]
completed_tasks = data["completed_tasks"]

# Set up the root window
root = tk.Tk()
root.title("TODO Liste")
root.geometry("200x480")
root.config(bg="#f5f5f5")

# Set up the fonts
title_font = font.Font(family="Helvetica", size=20, weight="bold")
label_font = font.Font(family="Helvetica", size=12)

# Set up the task entry
task_var = tk.StringVar()
task_entry = tk.Entry(root, textvariable=task_var, font=label_font, bg="#fff", fg="black", bd=0, highlightthickness=2, highlightcolor="#ccc", highlightbackground="#ccc")
task_entry.pack(pady=10)
task_entry.bind("<Return>", add_task)

# Set up the task list
listbox = tk.Listbox(root, font=label_font, bg="#fff",fg="black", bd=0, highlightthickness=2, highlightcolor="#ccc", highlightbackground="#ccc", height=10)
listbox.pack(side=tk.TOP, padx=10, pady=10)
listbox.bind("<Double-Button-1>", complete_task)

# Set up the completed tasks list
completed_listbox = tk.Listbox(root, font=label_font, bg="#fff", fg="black", bd=0, highlightthickness=2, highlightcolor="#ccc", highlightbackground="#ccc", height=10)
completed_listbox.pack(side=tk.TOP, padx=10, pady=10)
completed_listbox.bind("<Double-Button-1>", restore_task)

# Show the tasks and completed tasks
show_tasks()
show_completed_tasks()

root.mainloop()
