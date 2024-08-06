import tkinter as tk
from tkinter import filedialog
import pdfplumber
import re

def extract_relevant_lines(text, start_keyword="linkedin.com/in"):
    lines = text.splitlines()
    relevant_lines = []
    capture = False
    
    for i, line in enumerate(lines):
        if re.search(r'\b[A-Z][a-zA-Z]+\b', line):  # Simple regex to match a line with a name
            relevant_lines.append(line.strip())
            capture = True
            continue
        if capture:
            relevant_lines.append(line.strip())
            if len(relevant_lines) >= 5 or start_keyword.lower() in line.lower():
                break
    
    return relevant_lines

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            relevant_lines = extract_relevant_lines(text)
            result_text.delete(1.0, tk.END)
            for line in relevant_lines:
                result_text.insert(tk.END, f"{line}\n")

# Set up the GUI
root = tk.Tk()
root.title("Resume Information Extractor")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

open_button = tk.Button(frame, text="Open PDF", command=open_file)
open_button.pack()

result_text = tk.Text(frame, wrap='word', height=20, width=80)
result_text.pack(pady=10)

root.mainloop()
