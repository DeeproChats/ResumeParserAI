import tkinter as tk
from tkinter import filedialog, Text, Scrollbar, VERTICAL, RIGHT, Y
import pdfplumber

def extract_education_text(file_path):
    education_text = ""
    found_education = False
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'Education' in line:
                        found_education = True
                        education_text += "Education:\n"
                        continue
                    if found_education:
                        if 'Technical Skills' in line or 'Technical skills' in line:
                            found_education = False
                            break
                        education_text += line + '\n'
    return education_text.strip()

def open_file():
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=(("PDF files", "*.pdf"), ("all files", "*.*"))
    )
    if file_path:
        education_text = extract_education_text(file_path)
        result_textbox.delete(1.0, tk.END)
        result_textbox.insert(tk.END, education_text)

root = tk.Tk()
root.title("PDF Education Extractor")

# Set window size and background color
root.geometry("800x600")
root.configure(bg="lightblue")

frame = tk.Frame(root, bg="white", bd=5)
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

open_file_button = tk.Button(root, text="Open PDF File", padx=10, pady=5, fg="white", bg="blue", command=open_file)
open_file_button.pack(pady=20)

scrollbar = Scrollbar(frame, orient=VERTICAL)
scrollbar.pack(side=RIGHT, fill=Y)

result_textbox = Text(frame, wrap='word', yscrollcommand=scrollbar.set, bg="lightgrey", fg="black", font=("Arial", 12))
result_textbox.pack(expand=True, fill='both')
scrollbar.config(command=result_textbox.yview)

root.mainloop()
