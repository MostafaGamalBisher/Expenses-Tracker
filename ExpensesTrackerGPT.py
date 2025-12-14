# ===================== EXPENSES TRACKER – ENHANCED & PROFESSIONAL =====================
# Improved Validation • Better UI/UX • Stable Logic • Enhanced Error Handling
# ------------------------------------------------------------------------------------

import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import customtkinter as ctk
from tksheet import Sheet
import pycountry
import requests
from dotenv import load_dotenv
import os
from datetime import datetime, date
import re

# ===================== CONFIG =====================
load_dotenv()
API_KEY = os.getenv("MY_SECRET_KEY")
DATA_FILE = "expenses.txt"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Enhanced Color Scheme
BG_MAIN = "#0a0e1a"
BG_PANEL = "#1a1f35"
BG_INPUT = "#242b42"
ACCENT = "#38bdf8"
ACCENT_HOVER = "#0ea5e9"
TEXT = "#e5e7eb"
TEXT_SECONDARY = "#94a3b8"
SUCCESS = "#22c55e"
ERROR = "#ef4444"
WARNING = "#f59e0b"

categories = [
    "Food & Dining", "Transportation", "Utilities",
    "Entertainment", "Healthcare", "Personal Care",
    "Education", "Gifts & Donations", "Shopping",
    "Housing", "Insurance", "Savings & Investments", "Other"
]

payments = [
    "Cash", "Credit Card", "Debit Card",
    "Mobile Payment", "Bank Transfer", "Check", "Digital Wallet"
]

total_egp = 0.0
selected_row = None
is_editing = False

# ===================== VALIDATION =====================
def validate_amount(amount_str):
    """Validate amount input"""
    if not amount_str or amount_str.strip() == "":
        return False, "Amount is required"
    
    # Remove spaces and check for valid number format
    amount_str = amount_str.strip()
    
    # Allow decimal numbers with optional comma separators
    if not re.match(r'^\d+\.?\d*$', amount_str):
        return False, "Invalid amount format. Use numbers only (e.g., 100 or 100.50)"
    
    try:
        amount = float(amount_str)
        if amount <= 0:
            return False, "Amount must be greater than zero"
        if amount > 999999999:
            return False, "Amount is too large"
        return True, amount
    except ValueError:
        return False, "Invalid number format"

def validate_currency(currency_str):
    """Validate currency code"""
    if not currency_str or currency_str.strip() == "":
        return False, "Currency is required"
    
    currency_str = currency_str.strip().upper()
    
    if len(currency_str) != 3:
        return False, "Currency code must be 3 letters (e.g., USD, EUR, SAR)"
    
    # Check if valid ISO currency code
    try:
        pycountry.currencies.get(alpha_3=currency_str)
        return True, currency_str
    except:
        return False, f"Invalid currency code: {currency_str}"

