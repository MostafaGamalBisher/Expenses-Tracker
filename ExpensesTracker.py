import tkinter as tk #tkinter module for GUI
from tkinter import ttk #ttk for themed widgets

from tkcalendar import DateEntry #date picker module
import customtkinter as ctk #import customtkinter for enhanced GUI elements

from tkinter import messagebox

from tksheet import Sheet

import pycountry #import pycountry for currency codes

import requests #import requests for API calls

from dotenv import load_dotenv #import dotenv to load environment variables
import os

category = ["life expenses", "electricity", "gas", "rental", "grocery", "savings", "education", "charity"]
payment_method = [ "Cash", "Credit Card", "Debit Card", "Mobile Payment", "Bank Transfer", "Check"]

total_egp = 0.0 

currency_listbox = None


# Load API Key
load_dotenv()
apikey = os.getenv("MY_SECRET_KEY")

#Making the ctkinter appearance and theme

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_currency_suggestions(text):    #function to get suggestions from pycountry library based on the entry of the user
    if not text:
        return []
    text = text.upper()
    suggestions = []
    for currency in pycountry.currencies:
        if currency.alpha_3.startswith(text):
            suggestions.append(currency.alpha_3)
    return suggestions[:8]

def show_suggestions(entry_widget, event):   #function to show the suggestions in a list under the Entry box
    text = entry_widget.get()
    suggestions = get_currency_suggestions(text)

    if not suggestions:
        currency_listbox.place_forget()
        return

    currency_listbox.delete(0, tk.END)
    for s in suggestions:
        currency_listbox.insert(tk.END, s)

    entry_widget.update_idletasks()

    x = entry_widget.winfo_rootx() - window.winfo_rootx()
    y = (
        entry_widget.winfo_rooty()
        - window.winfo_rooty()
        + entry_widget.winfo_height()
    )

    currency_listbox.place(x=x, y=y)
    currency_listbox.lift()


def fill_currency(event):    #function to fill the entry with the chosen currency
    try:
        selected = currency_listbox.get(currency_listbox.curselection())
        Currency_entry.delete(0, tk.END)
        Currency_entry.insert(0, selected)
    except:
        pass

    currency_listbox.place_forget()
    Currency_entry.focus_set()


def update_total_label(new_value):   #function to calcoulate the total 
    global total_egp
    total_egp += float(new_value)
    total_label_value.configure(text=f"Total: {total_egp} EGP")


def rates(user_currancy):    #getting the rates from currancy freaks API request

    url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={apikey}"

    try:
        response = requests.get(url)

        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to retrieve exchange rates.")
            return
        
        data = response.json()
        rates = data.get("rates", {})

        if user_currancy not in rates:
            messagebox.showerror("Error", f"Currency '{user_currancy}' not supported.")
            return None
         
        user_rate = float(rates[user_currancy])
        egp_rate = float(rates["EGP"])
            
        return user_rate, egp_rate
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return
    

def add_expense():   #function to add the expense to the sheet #attched to add expense button 

    amount = amount_entry.get().strip()
    currency = Currency_entry.get().strip()
    category = category_entry.get()
    payment_method = payment_method_entry.get()
    date = date_entry.get()

    if (  not amount or not currency or category == "Select Category" 
        or payment_method == "Select a Payment Method" or not date  ):

        messagebox.showerror("Error", "Incomplete Information")
        return
    
    try:
        amount = float(amount)
    except:
        messagebox.showerror("Error", "Invalid Amount")
        return
    

    if currency == "EGP":
        amount_egp = amount

    else:
        user_rate, egp_rate = rates(currency)
        
        amount_usd = round( amount / user_rate  , 2)
        amount_egp = round( amount_usd * egp_rate , 2)

    sheet.insert_row(
        [amount, currency, amount_egp, category, payment_method, date],
        idx=0
    )

    refresh_row_colors()


    # -------- Update Total -------- #   in EGP not USD

    update_total_label(amount_egp)

    amount_entry.delete(0, tk.END)
    Currency_entry.delete(0, tk.END)
    category_entry.set("Select Category")
    payment_method_entry.set("Select a Payment Method")
    
    from datetime import date
    date_entry.set_date(date.today())

#--------------------- Coloring Row with different colors to easen the reading ----------------#

