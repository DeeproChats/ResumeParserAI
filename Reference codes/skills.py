import tkinter as tk
from tkinter import filedialog, messagebox
import spacy
from pdfminer.high_level import extract_text

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Keywords for skill recommendation
ds_keywords = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit']
web_keywords = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'flask']
android_keywords = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
ios_keywords = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
uiux_keywords = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']

# Function to parse PDF and extract text
def pdf_reader(file):
    return extract_text(file)

# Function to recommend skills based on current skills
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

# Function to upload and process the resume PDF
def upload_resume():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        print("No file selected.")
        return

    # Debugging step: Print file path
    print(f"Selected file: {file_path}")

    try:
        resume_text = pdf_reader(file_path)
        # Debugging step: Print extracted text
        print(f"Extracted text: {resume_text[:1000]}")  # Print first 1000 characters for brevity
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        messagebox.showerror("Error", "Failed to extract text from PDF.")
        return

    try:
        doc = nlp(resume_text)
        # Debugging step: Print entities
        print(f"Entities: {[(ent.text, ent.label_) for ent in doc.ents]}")
    except Exception as e:
        print(f"Error processing text with spaCy: {e}")
        messagebox.showerror("Error", "Failed to process text with spaCy.")
        return

    # Attempt to detect skills from entities (Assuming SKILL label is defined)
    skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
    
    # If no skills are detected using SKILL label, use pattern matching
    if not skills:
        skill_patterns = ds_keywords + web_keywords + android_keywords + ios_keywords + uiux_keywords
        skills = [token.text for token in doc if token.text.lower() in skill_patterns]

    # Remove duplicates
    unique_skills = list(set(skills))

    # Debugging step: Print extracted skills
    print(f"Extracted skills: {unique_skills}")

    skills_text.delete(1.0, tk.END)
    skills_text.insert(tk.END, ', '.join(unique_skills))

# Setting up the Tkinter window
window = tk.Tk()
window.title("Resume Skills Analyzer")
window.geometry("800x600")

upload_button = tk.Button(window, text="Upload Resume PDF", command=upload_resume)
upload_button.pack(pady=10)

skills_label = tk.Label(window, text="Extracted Skills:")
skills_label.pack()
skills_text = tk.Text(window, height=25, width=85)
skills_text.pack()

window.mainloop()
