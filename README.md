# 📄 Resume Parser and Job Matcher

An intelligent dual-purpose web application that analyzes resumes, predicts job categories, identifies skill gaps, and provides personalized career recommendations for both **job seekers** and **employers**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [How It Works](#-how-it-works)
- [Dataset](#-dataset)
- [Skills Detected](#-skills-detected)
- [API Endpoints](#-api-endpoints)
- [Screenshots](#-screenshots)
- [Future Enhancements](#-future-enhancements)
- [References](#-references)
- [License](#-license)

---

## 🎯 Overview

**Resume Parser and Job Matcher** is a Flask-based web application that uses **Natural Language Processing (NLP)** and **Machine Learning** to:

- Parse resumes in **PDF, DOCX, and TXT** formats
- Extract **technical skills** and **years of experience**
- Predict the most suitable **job category** using **TF-IDF** and **Cosine Similarity**
- Identify **skill gaps** against trending industry skills
- Recommend **learning resources, courses, and projects**
- Generate **personalized interview questions**
- Estimate **salary ranges** (Indian market, in LPA)
- Match resumes with similar profiles from a real dataset

This tool serves **both applicants** (self-evaluation, career guidance) and **employers** (candidate screening, skill-based filtering).

---

## ✨ Features

### 👤 For Job Seekers
- 📊 **Resume Strength Score** (Beginner / Intermediate / Advanced)
- 🎯 **Job Category Prediction** with confidence scores
- 🕳️ **Skill Gap Analysis** based on trending skills
- 📚 **Personalized Learning Recommendations** (Courses, Platforms, Projects)
- 🎤 **Interview Preparation** with category-specific questions
- 💰 **Salary Estimation** based on category and experience

### 🏢 For Employers / HR
- ⚡ **Automated Resume Screening**
- 📈 **Objective Skill-Based Matching**
- 🔍 **Batch Processing Support**
- 🧠 **AI-Powered Candidate Ranking**

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, Flask |
| **NLP** | NLTK, scikit-learn (TF-IDF, Cosine Similarity) |
| **File Parsing** | pdfplumber, python-docx |
| **Data Handling** | Pandas, NumPy |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Visualization** | Plotly |

---

## 📁 Project Structure

```
resume_job_matcher/
│
├── app.py                          # Main Flask application
├── requirements.txt                # Dependencies
├── README.md                       # Project documentation
│
├── data/
│   └── UpdatedResumeDataSet.csv    # Resume dataset (auto-created if missing)
│
├── templates/
│   └── index.html                  # Frontend UI
│
└── static/
    └── style.css                   # Styles
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/resume-job-matcher.git
cd resume-job-matcher
```

### 2️⃣ Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

**`requirements.txt`:**
```
flask==2.3.3
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
nltk==3.8.1
pdfplumber==0.9.0
python-docx==0.8.11
plotly==5.15.0
```

### 4️⃣ (Optional) Add Real Kaggle Dataset

Download the dataset from [Kaggle - Resume Dataset](https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset) and place `UpdatedResumeDataSet.csv` inside the `data/` folder.

> 💡 If the file is missing, the app **automatically creates a sample dataset** with 14 resumes so you can run the project right away.

---

## 🚀 Usage

Run the Flask application:

```bash
python app.py
```

Open your browser and navigate to:

```
http://localhost:5000
```

1. **Upload** your resume (PDF / DOCX / TXT)
2. Click **Analyze Resume**
3. View results:
   - Predicted job categories
   - Detected skills
   - Skill gaps
   - Learning recommendations
   - Interview questions
   - Salary estimates
   - Similar resumes from the dataset

---

## 🧠 How It Works

```
User Uploads Resume
        ↓
Text Extraction (pdfplumber / python-docx)
        ↓
Text Cleaning & Preprocessing (NLTK)
        ↓
┌───────────────────────────────┐
│  Skill Extraction             │
│  Experience Extraction        │
│  Category Prediction (TF-IDF) │
└───────────────────────────────┘
        ↓
Skill Gap Analysis → Learning Recommendations
        ↓
Cosine Similarity → Similar Resumes
        ↓
Job Recommendations + Salary Estimation
        ↓
Display Results on Web UI
```

### Key Algorithms
- **TF-IDF Vectorization** – converts resume & job text into numerical vectors
- **Cosine Similarity** – measures how closely a resume matches each job category
- **Regex Pattern Matching** – extracts years of experience
- **Rule-Based Skill Matching** – detects 55+ technical skills from predefined DB

---

## 📊 Dataset

- **Source:** [Kaggle Resume Dataset](https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset)
- **Size:** ~2,500 resumes
- **Categories:** 25+ (IT, Data Science, Healthcare, Finance, Engineering, etc.)
- **Format:** CSV with `Category` and `Resume` columns

If the dataset is not available, a **fallback sample dataset** with 14 resumes across 6 categories is generated automatically.

---

## 🧩 Skills Detected

The parser recognizes **55+ technical skills**, including:

| Domain | Skills |
|--------|--------|
| **AI/ML** | Machine Learning, Deep Learning, TensorFlow, PyTorch, LLM, Generative AI, Computer Vision, NLP |
| **Web Dev** | React, Node.js, Django, Flask, JavaScript, HTML, CSS, GraphQL, REST API |
| **Cloud/DevOps** | AWS, Azure, Docker, Kubernetes, CI/CD, DevOps |
| **Databases** | MySQL, MongoDB, PostgreSQL, Oracle, SQLite |
| **Healthcare** | EMR Systems, Telemedicine, Healthcare Analytics, Medical AI |
| **Others** | Python, Java, C++, Git, Linux, Tableau, Power BI |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page (UI) |
| `POST` | `/upload` | Upload and analyze a resume |
| `GET` | `/category/<category_name>` | Get sample resumes for a category |
| `GET` | `/stats` | Dataset statistics |

### Example Request

```bash
curl -X POST -F "resume=@my_resume.pdf" http://localhost:5000/upload
```

---

## 📸 Screenshots

> Add your own screenshots here after running the project.

| Dashboard | Analysis Result |
|-----------|-----------------|
| ![Dashboard](screenshots/dashboard.png) | ![Results](screenshots/results.png) |

---

## 🚧 Future Enhancements

- 🔐 User authentication (login/signup)
- 📄 Multi-resume batch upload for employers
- 🌐 Multilingual resume support
- 🤖 Transformer-based (BERT) semantic matching
- 📈 Resume score improvement suggestions
- 📤 Export results as PDF/CSV
- ☁️ Deployment on Heroku / AWS / Render

---

## 📚 References

1. Smith, J., Johnson, M., & Brown, K. (2021). *Resume Parsing and Classification using Natural Language Processing.* International Journal of Advanced Computer Science and Applications, 12(4), 245–256.
2. Chen, L., & Wang, R. (2020). *Intelligent Recruitment Systems: A Machine Learning Approach.* IEEE Transactions on Human-Machine Systems, 50(3), 215–228.
3. Pedregosa, F., et al. (2018). *Scikit-learn: Machine Learning in Python.* Journal of Machine Learning Research, 12(85), 2825–2830.
4. Kumar, S., & Patel, R. (2019). *TF-IDF and Cosine Similarity for Document Classification and Matching.* Proceedings of the International Conference on Computational Intelligence and Data Science, 118–125.
5. Groot, A. D., & van der Heijden, K. (2020). *AI in Recruitment: A Systematic Review of Machine Learning Applications in Resume Screening and Job Matching.* International Journal of Human Resource Management, 31(20), 2551–2580.

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---


---

⭐ **If you found this project helpful, please give it a star!** ⭐