def validate_date(date_str):
    """Validate date format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, date_str
    except:
        return False, "Invalid date format"

def validate_inputs(amount, currency, category, payment):
    """Comprehensive input validation"""
    errors = []
    
    # Validate amount
    is_valid, result = validate_amount(amount)
    if not is_valid:
        errors.append(result)
    
    # Validate currency
    is_valid, result = validate_currency(currency)
    if not is_valid:
        errors.append(result)
    
    # Validate category
    if not category or category == "Select Category":
        errors.append("Please select a category")
    
    # Validate payment method
    if not payment or payment == "Select Payment Method":
        errors.append("Please select a payment method")
    
    return len(errors) == 0, errors

# ===================== HELPERS =====================
def get_currency_suggestions(text):
    """Get currency suggestions with caching"""
    if not text or len(text) < 1:
        return []
    text = text.upper()
    suggestions = []
    for c in pycountry.currencies:
        if c.alpha_3.startswith(text):
            suggestions.append(c.alpha_3)
        if len(suggestions) >= 10:
            break
    return suggestions

def fetch_rates(currency):
    """Fetch exchange rates with error handling"""
    if currency == "EGP":
        return None, None
    
    try:
        url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            raise Exception("Failed to fetch exchange rates")
        
        rates = response.json()["rates"]
        
        if currency not in rates:
            raise Exception(f"Currency {currency} not found in rates")
        
        return float(rates[currency]), float(rates["EGP"])
    
    except requests.exceptions.Timeout:
        messagebox.showerror("Error", "Connection timeout. Please check your internet.")
        return None, None
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Error", "No internet connection.")
        return None, None
    except Exception as e:
        messagebox.showerror("Error", f"Exchange rate error: {str(e)}")
        return None, None

def refresh_rows():
    """Refresh row styling with alternating colors"""
    rows = sheet.get_total_rows()
    if rows == 0:
        return
    
    # Alternating row colors
    for i in range(rows):
        if i % 2 == 0:
            sheet.highlight_rows([i], bg="#1a1f35", fg=TEXT)
        else:
            sheet.highlight_rows([i], bg="#242b42", fg=TEXT)

def update_total():
    """Update total with proper formatting"""
    global total_egp
    total_egp = 0.0
    
    for r in range(sheet.get_total_rows()):
        try:
            egp_value = sheet.get_cell_data(r, 2)
            if egp_value:
                total_egp += float(egp_value)
        except (ValueError, TypeError):
            continue
    
    # Format with thousands separator
    formatted_total = f"{total_egp:,.2f}"
    total_label.configure(text=f"Total: {formatted_total} EGP")
    
    # Update row count
    row_count_label.configure(text=f"Total Expenses: {sheet.get_total_rows()}")

def save_data():
    """Save data with error handling"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            for r in range(sheet.get_total_rows()):
                row_data = sheet.get_row_data(r)
                f.write("|".join(map(str, row_data)) + "\n")
        status_label.configure(text="✓ Data saved successfully", text_color=SUCCESS)
        window.after(3000, lambda: status_label.configure(text=""))
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save data: {str(e)}")

def load_data():
    """Load data with validation"""
    if not os.path.exists(DATA_FILE):
        return
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = line.strip().split("|")
                    if len(data) == 7:  # Ensure correct number of fields
                        sheet.insert_row(data)
        refresh_rows()
        update_total()
        status_label.configure(text="✓ Data loaded successfully", text_color=SUCCESS)
        window.after(3000, lambda: status_label.configure(text=""))
    except Exception as e:
        messagebox.showerror("Load Error", f"Failed to load data: {str(e)}")

# ===================== CURRENCY AUTOCOMPLETE =====================
def show_currency(event):
    """Show currency suggestions dropdown"""
    items = get_currency_suggestions(currency_entry.get())
    currency_list.delete(0, tk.END)

    if not items:
        currency_list.place_forget()
        return

    for i in items:
        currency_list.insert(tk.END, i)

    # Position dropdown below entry
    x = currency_entry.winfo_rootx() - window.winfo_rootx()
    y = currency_entry.winfo_rooty() - window.winfo_rooty() + currency_entry.winfo_height() + 2
    currency_list.place(x=x, y=y, width=currency_entry.winfo_width())
    currency_list.lift()

def select_currency(event=None):
    """Select currency from dropdown"""
    try:
        selection = currency_list.curselection()
        if selection:
            value = currency_list.get(selection)
            currency_entry.delete(0, tk.END)
            currency_entry.insert(0, value)
    except:
        pass
    currency_list.place_forget()
    category_box.focus_set()

def hide_currency_list(event):
    """Hide currency dropdown"""
    currency_list.place_forget()

# ===================== CRUD OPERATIONS =====================
def clear_inputs():
    """Clear all input fields"""
    global is_editing, selected_row
    
    amount_entry.delete(0, tk.END)
    currency_entry.delete(0, tk.END)
    category_box.set("Select Category")
    payment_box.set("Select Payment Method")
    date_entry.set_date(date.today())
    due_entry.set_date(date.today())
    
    is_editing = False
    selected_row = None
    
    # Update button states
    add_btn.configure(text="Add Expense")
    update_btn.configure(state="disabled")
    cancel_btn.configure(state="disabled")
    
    # Remove selection highlight
    sheet.deselect("all")
    
    amount_entry.focus_set()