def refresh_row_colors():
    total = sheet.get_total_rows()

    sheet.highlight_rows(
        rows=range(0, total, 2),
        bg="#0f172a",
        fg="#EFF1F3"
    )

    sheet.highlight_rows(
        rows=range(1, total, 2),
        bg="#162036",
        fg="#EFF1F3"
    )



#-------------------------- GUI -------------------------#


#------------------ creating the main window ------------------#

window = ctk.CTk()
window.title("Expenses Tracker")
window.geometry("1200x750")
window.configure(fg_color="#030612")

#------------------------- Make the window grid expand and center content -----------------------#

window.grid_columnconfigure(0, weight=1)   # left empty space
window.grid_columnconfigure(1, weight=0)   # main content stays centered
window.grid_columnconfigure(2, weight=1)   # right empty space

#------------------- Title label -----------------#

title_label = ctk.CTkLabel(window, text="Track Your Expense", font=("Calibri", 24, "bold"), text_color="#79AFE6",
                             width=300, corner_radius=10,fg_color="#0f172a",
                              pady=10, padx=10)
title_label.grid(row=0, column=1, pady=10)

#------------------------- Input Labels Frames -----------------#

labels_frame = ctk.CTkFrame(window, height=200, corner_radius=10,
                                   fg_color="#0f172a", border_width=1, border_color="#79AFE6")
labels_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")

#------------------------- AMOUNT -----------------#

amount_label = ctk.CTkLabel(labels_frame, text="Amount", font=("Calibri", 18), text_color="#79AFE6",
                             width=100, corner_radius=15,fg_color="#2D3A4B")
amount_label.grid(row=0 , column=0 ,  padx=40 , pady=15, sticky="ew")

amount_entry = ctk.CTkEntry(labels_frame, font=("Calibri", 14),text_color="#EFF1F3",
                             width=150, corner_radius=5,fg_color="#2D3A4B", border_width=1, border_color="#79AFE6")
amount_entry.grid(row=1, column=0, padx=27, pady=15, sticky="ew")

#------------------------- Currncy -----------------#

Currency_label= ctk.CTkLabel(labels_frame, text="Currency", font=("Calibri", 18), text_color="#79AFE6",
                              width=100, corner_radius=15,fg_color="#2D3A4B")
Currency_label.grid(row=0, column=1,  padx=40, pady=15, sticky="ew")

Currency_entry = ctk.CTkEntry(labels_frame, font=("Calibri", 14),text_color="#EFF1F3",
                             width=150, corner_radius=5,fg_color="#2D3A4B", border_width=1, border_color="#79AFE6")
Currency_entry.grid(row=1, column=1, padx=27, pady=15, sticky="ew")


#---------------------- Currency listbox -------------#

currency_listbox = tk.Listbox(
    window,
    height=5,
    bg="#0f172a",
    fg="#EFF1F3",
    selectbackground="#2563eb",
    selectforeground="white",
    font=("Calibri", 12)
)

currency_listbox.place_forget()

currency_listbox.bind("<<ListboxSelect>>", fill_currency)

Currency_entry.bind(
    "<KeyRelease>",
    lambda event: show_suggestions(Currency_entry, event)
)


Currency_entry.bind("<FocusOut>", lambda e: currency_listbox.place_forget())


#------------------------- Category -----------------#

category_label = ctk.CTkLabel(labels_frame, text= "Category", font=("Calibri", 18), text_color="#79AFE6",
                               width=100, corner_radius=15,fg_color="#2D3A4B")
category_label.grid(row=0, column=2,  padx=40, pady=15, sticky="ew")

category_entry = ctk.CTkComboBox(labels_frame, font=("Calibri", 10), values=category,text_color="#EFF1F3",
                             width=150, corner_radius=5,fg_color="#2D3A4B", border_width=1, border_color="#79AFE6")
category_entry.set("Select Category")
category_entry.grid(row=1, column=2, padx=27, pady=15, sticky="ew")

#------------------------- Payment Method -----------------#

payment_method_label = ctk.CTkLabel(labels_frame, text="Payment Method", font=("Calibri", 18), text_color="#79AFE6",
                                     width=100, corner_radius=15,fg_color="#2D3A4B")
payment_method_label.grid(row=0, column=3, padx=40, pady=15, sticky="ew")

