import tkinter as tk
from tkinter import filedialog, Text
import pdfplumber
import re
import json
import spacy  # Ensure spacy is installed

# Load the spaCy model
nlp_spacy = spacy.load("en_core_web_sm")

# Keywords for skill recommendation
ds_keywords = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit']
web_keywords = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'flask']
android_keywords = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
ios_keywords = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
uiux_keywords = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']

def extract_relevant_lines(text):
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
            if len(relevant_lines) >= 5 or "linkedin.com/in" in line.lower():
                break
    
    return relevant_lines

def extract_education_text(file_path):
    education_text = ""
    found_education = False
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
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

def extract_education_text_with_limit(file_path):
    education_text = ""
    found_education = False
    year_count = 0
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    if 'Education' in line:
                        found_education = True
                        education_text += "Education:\n"
                        continue
                    if found_education:
                        if 'Technical Skills' in line or 'Technical skills' in line or year_count >= 2:
                            found_education = False
                            break
                        education_text += line + '\n'
                        year_count += len(re.findall(r'\b(?:19|20)\d{2}\b', line))
    return education_text.strip()

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_experience_periods(text):
    date_range_pattern = re.compile(r'(\b(?:19|20)\d{2})\D+(\b(?:19|20)\d{2})')
    single_date_pattern = re.compile(r'\b(?:19|20)\d{2}\b')
    periods = []
    
    for match in date_range_pattern.finditer(text):
        start_year, end_year = match.groups()
        if int(start_year) <= int(end_year):
            periods.append((int(start_year), int(end_year)))
    
    single_years = single_date_pattern.findall(text)
    for year in single_years:
        year = int(year)
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
    
    periods.sort(key=lambda x: x[0])
    total_years = 0
    current_start, current_end = periods[0]
    
    for start, end in periods[1:]:
        if start <= current_end + 1:
            current_end = max(current_end, end)
        else:
            total_years += current_end - current_start + 1
            current_start, current_end = start, end
    
    total_years += current_end - current_start + 1
    total_years = max(total_years - 4, 0)
    
    return total_years

def recommend_skills(skills):
    recommendations = {
        'Data Science': ds_keywords,
        'Web Development': web_keywords,
        'Android Development': android_keywords,
        'IOS Development': ios_keywords,
        'UI-UX Development': uiux_keywords
    }

    recommended_skills = []
    field = ''

    for skill in skills:
        skill_lower = skill.lower()
        for category, keywords in recommendations.items():
            if skill_lower in keywords:
                field = category
                recommended_skills = keywords
                break
        if recommended_skills:
            break

    return field, recommended_skills

def extract_technical_skills(education_text):
    technical_skills = {}
    
    if 'TechnicalSkills:' in education_text:
        tech_skills_text = education_text.split('TechnicalSkills:')[1].strip()
        skills_list = tech_skills_text.split('\n\u25cf ')
        
        for skill in skills_list:
            if 'Operatingsystems:' in skill:
                technical_skills['Operating systems'] = skill.split('Operatingsystems:')[1].strip()
            elif 'Languages:' in skill:
                technical_skills['Languages'] = skill.split('Languages:')[1].strip()
            elif 'Scriptinglanguages:' in skill:
                technical_skills['Scripting languages'] = skill.split('Scriptinglanguages:')[1].strip()
            elif 'AnalyticsTools:' in skill:
                technical_skills['Analytics Tools'] = skill.split('AnalyticsTools:')[1].strip()
            elif 'Methodologies&tools:' in skill:
                technical_skills['Methodologies & tools'] = skill.split('Methodologies&tools:')[1].strip()
    
    return technical_skills

def generate_json_output(file_path):
    resume_text = extract_text_from_pdf(file_path)
    education_text = extract_education_text(file_path)
    technical_skills = extract_technical_skills(education_text)
    relevant_lines = extract_relevant_lines(resume_text)
    years_of_experience = calculate_years_of_experience(resume_text)
    
    doc_spacy = nlp_spacy(resume_text)
    skills = [ent.text for ent in doc_spacy.ents if ent.label_ == "SKILL"]
    if not skills:
        skill_patterns = ds_keywords + web_keywords + android_keywords + ios_keywords + uiux_keywords
        skills = [token.text for token in doc_spacy if token.text.lower() in skill_patterns]
    unique_skills = list(set(skills))
    
    json_output = {
        "years_of_experience": years_of_experience,
        "relevant_information": relevant_lines,
        "technical_skills": technical_skills,
        "skills": {
            "extracted_skills": unique_skills
        }
    }

    return json.dumps(json_output, indent=4)

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        resume_text = extract_text_from_pdf(file_path)
        limited_education_text = extract_education_text_with_limit(file_path)
        limited_education_text = limited_education_text.replace("Education:\n", "", 1)  # Remove extra "Education:" label
        json_output = generate_json_output(file_path)

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Education:\n" + limited_education_text + "\n\n")
        result_text.insert(tk.END, json_output)

root = tk.Tk()
root.title("Resume Information Extractor")

canvas = tk.Canvas(root, height=600, width=600, bg="#263D42")
canvas.pack()

frame = tk.Frame(root, bg="white")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

open_file_button = tk.Button(root, text="Open PDF File", padx=10, pady=5, fg="white", bg="#263D42", command=open_file)
open_file_button.pack()

result_text = Text(frame, wrap=tk.WORD, bg="white", fg="black")
result_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

root.mainloop()
