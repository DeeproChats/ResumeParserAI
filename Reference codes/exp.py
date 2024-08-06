import tkinter as tk
from tkinter import filedialog, Text
import pdfplumber
from transformers import pipeline
import re

# Load Hugging Face NER pipeline
nlp = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_experience_periods(text):
    # Regex pattern to match date ranges (e.g., 2010-2015) and single years
    date_range_pattern = re.compile(r'(\b(?:19|20)\d{2})\D+(\b(?:19|20)\d{2})')
    single_date_pattern = re.compile(r'\b(?:19|20)\d{2}\b')

    periods = []

    # Find date ranges
    for match in date_range_pattern.finditer(text):
        start_year, end_year = match.groups()
        if int(start_year) <= int(end_year):
            periods.append((int(start_year), int(end_year)))

    # Find standalone years and determine their context
    single_years = single_date_pattern.findall(text)
    for year in single_years:
        year = int(year)
        # Check if the year is part of a work experience context
        context_start = max(0, text.find(str(year)) - 50)
        context_end = text.find(str(year)) + 50
        context = text[context_start:context_end].lower()
        if any(keyword in context for keyword in ["worked", "position", "job", "role", "employed", "experience"]):
            periods.append((year, year))

    return periods

def calculate_years_of_experience(text):
    periods = extract_experience_periods(text)

    if not periods:
        return 0

    # Sort periods by start year
    periods.sort(key=lambda x: x[0])

    # Calculate the total years of experience by merging overlapping periods
    total_years = 0
    current_start, current_end = periods[0]

    for start, end in periods[1:]:
        if start <= current_end + 1:  # Allow small gap between jobs
            current_end = max(current_end, end)
        else:  # Non-overlapping period
            total_years += current_end - current_start + 1
            current_start, current_end = start, end

    # Add the last period
    total_years += current_end - current_start + 1

    # Subtract 4 years
    total_years = max(total_years - 4, 0)  # Ensure the result is not negative

    return total_years

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        resume_text = extract_text_from_pdf(file_path)
        years_of_experience = calculate_years_of_experience(resume_text)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Years of Experience: {years_of_experience}")

# Set up Tkinter window
root = tk.Tk()
root.title("Resume Experience Calculator")

canvas = tk.Canvas(root, height=500, width=800, bg="#263D42")
canvas.pack()

frame = tk.Frame(root, bg="white")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

open_file_btn = tk.Button(frame, text="Open Resume", padx=10, pady=5, fg="white", bg="#263D42", command=open_file)
open_file_btn.pack()

result_text = Text(frame, height=10, width=60)
result_text.pack()

root.mainloop()
