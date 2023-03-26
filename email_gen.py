#!python
import datetime
import tkinter as tk
from tkinter import ttk

def generate_message(date, location, time, sag_driver):
    base_message = (
        "Please fill out this form if you plan on attending the {Date} training ride "
        "leaving {Location}. Please be prepared to arrive a few minutes early and "
        "be ready to roll at {Time}. {SAG_line} Please come prepared with plenty "
        "of water and a spare tube and the tools needed to fix a flat."
        f"\n\n"
    )
    
    if sag_driver:
        sag_line = "There will be limited SAG (support and gear) space available."
    else:
        sag_line = "There will be no SAG (support and gear) space available."

    return base_message.format(Date=date, Location=location, Time=time, SAG_line=sag_line)

def ordinal(n):
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix

def on_submit():
    date_input = date_entry.get()
    date_obj = datetime.datetime.strptime(date_input, "%m/%d")
    day_with_suffix = ordinal(date_obj.day)
    formatted_date = date_obj.strftime("%B ") + day_with_suffix

    location = location_entry.get()

    if location.lower() == "westmo":
        location = "Westmoreland Upper Elementary School"
    if location.lower() == "sauqouit":
        location = "Sauquoit Valley High Schoo"
    if location.lower() == "herkimer":
        location = "Herkimer Hannford"
    if location.lower == "marcy":
        location = "Town of Marcy Town Hall"

    time = time_entry.get()
    sag_driver = sag_var.get()

    message = generate_message(formatted_date, location, time, sag_driver)

    form_link = form_entry.get()
    training_schedule_link = "https://docs.google.com/document/d/1pJTQTW1wuFcYQ8b3n8x2Lu5aDFjQn6pe"  # Replace with the actual URL

    second_block = (
        f"Our next training ride is scheduled for {formatted_date} at {time}. "
        f"We will be leaving from {location}. Please fill out this form located here if you are able to attend. "
        f"{form_link}"
        f"If you signed up and need to cancel, please notify the ride leader(s) as indicated on the bottom of the signup sheet.\n\n"

        f"Our Training ride schedule has also been updated to include the planned routes as well as the starting locations. "
        f"Please be aware that last-minute changes may be made to the route, and we apologize if this causes any inconvenience.\n\n"

        f"For cancellation notices, we will be using the Ride Line and the \"CNY Ride Family\" Facebook group. "
        f"We will make every effort to have these updated before any of you should start making your way to the ride location. "
        f"The ride number is 315-624-RIDE (7433)."
        f"\n\n"
        f"{training_schedule_link}"
    )


# def on_submit():
#     date_input = date_entry.get()
#     date_obj = datetime.datetime.strptime(date_input, "%m/%d")
#     day_with_suffix = ordinal(date_obj.day)
#     formatted_date = date_obj.strftime("%B ") + day_with_suffix

#     location = location_entry.get()

#     if location.lower() == "westmo":
#         location = "Westmoreland Upper Elementary School"

#     time = time_entry.get()
#     sag_driver = sag_var.get()

#     message = generate_message(formatted_date, location, time, sag_driver)

#     form_link = form_entry.get()
#     training_schedule_link = "https://example.com/training_schedule"  # Replace with the actual URL

#     second_block = (
#         f"Our next training ride is scheduled for {formatted_date} at {time}. "
#         f"We will be leaving from {location}. Please <a href='{form_link}'>fill out this form</a> if you are able to attend. "
#         f"If you signed up and need to cancel, please notify the ride leader(s) as indicated on the bottom of the signup sheet.<br><br>"

#         f"Our <a href='{training_schedule_link}'>Training ride schedule</a> has also been updated to include the planned routes as well as the starting locations. "
#         f"Please be aware that last-minute changes may be made to the route, and we apologize if this causes any inconvenience.<br><br>"

#         f"For cancellation notices, we will be using the Ride Line and the \"CNY Ride Family\" Facebook group. "
#         f"We will make every effort to have these updated before any of you should start making your way to the ride location. "
#         f"The ride number is 315-624-RIDE (7433)."
#     )

    output_message = message + f"\n\nEmail content:\n\n" + second_block
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, output_message)


root = tk.Tk()
root.title("Training Ride Message Generator")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(mainframe, text="Date (e.g., 4/1):").grid(row=0, column=0, sticky=tk.W)
date_entry = ttk.Entry(mainframe)
date_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

ttk.Label(mainframe, text="Location (e.g., Westmo, Herkimer, Saquoit):").grid(row=1, column=0, sticky=tk.W)
location_entry = ttk.Entry(mainframe)
location_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

ttk.Label(mainframe, text="Time (e.g., 8:00 AM):").grid(row=2, column=0, sticky=tk.W)
time_entry = ttk.Entry(mainframe)
time_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

sag_var = tk.BooleanVar()
ttk.Label(mainframe, text="Is there a SAG driver available?").grid(row=3, column=0, sticky=tk.W)
ttk.Checkbutton(mainframe, variable=sag_var).grid(row=3, column=1, sticky=tk.W)

ttk.Label(mainframe, text="Form link:").grid(row=4, column=0, sticky=tk.W)
form_entry = ttk.Entry(mainframe)
form_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

ttk.Button(mainframe, text="Submit", command=on_submit).grid(row=5, columnspan=2)

result_text = tk.Text(root, wrap=tk.WORD, height=10, padx=10, pady=10)
result_text.grid(row=1, column=0)

root.mainloop()
