"""
VA Medication Refill Identifier - GUI Version
Finds medications with Active status, 0 refills left, and a prescription number.
"""

import tkinter as tk
from tkinter import scrolledtext
import os
import re
import shutil
from datetime import datetime

def get_script_dir():
    """Get the directory where this script/exe lives."""
    if getattr(import_module, '_MEIPASS', None):
        # Running as PyInstaller .exe
        return os.path.dirname(os.path.abspath(import_module.executable))
    return os.path.dirname(os.path.abspath(__file__))

# Use sys module for PyInstaller detection
import sys as import_module

SCRIPT_DIR = get_script_dir()
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")


def get_file_datetime(filename):
    """Extract date/time from VA medication filename for sorting."""
    match = re.search(r'(\d{1,2})-(\d{1,2})-(\d{4})_(\d+)(am|pm)', filename)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        year = int(match.group(3))
        time_str = match.group(4).zfill(6)
        ampm = 1 if match.group(5) == 'pm' else 0
        return (year, month, day, ampm, time_str)
    return (0, 0, 0, 0, '')


def is_med_name(line):
    """Check if a line is a medication name (all caps with dosage keywords)."""
    stripped = line.strip()
    if not stripped or len(stripped) <= 3:
        return False
    if stripped != stripped.upper():
        return False

    # Main pattern: digit followed by dosage keyword
    keywords = (r'\d+(MG|MCG|GR|GM|ML|TAB|CAP|IU|UNIT|STRIP|GEL|PATCH|CREAM|'
                r'OINTMENT|LOTION|POWDER|SPRAY|SOLN|INJ|INJECTOR|INJCTR|VIAL|'
                r'PEN|CHEW|DROP|INJECTION|TEST|TOP|INHL|SUBLINGUAL|EC|ER|SR|XR|'
                r'EXTENDED|DELAYED|ORAL|SOLUTION|PACK|PO)')
    if re.search(keywords, stripped):
        return True

    # Also catch Non-VA entries and all-caps lines with CAP/TAB without digit prefix
    if stripped.startswith('NON-VA '):
        return True
    if re.search(r'\b(CAP|TAB)(/|\b)', stripped):
        return True

    return False


def run_meds_filter():
    """Main processing function."""
    status_var.set("Searching for VA medication files...")
    root.update()

    # Find VA medication files in Downloads
    try:
        files = [f for f in os.listdir(DOWNLOADS)
                 if f.startswith("VA-medication") and f.endswith(".txt")]
    except FileNotFoundError:
        status_var.set("Downloads folder not found!")
        status_label.config(fg="#cc0000")
        return

    if not files:
        status_var.set("No VA-medication files found in Downloads folder")
        status_label.config(fg="#cc0000")
        return

    # Sort by date/time in filename, pick newest
    files.sort(key=get_file_datetime, reverse=True)
    input_filename = files[0]
    input_path = os.path.join(DOWNLOADS, input_filename)

    status_var.set(f"Reading: {input_filename} ...")
    root.update()

    # Read file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip header before "All medications"
    if "All medications" in content:
        content = content.split("All medications", 1)[1]

    # Parse medications
    lines = content.split('\n')
    medications = []
    current_med = []

    for line in lines:
        if is_med_name(line):
            if current_med:
                medications.append('\n'.join(current_med))
            current_med = [line]
        else:
            current_med.append(line)

    if current_med:
        medications.append('\n'.join(current_med))

    status_var.set(f"Found {len(medications)} total medications. Filtering...")
    root.update()

    # Filter: Active + Refills left: 0 + has Prescription number + NOT Refill in Process
    filtered = []
    for med in medications:
        has_active = "Status: Active" in med
        has_no_refills = "Refills left: 0" in med
        has_refill_in_process = "Refill in Process" in med
        has_rx_number = "Prescription number:" in med

        if has_active and has_no_refills and not has_refill_in_process and has_rx_number:
            filtered.append(med.strip())

    # Build result - clean up blank lines within each med
    result_lines = []
    for i, med in enumerate(filtered):
        clean_lines = [l for l in med.split('\n') if l.strip()]
        if i > 0:
            result_lines.append('')
        result_lines.extend(clean_lines)

    result_text = '\n'.join(result_lines)

    # Save to file
    output_path = os.path.join(SCRIPT_DIR, "MedsToOrder.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result_text)

    # Archive processed file
    archive_folder = os.path.join(DOWNLOADS, "VA_Meds_Archive")
    os.makedirs(archive_folder, exist_ok=True)
    try:
        shutil.move(input_path, os.path.join(archive_folder, input_filename))
    except Exception:
        pass

    # Log (keep only last 3 entries)
    log_path = os.path.join(SCRIPT_DIR, "MedsToOrder_Log.txt")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_entry = f"[{timestamp}] {input_filename} - {len(filtered)} meds"
    existing = []
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            existing = [l.strip() for l in f.readlines() if l.strip()]
    existing.append(new_entry)
    existing = existing[-3:]  # keep only last 3
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(existing) + '\n')

    # Update UI
    if not filtered:
        status_var.set("No medications need refills right now. File processed and archived.")
        status_label.config(fg="#4c9900")
        results_label.config(text="")
        results_box.config(state='normal')
        results_box.delete('1.0', tk.END)
        results_box.config(state='disabled')
        open_btn.pack_forget()
    else:
        status_var.set(f"Found {len(filtered)} medication(s) needing refills. Saved to MedsToOrder.txt")
        status_label.config(fg="#4c9900")
        results_label.config(text=f"Medications Needing Refills ({len(filtered)}):")
        results_box.config(state='normal')
        results_box.delete('1.0', tk.END)
        results_box.insert('1.0', result_text)
        results_box.config(state='disabled')
        open_btn.pack(side='left', padx=(10, 0))

    log_var.set(f"Processed: {input_filename} | Archived to Downloads\\VA_Meds_Archive\\")