payment_method_entry = ctk.CTkComboBox(labels_frame, font=("Calibri", 10), values=payment_method,text_color="#EFF1F3",
                             width=150, corner_radius=5,fg_color="#2D3A4B", border_width=1, border_color="#79AFE6")
payment_method_entry.set("Select a Payment Method")
payment_method_entry.grid(row=1, column=3, padx=27, pady=15, sticky="ew")

#------------------------- Date -----------------#

date_label = ctk.CTkLabel(labels_frame, text="Date", font=("Calibri", 18), text_color="#79AFE6",
                           width=100, corner_radius=15,fg_color="#2D3A4B")
date_label.grid(row=0, column=4, padx=40, pady=15, sticky="ew")

date_entry = DateEntry(labels_frame,width=17,background="#1f2937",foreground="white",borderwidth=0,
                       justify="center", date_pattern='y-mm-dd')
date_entry.grid(row=1, column=4, padx=27, pady=15, sticky="ew")

#------------------------- Add Expense Button -----------------#

add_expense_button = ctk.CTkButton(window, text="Add Expense", font=("Calibri", 18),text_color="#79AFE6",
                                    width=200, corner_radius=10,fg_color="#0f172a", border_width=1, border_color="#79AFE6"
                                    , command=add_expense)
add_expense_button.grid(row=2, column=1, pady=10, sticky="n")

# ------------------ table area -----------------#

#------------------- Table Frame -----------------#

table_wrapper = ctk.CTkFrame(
    window,
    fg_color="#0f172a",
    border_width=1,
    border_color="#79AFE6",
    corner_radius=10
)
table_wrapper.grid(row=3, column=1, pady=20, padx=20, sticky="nsew")

table_wrapper.grid_rowconfigure(0, weight=1)
table_wrapper.grid_columnconfigure(0, weight=1)


# ----------------------- SHEET -----------------------#

sheet = Sheet(
    table_wrapper,
    headers=["Amount", "Currency","Amount in EGP", "Category", "Payment Method", "Date"],
    height=500,
    width=1400,
    column_width=150,
    row_height=32,
    header_height=40,
    font=("Arial", 13, "normal"),
    header_font=("Calibri", 14, "bold"),
    show_x_scrollbar=True,
    show_y_scrollbar=True
)

sheet.grid(row=0, column=0, sticky="nsew")


# --------------------- INDIVIDUAL COLUMN WIDTHS ---------------#

sheet.column_width(0, 150)   # Amount
sheet.column_width(1, 150)   # Currency
sheet.column_width(2, 150)   # Amount in EGP
sheet.column_width(3, 280)   # Category
sheet.column_width(4, 300)   # Payment Method
sheet.column_width(5, 320)   # Date


# ---------------- GRID / BORDER STYLE -----------------#

sheet.set_options(
    table_bg="#0f172a",
    table_fg="#F7F3F3",
    table_grid_fg="#1E2A3A",
    table_grid_thickness=1,
    header_bg="#0f172a",
    header_fg="#79AFE6",
    header_grid_fg="#1E2A3A",
    header_grid_thickness=1,
)


# --------------- ALTERNATING ROW COLORS --------------#

sheet.highlight_rows(
    rows=range(0, sheet.get_total_rows(), 2),
    bg="#0f172a",
    fg="#EFF1F3"
)

sheet.highlight_rows(
    rows=range(1, sheet.get_total_rows(), 2),
    bg="#162036",
    fg="#EFF1F3"
)

#------------------------- Total frame -----------------#
total_frame = ctk.CTkFrame(
    window,
    fg_color="#0f172a",
    border_width=1,
    border_color="#79AFE6",
    corner_radius=12,
)
total_frame.grid(row=4, column=1, pady=(10, 40), padx=20, sticky="ew")

#------------------------- Total Label -----------------#
total_label_title = ctk.CTkLabel(
    total_frame,
    text="Total Amount (EGP):",
    font=("Arial", 20, "bold"),
    text_color="#79AFE6"
)
total_label_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")

total_label_value = ctk.CTkLabel(
    total_frame,
    text="0.00 EGP",
    font=("Arial", 22, "bold"),
    text_color="#4ADE80"   
)
total_label_value.grid(row=0, column=1, padx=20, pady=15, sticky="w")


window.mainloop()