def add_expense():
    """Add new expense with validation"""
    amount = amount_entry.get().strip()
    currency = currency_entry.get().strip().upper()
    category = category_box.get()
    payment = payment_box.get()
    exp_date = date_entry.get()
    due_date = due_entry.get()

    # Validate inputs
    is_valid, errors = validate_inputs(amount, currency, category, payment)
    if not is_valid:
        messagebox.showerror("Validation Error", "\n".join(f"• {err}" for err in errors))
        return

    # Convert amount
    try:
        amount_value = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Invalid amount format")
        return

    # Calculate EGP equivalent
    if currency == "EGP":
        egp_value = amount_value
    else:
        rates = fetch_rates(currency)
        if rates[0] is None or rates[1] is None:
            return  # Error already shown in fetch_rates
        
        usd_rate, egp_rate = rates
        egp_value = round((amount_value / usd_rate) * egp_rate, 2)

    # Add to sheet
    sheet.insert_row([
        f"{amount_value:.2f}",
        currency,
        f"{egp_value:.2f}",
        category,
        payment,
        exp_date,
        due_date
    ], idx=0)
    
    refresh_rows()
    update_total()
    save_data()
    clear_inputs()
    
    messagebox.showinfo("Success", "Expense added successfully!")

def update_expense():
    """Update selected expense"""
    global selected_row
    
    if selected_row is None:
        messagebox.showwarning("Warning", "Please select an expense to update")
        return

    amount = amount_entry.get().strip()
    currency = currency_entry.get().strip().upper()
    category = category_box.get()
    payment = payment_box.get()
    exp_date = date_entry.get()
    due_date = due_entry.get()

    # Validate inputs
    is_valid, errors = validate_inputs(amount, currency, category, payment)
    if not is_valid:
        messagebox.showerror("Validation Error", "\n".join(f"• {err}" for err in errors))
        return

    try:
        amount_value = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Invalid amount format")
        return

    # Calculate EGP equivalent
    if currency == "EGP":
        egp_value = amount_value
    else:
        rates = fetch_rates(currency)
        if rates[0] is None or rates[1] is None:
            return
        
        usd_rate, egp_rate = rates
        egp_value = round((amount_value / usd_rate) * egp_rate, 2)

    # Update row
    sheet.set_row_data(selected_row, [
        f"{amount_value:.2f}",
        currency,
        f"{egp_value:.2f}",
        category,
        payment,
        exp_date,
        due_date
    ])
    
    refresh_rows()
    update_total()
    save_data()
    clear_inputs()
    
    messagebox.showinfo("Success", "Expense updated successfully!")

def delete_row():
    """Delete selected row with confirmation"""
    selection = sheet.get_currently_selected()
    if not selection or selection[0] is None:
        messagebox.showwarning("Warning", "Please select an expense to delete")
        return
    
    # Confirm deletion
    result = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this expense?",
        icon='warning'
    )
    
    if result:
        sheet.delete_row(selection[0])
        refresh_rows()
        update_total()
        save_data()
        clear_inputs()
        messagebox.showinfo("Success", "Expense deleted successfully!")

def select_row(event):
    """Select row for editing"""
    global selected_row, is_editing
    
    selection = sheet.get_currently_selected()
    if not selection or selection[0] is None:
        return
    
    selected_row = selection[0]
    is_editing = True
    
    try:
        data = sheet.get_row_data(selected_row)
        
        # Populate fields
        amount_entry.delete(0, tk.END)
        amount_entry.insert(0, data[0])
        
        currency_entry.delete(0, tk.END)
        currency_entry.insert(0, data[1])
        
        category_box.set(data[3])
        payment_box.set(data[4])
        
        date_entry.set_date(data[5])
        due_entry.set_date(data[6])
        
        # Update button states
        add_btn.configure(text="Add New")
        update_btn.configure(state="normal")
        cancel_btn.configure(state="normal")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load expense: {str(e)}")
        clear_inputs()

# ===================== UI CONSTRUCTION =====================
window = ctk.CTk()
window.title("Expenses Tracker - Professional Edition")
window.geometry("1300x850")
window.configure(fg_color=BG_MAIN)

# Prevent window from being too small
window.minsize(1200, 750)

# ===== HEADER =====
header_frame = ctk.CTkFrame(window, fg_color="transparent")
header_frame.pack(pady=(15, 10), padx=20, fill="x")

title = ctk.CTkLabel(
    header_frame,
    text="💰 Expenses Tracker",
    font=("Segoe UI", 32, "bold"),
    text_color=ACCENT
)
title.pack(side="left")

status_label = ctk.CTkLabel(
    header_frame,
    text="",
    font=("Segoe UI", 12),
    text_color=TEXT_SECONDARY
)
status_label.pack(side="right", padx=20)