def on_run_click():
    """Handle Run button click."""
    run_btn.config(state='disabled', text='Processing...')
    open_btn.pack_forget()
    root.update()
    try:
        run_meds_filter()
    except Exception as e:
        status_var.set(f"Error: {e}")
        status_label.config(fg="#cc0000")
    run_btn.config(state='normal', text='Find Medications to Reorder')


def on_open_click():
    """Open MedsToOrder.txt in Notepad."""
    output_path = os.path.join(SCRIPT_DIR, "MedsToOrder.txt")
    if os.path.exists(output_path):
        os.startfile(output_path)


# ============================================================
# BUILD GUI
# ============================================================

root = tk.Tk()
root.title("VA Medication Refill Identifier")
root.geometry("700x600")
root.resizable(False, False)
root.configure(bg='#f5f5f5')

# Title
title_frame = tk.Frame(root, bg='#f5f5f5')
title_frame.pack(fill='x', padx=20, pady=(15, 0))

title_label = tk.Label(title_frame, text="VA Medication Refill Identifier",
                       font=('Segoe UI', 16, 'bold'), fg='#003366', bg='#f5f5f5')
title_label.pack(anchor='w')

subtitle_label = tk.Label(title_frame,
                          text="Finds medications with Active status, 0 refills left, and a prescription number",
                          font=('Segoe UI', 9), fg='gray', bg='#f5f5f5')
subtitle_label.pack(anchor='w', pady=(2, 0))

# Separator
sep = tk.Frame(root, height=2, bg='#cccccc')
sep.pack(fill='x', padx=20, pady=(10, 10))

# Buttons row
btn_frame = tk.Frame(root, bg='#f5f5f5')
btn_frame.pack(fill='x', padx=20)

run_btn = tk.Button(btn_frame, text='Find Medications to Reorder',
                    font=('Segoe UI', 12, 'bold'), fg='white', bg='#006699',
                    activebackground='#005580', activeforeground='white',
                    relief='flat', padx=20, pady=8, cursor='hand2',
                    command=on_run_click)
run_btn.pack(side='left')

open_btn = tk.Button(btn_frame, text='Open Results File',
                     font=('Segoe UI', 10), fg='white', bg='#4c9900',
                     activebackground='#3d7a00', activeforeground='white',
                     relief='flat', padx=15, pady=8, cursor='hand2',
                     command=on_open_click)
# open_btn starts hidden, packed when results are found

close_btn = tk.Button(btn_frame, text='Exit',
                      font=('Segoe UI', 10, 'bold'), fg='white', bg='#cc3333',
                      activebackground='#aa2222', activeforeground='white',
                      relief='flat', padx=15, pady=8, cursor='hand2',
                      command=root.destroy)
close_btn.pack(side='right')

# Status
status_var = tk.StringVar(value="Ready — click the button to start")
status_label = tk.Label(root, textvariable=status_var, font=('Segoe UI', 10),
                        fg='#003366', bg='#f5f5f5', anchor='w')
status_label.pack(fill='x', padx=22, pady=(10, 5))

# Results label
results_label = tk.Label(root, text="", font=('Segoe UI', 10, 'bold'),
                         fg='#003366', bg='#f5f5f5', anchor='w')
results_label.pack(fill='x', padx=20)

# Results text box
results_box = scrolledtext.ScrolledText(root, font=('Consolas', 9),
                                         width=80, height=18, wrap='word',
                                         state='disabled', bg='white',
                                         relief='solid', borderwidth=1)
results_box.pack(fill='both', padx=20, pady=(5, 5), expand=True)

# Log label at bottom
log_var = tk.StringVar()
log_label = tk.Label(root, textvariable=log_var, font=('Segoe UI', 8),
                     fg='gray', bg='#f5f5f5', anchor='w')
log_label.pack(fill='x', padx=22, pady=(0, 10))

# Run the app
root.mainloop()
