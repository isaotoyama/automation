import tkinter as tk
from tkinter import ttk
import csv
import time
import threading
from datetime import datetime, timedelta
from win10toast import ToastNotifier  

reminders = [] # List to store all reminders  
# Function to periodically check reminders
def check_reminders():
    while True:
        current_time = datetime.now()
        for reminder in reminders[:]:  
            if current_time >= reminder["remind_time"]:
                show_custom_notification(reminder["task_name"], reminder["description"])
                reminders.remove(reminder)
        time.sleep(10)  

# Thread to run the check reminders function
threading.Thread(target=check_reminders, daemon=True).start()

# Function to show custom notifications using Win10Toast
def show_custom_notification(task_name, description):
    toaster = ToastNotifier()
    toaster.show_toast(title=f"Reminder: {task_name}",msg=f"Description: {description}",icon_path="icon.ico",  duration=10,  threaded=True)

# Function to set a reminder
def set_reminder():
    task_name = task_name_entry.get()
    description = description_entry.get("1.0", tk.END).strip()
    time_minutes = float(time_entry.get())
    remind_time = datetime.now() + timedelta(minutes=time_minutes)

    ## Generate Logs on Console
    print(f'''
          Task Name: {task_name}\n
          Task Description: {description} \n
          Remind Time: {remind_time}\n''')
    print('Task added! I will remind you when the time comes.')

    # Saving Reminder Logs
    reminders.append({
        "task_name": task_name,
        "description": description,
        "remind_time": remind_time })
    with open('reminders.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([task_name, description, remind_time])

# Function to reset input fields
def add_task():
    task_name_entry.delete(0, tk.END)
    description_entry.delete("1.0", tk.END)
    time_entry.delete(0, tk.END)

# Function to create the GUI
def create_gui():
    global task_name_entry, description_entry, time_entry
    root = tk.Tk()

    # GUI Designing
    root.title("A Multi-Task Reminder App")
    root.geometry("500x400")
    root.configure(bg="#f7f7f7")
    title_frame = tk.Frame(root, bg="#4a90e2", pady=10)
    title_frame.pack(fill="x")
    title_label = tk.Label(title_frame, text="TaskTock", font=("Arial", 16, "bold"), fg="white", bg="#4a90e2")
    title_label.pack()
    form_frame = ttk.Frame(root, padding="20 20 20 10")
    form_frame.pack(fill="both", expand=True, padx=20, pady=20)
    ttk.Label(form_frame, text="Task Name:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
    task_name_entry = ttk.Entry(form_frame, width=40, font=("Arial", 10))
    task_name_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(form_frame, text="Description:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
    description_entry = tk.Text(form_frame, width=40, height=4, font=("Arial", 10))
    description_entry.grid(row=1, column=1, padx=5, pady=5)
    ttk.Label(form_frame, text="Time to Remind (minutes):", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
    time_entry = ttk.Entry(form_frame, width=40, font=("Arial", 10))
    time_entry.grid(row=2, column=1, padx=5, pady=5)
    button_frame = tk.Frame(root, bg="#f7f7f7")
    button_frame.pack(pady=10)
    set_button = tk.Button(button_frame, text="Set Reminder", command=set_reminder, font=("Arial", 10, "bold"), bg="#4a90e2", fg="white", width=15)
    set_button.pack(side="left", padx=10)
    add_button = tk.Button(button_frame, text="Add New Task", command=add_task, font=("Arial", 10, "bold"), bg="#f1c40f", fg="white", width=15)
    add_button.pack(side="left", padx=10)
    root.mainloop()

if __name__ == "__main__":
    create_gui()