# ===== INPUT PANEL =====
input_panel = ctk.CTkFrame(
    window,
    fg_color=BG_PANEL,
    corner_radius=12,
    border_width=1,
    border_color="#334155"
)
input_panel.pack(padx=20, pady=10, fill="x")

# Row 1: Amount, Currency, Category
row1 = ctk.CTkFrame(input_panel, fg_color="transparent")
row1.pack(pady=(20, 10), padx=20, fill="x")

# Amount
amount_frame = ctk.CTkFrame(row1, fg_color="transparent")
amount_frame.pack(side="left", padx=(0, 15))
ctk.CTkLabel(amount_frame, text="Amount *", font=("Segoe UI", 11, "bold"), text_color=TEXT_SECONDARY).pack(anchor="w")
amount_entry = ctk.CTkEntry(
    amount_frame,
    width=160,
    placeholder_text="0.00",
    font=("Segoe UI", 12),
    fg_color=BG_INPUT,
    border_color="#334155"
)
amount_entry.pack(pady=(3, 0))

# Currency
currency_frame = ctk.CTkFrame(row1, fg_color="transparent")
currency_frame.pack(side="left", padx=15)
ctk.CTkLabel(currency_frame, text="Currency *", font=("Segoe UI", 11, "bold"), text_color=TEXT_SECONDARY).pack(anchor="w")
currency_entry = ctk.CTkEntry(
    currency_frame,
    width=160,
    placeholder_text="EGP, USD, SAR...",
    font=("Segoe UI", 12),
    fg_color=BG_INPUT,
    border_color="#334155"
)
currency_entry.pack(pady=(3, 0))

# Category
category_frame = ctk.CTkFrame(row1, fg_color="transparent")
category_frame.pack(side="left", padx=15)
ctk.CTkLabel(category_frame, text="Category *", font=("Segoe UI", 11, "bold"), text_color=TEXT_SECONDARY).pack(anchor="w")
category_box = ctk.CTkComboBox(
    category_frame,
    values=categories,
    width=200,
    font=("Segoe UI", 12),
    fg_color=BG_INPUT,
    border_color="#334155",
    button_color=ACCENT,
    button_hover_color=ACCENT_HOVER
)
category_box.set("Select Category")
category_box.pack(pady=(3, 0))

# Payment
payment_frame = ctk.CTkFrame(row1, fg_color="transparent")
payment_frame.pack(side="left", padx=15)
ctk.CTkLabel(payment_frame, text="Payment Method *", font=("Segoe UI", 11, "bold"), text_color=TEXT_SECONDARY).pack(anchor="w")
payment_box = ctk.CTkComboBox(
    payment_frame,
    values=payments,
    width=180,
    font=("Segoe UI", 12),
    fg_color=BG_INPUT,
    border_color="#334155",
    button_color=ACCENT,
    button_hover_color=ACCENT_HOVER
)
payment_box.set("Select Payment Method")
payment_box.pack(pady=(3, 0))

# Row 2: Dates
row2 = ctk.CTkFrame(input_panel, fg_color="transparent")
row2.pack(pady=(10, 20), padx=20, fill="x")

# Expense Date
date_frame = ctk.CTkFrame(row2, fg_color="transparent")
date_frame.pack(side="left", padx=(0, 15))
ctk.CTkLabel(date_frame, text="Expense Date", font=("Segoe UI", 11, "bold"), text_color=TEXT_SECONDARY).pack(anchor="w")
date_entry = DateEntry(
    date_frame,
    date_pattern="y-mm-dd",
    width=18,
    background=BG_INPUT,
    foreground=TEXT,
    borderwidth=1,
    font=("Segoe UI", 11)
)
date_entry.pack(pady=(3, 0))

# Due Date
due_frame = ctk.CTkFrame(row2, fg_color="transparent")
due_frame.pack(side="left", padx=15)
ctk.CTkLabel(due_frame, text="Due Date", font=("Segoe UI", 11, "bold"), text_color=TEXT_SECONDARY).pack(anchor="w")
due_entry = DateEntry(
    due_frame,
    date_pattern="y-mm-dd",
    width=18,
    background=BG_INPUT,
    foreground=TEXT,
    borderwidth=1,
    font=("Segoe UI", 11)
)
due_entry.pack(pady=(3, 0))

# Currency autocomplete listbox
currency_list = tk.Listbox(
    window,
    height=8,
    bg=BG_PANEL,
    fg=TEXT,
    selectbackground=ACCENT,
    selectforeground="white",
    font=("Segoe UI", 11),
    relief="solid",
    borderwidth=1,
    highlightthickness=0
)
currency_list.bind("<<ListboxSelect>>", select_currency)
currency_list.bind("<Return>", select_currency)
currency_list.bind("<Escape>", hide_currency_list)
currency_entry.bind("<KeyRelease>", show_currency)
currency_entry.bind("<FocusOut>", lambda e: window.after(200, hide_currency_list, None))

# ===== BUTTONS =====
buttons_frame = ctk.CTkFrame(window, fg_color="transparent")
buttons_frame.pack(pady=15)

add_btn = ctk.CTkButton(
    buttons_frame,
    text="Add Expense",
    width=160,
    height=38,
    font=("Segoe UI", 13, "bold"),
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    command=add_expense
)
add_btn.grid(row=0, column=0, padx=8)

update_btn = ctk.CTkButton(
    buttons_frame,
    text="Update Expense",
    width=160,
    height=38,
    font=("Segoe UI", 13, "bold"),
    fg_color=WARNING,
    hover_color="#d97706",
    command=update_expense,
    state="disabled"
)
update_btn.grid(row=0, column=1, padx=8)

delete_btn = ctk.CTkButton(
    buttons_frame,
    text="Delete Expense",
    width=160,
    height=38,
    font=("Segoe UI", 13, "bold"),
    fg_color=ERROR,
    hover_color="#dc2626",
    command=delete_row
)
delete_btn.grid(row=0, column=2, padx=8)

cancel_btn = ctk.CTkButton(
    buttons_frame,
    text="Clear / Cancel",
    width=160,
    height=38,
    font=("Segoe UI", 13, "bold"),
    fg_color="#475569",
    hover_color="#64748b",
    command=clear_inputs,
    state="disabled"
)
cancel_btn.grid(row=0, column=3, padx=8)

# ===== DATA TABLE =====
sheet_frame = ctk.CTkFrame(window, fg_color=BG_PANEL, corner_radius=12)
sheet_frame.pack(padx=20, pady=(0, 10), fill="both", expand=True)

sheet = Sheet(
    sheet_frame,
    headers=["Amount", "Currency", "Amount (EGP)", "Category", "Payment Method", "Date", "Due Date"],
    height=380,
    width=1220,
    header_bg=BG_INPUT,
    header_fg=TEXT,
    index_bg=BG_INPUT,
    index_fg=TEXT_SECONDARY,
    top_left_bg=BG_INPUT
)
sheet.pack(padx=15, pady=15, fill="both", expand=True)
sheet.enable_bindings()
sheet.bind("<<SheetSelect>>", select_row)

# Set column widths
sheet.column_width(column=0, width=100)
sheet.column_width(column=1, width=100)
sheet.column_width(column=2, width=120)
sheet.column_width(column=3, width=180)
sheet.column_width(column=4, width=160)
sheet.column_width(column=5, width=120)
sheet.column_width(column=6, width=120)

# ===== FOOTER =====
footer_frame = ctk.CTkFrame(window, fg_color="transparent")
footer_frame.pack(pady=(0, 15), padx=20, fill="x")

row_count_label = ctk.CTkLabel(
    footer_frame,
    text="Total Expenses: 0",
    font=("Segoe UI", 14, "bold"),
    text_color=TEXT_SECONDARY
)
row_count_label.pack(side="left", padx=20)

total_label = ctk.CTkLabel(
    footer_frame,
    text="Total: 0.00 EGP",
    font=("Segoe UI", 20, "bold"),
    text_color=SUCCESS
)
total_label.pack(side="right", padx=20)

# ===== KEYBOARD SHORTCUTS =====
window.bind("<Control-n>", lambda e: clear_inputs())
window.bind("<Control-s>", lambda e: save_data())
window.bind("<Return>", lambda e: add_expense() if not is_editing else update_expense())
window.bind("<Escape>", lambda e: clear_inputs())
window.bind("<Delete>", lambda e: delete_row())

# ===== INITIALIZE =====
load_data()
amount_entry.focus_set()

window.mainloop()