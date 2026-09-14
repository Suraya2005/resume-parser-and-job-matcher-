from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import numpy as np
import pdfplumber
import docx
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import os
import string
import plotly
import plotly.express as px
import json
import io
from datetime import datetime

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

app = Flask(__name__)
app.secret_key = 'resume-parser-secret-key'

# Enhanced skills database with trending skills and interview questions
TRENDING_SKILLS = {
    'Data-Science': [
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 
        'LLM', 'Generative AI', 'Computer Vision', 'NLP', 'MLOps',
        'Big Data', 'Data Engineering', 'Cloud AI', 'System Design',
        'Healthcare Analytics', 'Medical AI'
    ],
    'Information-Technology': [
        'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes', 'Microservices',
        'GraphQL', 'Serverless', 'CI/CD', 'DevOps', 'TypeScript', 'Next.js',
        'System Design', 'Cloud Computing', 'Microservices Architecture',
        'EMR Systems', 'Healthcare IT'
    ],
    'Engineering': [
        'System Design', 'Cloud Architecture', 'Microservices', 'API Design',
        'Performance Optimization', 'Security', 'Scalability', 'Agile',
        'Cloud Computing', 'Distributed Systems', 'Containerization',
        'GraphQL', 'TensorFlow', 'PyTorch', 'Computer Vision'
    ],
    'Business-Development': [
        'Digital Marketing', 'SEO', 'Growth Hacking', 'Data Analytics',
        'CRM', 'Salesforce', 'Market Research', 'Strategic Planning',
        'Telemedicine', 'Healthcare Analytics', 'EMR Systems'
    ],
    'Finance': [
        'Financial Modeling', 'Risk Management', 'Blockchain', 'FinTech',
        'Data Analysis', 'Python for Finance', 'Quantitative Analysis',
        'Healthcare Finance', 'Medical Billing Systems'
    ],
    'Healthcare': [
        'Healthcare Analytics', 'Telemedicine', 'EMR Systems', 'Data Privacy',
        'Medical AI', 'Healthcare IT', 'Regulatory Compliance',
        'LLM', 'Generative AI', 'Computer Vision', 'Clinical Data Analysis',
        'Patient Monitoring Systems', 'Healthcare Data Security',
        'TensorFlow', 'PyTorch'
    ]
}

INTERVIEW_QUESTIONS = {
    'Data-Science': [
        "Explain the bias-variance tradeoff in machine learning",
        "How would you handle missing data in a dataset?",
        "What's the difference between supervised and unsupervised learning?",
        "How do you evaluate a machine learning model?",
        "Explain cross-validation and why it's important",
        "How would you apply LLMs in healthcare data analysis?",
        "What are the ethical considerations when using Generative AI in medical applications?"
    ],
    'Information-Technology': [
        "Explain the difference between REST and GraphQL APIs",
        "How do you ensure application security?",
        "What's your experience with cloud platforms like AWS/Azure?",
        "How do you handle database optimization?",
        "Explain microservices architecture and its benefits",
        "How would you design an EMR system for scalability?",
        "What security measures are crucial for healthcare applications?"
    ],
    'Engineering': [
        "Describe your experience with system design",
        "How do you design a scalable web application?",
        "Explain microservices vs monolithic architecture",
        "What cloud computing platforms have you worked with?",
        "How do you handle system reliability and monitoring?",
        "How would you implement computer vision for medical imaging?",
        "What's your experience with TensorFlow vs PyTorch for healthcare applications?"
    ],
    'Business-Development': [
        "How do you identify new market opportunities?",
        "Describe your sales process",
        "How do you build relationships with clients?",
        "What metrics do you track for business growth?",
        "How do you handle competitor analysis?",
        "How would you approach telemedicine market expansion?",
        "What's your experience with healthcare technology sales?"
    ],
    'Finance': [
        "Explain financial modeling techniques",
        "How do you assess investment risks?",
        "What's your experience with financial analysis tools?",
        "How do you stay updated with market trends?",
        "Describe your experience with budgeting and forecasting",
        "How would you analyze healthcare investment opportunities?",
        "What's your experience with medical billing systems?"
    ],
    'Healthcare': [
        "How do you ensure patient data privacy and security?",
        "What's your experience with healthcare regulations?",
        "How do you handle healthcare data analysis?",
        "Describe your experience with medical software systems",
        "How do you stay updated with healthcare technology trends?",
        "How would you implement AI in clinical decision support?",
        "What's your experience with telemedicine platforms?"
    ]
}

LEARNING_RESOURCES = {
    'Healthcare Analysis': {
        'courses': [
            {'name': 'Healthcare Data Analytics Specialization', 'type': 'Paid', 'link': 'https://www.coursera.org/specializations/healthcare-data-analytics'},
            {'name': 'Health Data Science - Harvard Online', 'type': 'Paid', 'link': 'https://online-learning.harvard.edu/course/health-data-science'},
            {'name': 'Healthcare Analytics Course - edX', 'type': 'Free Audit / Paid Certificate', 'link': 'https://www.edx.org/learn/healthcare-analytics'}
        ],
        'platforms': ['Healthcare Analytics Association', 'Health Data Management', 'Journal of Healthcare Informatics'],
        'projects': ['Analyze patient readmission rates', 'Build healthcare dashboard', 'Predict disease outbreaks']
    },
    'Telemedicine': {
        'courses': [
            {'name': 'Telehealth Fundamentals - AMA', 'type': 'Free', 'link': 'https://www.ama-assn.org/practice-management/digital/telehealth-fundamentals'},
            {'name': 'Digital Health Specialization', 'type': 'Paid', 'link': 'https://www.coursera.org/specializations/digital-health'},
            {'name': 'Telemedicine Implementation Guide', 'type': 'Free', 'link': 'https://www.hrsa.gov/rural-health/telehealth'}
        ],
        'platforms': ['Telemedicine and e-Health Journal', 'mHealth Intelligence', 'Telehealth Technology Association'],
        'projects': ['Design telemedicine app prototype', 'Telehealth workflow analysis', 'Remote patient monitoring system']
    },
    'EMR Systems': {
        'courses': [
            {'name': 'EMR Implementation Specialist Training', 'type': 'Paid', 'link': 'https://www.healthit.gov/training'},
            {'name': 'Electronic Health Records Course', 'type': 'Free', 'link': 'https://www.coursera.org/learn/electronic-health-records'},
            {'name': 'Healthcare Information Systems', 'type': 'Paid', 'link': 'https://www.udemy.com/course/healthcare-information-systems/'}
        ],
        'platforms': ['HL7 International', 'Epic UserWeb', 'Cerner Developer Portal'],
        'projects': ['EMR data migration plan', 'Interoperability solution design', 'EMR customization for clinic']
    },
    'LLM': {
        'courses': [
            {'name': 'Large Language Models Specialization', 'type': 'Paid', 'link': 'https://www.coursera.org/specializations/large-language-models'},
            {'name': 'LLM Fine-tuning Course - Hugging Face', 'type': 'Free', 'link': 'https://huggingface.co/learn/cookbook'},
            {'name': 'Advanced NLP with Transformers', 'type': 'Free', 'link': 'https://www.youtube.com/playlist?list=PLoROMvodv4rOhcuXMZkNm7j3fVwBBY42z'}
        ],
        'platforms': ['Hugging Face', 'OpenAI Cookbook', 'LangChain Documentation'],
        'projects': ['Fine-tune LLM for medical Q&A', 'Build chatbot with RAG', 'Text summarization system']
    },
    'Generative AI': {
        'courses': [
            {'name': 'Generative AI with LLMs - Coursera', 'type': 'Paid', 'link': 'https://www.coursera.org/learn/generative-ai-with-llms'},
            {'name': 'Google Generative AI Learning Path', 'type': 'Free', 'link': 'https://www.cloudskillsboost.google/paths/118'},
            {'name': 'Generative AI for Everyone - DeepLearning.AI', 'type': 'Free', 'link': 'https://www.coursera.org/learn/generative-ai-for-everyone'}
        ],
        'platforms': ['Stable Diffusion GitHub', 'DALL-E API Docs', 'Midjourney Community'],
        'projects': ['Generate medical images', 'Create synthetic patient data', 'AI-powered content creation']
    },
    'Computer Vision': {
        'courses': [
            {'name': 'Computer Vision Specialization - Coursera', 'type': 'Paid', 'link': 'https://www.coursera.org/specializations/computer-vision'},
            {'name': 'OpenCV Official Courses', 'type': 'Free', 'link': 'https://opencv.org/courses/'},
            {'name': 'Practical Computer Vision', 'type': 'Free', 'link': 'https://www.youtube.com/playlist?list=PL5-TkQAfAZFbzxjBHtzdVCWE0Zbhomg7r'}
        ],
        'platforms': ['OpenCV Documentation', 'PyImageSearch', 'CVPR Conference Papers'],
        'projects': ['Medical image classification', 'Object detection in X-rays', 'Facial recognition system']
    },
    'GraphQL': {
        'courses': [
            {'name': 'GraphQL Official Tutorial', 'type': 'Free', 'link': 'https://graphql.org/learn/'},
            {'name': 'Fullstack GraphQL Tutorial', 'type': 'Free', 'link': 'https://www.howtographql.com/'},
            {'name': 'GraphQL with React Course', 'type': 'Paid', 'link': 'https://www.udemy.com/course/graphql-with-react-course/'}
        ],
        'platforms': ['GraphQL Weekly', 'Apollo GraphQL Docs', 'Prisma Documentation'],
        'projects': ['Build GraphQL API for healthcare app', 'Migrate REST to GraphQL', 'Real-time data subscriptions']
    },
    'TensorFlow': {
        'courses': [
            {'name': 'TensorFlow Developer Certificate', 'type': 'Paid', 'link': 'https://www.tensorflow.org/certificate'},
            {'name': 'TensorFlow Official Tutorials', 'type': 'Free', 'link': 'https://www.tensorflow.org/tutorials'},
            {'name': 'Deep Learning with TensorFlow', 'type': 'Free Audit / Paid Certificate', 'link': 'https://www.coursera.org/learn/introduction-tensorflow'}
        ],
        'platforms': ['TensorFlow Hub', 'TFX Documentation', 'TensorFlow Blog'],
        'projects': ['Medical image analysis with CNNs', 'Time series prediction', 'Neural network deployment']
    },
    'PyTorch': {
        'courses': [
            {'name': 'PyTorch Official Tutorials', 'type': 'Free', 'link': 'https://pytorch.org/tutorials/'},
            {'name': 'Deep Learning with PyTorch', 'type': 'Free', 'link': 'https://www.learnpytorch.io/'},
            {'name': 'PyTorch for Deep Learning', 'type': 'Free', 'link': 'https://www.youtube.com/playlist?list=PLZbbT5o_s2xrfNyHZsM6ufI0iZENK9xgG'}
        ],
        'platforms': ['PyTorch Forums', 'Papers With Code', 'PyTorch Lightning'],
        'projects': ['Build custom neural networks', 'Research paper implementation', 'Production ML pipeline']
    },
    'System Design': {
        'courses': [
            {'name': 'Grokking the System Design Interview', 'type': 'Paid', 'link': 'https://www.educative.io/courses/grokking-the-system-design-interview'},
            {'name': 'System Design Primer - GitHub', 'type': 'Free', 'link': 'https://github.com/donnemartin/system-design-primer'},
            {'name': 'System Design Course by Gaurav Sen', 'type': 'Free', 'link': 'https://www.youtube.com/playlist?list=PLMCXHnjXnTnvo6alSjVkgxV-VH6EPyvoX'}
        ],
        'platforms': ['System Design Interview', 'High Scalability', 'Architecture Notes'],
        'projects': ['Design Twitter', 'Design URL Shortener', 'Design Netflix']
    },
    'Cloud Computing': {
        'courses': [
            {'name': 'AWS Cloud Practitioner Essentials', 'type': 'Free', 'link': 'https://www.aws.training/Details/Curriculum?id=27076'},
            {'name': 'Microsoft Azure Fundamentals', 'type': 'Free', 'link': 'https://docs.microsoft.com/en-us/learn/certifications/azure-fundamentals/'},
            {'name': 'Google Cloud Digital Leader', 'type': 'Free', 'link': 'https://cloud.google.com/training/digital-leader'}
        ],
        'platforms': ['AWS Documentation', 'Azure Docs', 'Google Cloud Docs'],
        'projects': ['Deploy web app on EC2', 'Setup cloud storage', 'Create serverless function']
    },
    'Microservices': {
        'courses': [
            {'name': 'Microservices by Martin Fowler', 'type': 'Free', 'link': 'https://martinfowler.com/microservices/'},
            {'name': 'Microservices with Spring Boot', 'type': 'Free', 'link': 'https://spring.io/guides/gs/microservices/'},
            {'name': 'Microservices Architecture Course', 'type': 'Free', 'link': 'https://www.nginx.com/resources/library/microservices-reference-architecture/'}
        ],
        'platforms': ['Microservices.io', 'Docker Docs', 'Kubernetes Docs'],
        'projects': ['Build microservices app', 'Containerize services', 'Setup service discovery']
    },
    'Machine Learning': {
        'courses': [
            {'name': 'Machine Learning by Andrew Ng (Coursera)', 'type': 'Free Audit / Paid Certificate', 'link': 'https://www.coursera.org/learn/machine-learning'},
            {'name': 'Google Machine Learning Crash Course', 'type': 'Free', 'link': 'https://developers.google.com/machine-learning/crash-course'},
            {'name': 'Fast.ai Practical Deep Learning', 'type': 'Free', 'link': 'https://course.fast.ai/'}
        ],
        'platforms': ['Kaggle Learn', 'Towards Data Science', 'Machine Learning YouTube'],
        'projects': ['Build a recommendation system', 'Image classification project', 'Predict housing prices']
    },
    'Deep Learning': {
        'courses': [
            {'name': 'Deep Learning Specialization (Coursera)', 'type': 'Free Audit / Paid Certificate', 'link': 'https://www.coursera.org/specializations/deep-learning'},
            {'name': 'PyTorch Official Tutorials', 'type': 'Free', 'link': 'https://pytorch.org/tutorials/'},
            {'name': 'TensorFlow Developer Certificate', 'type': 'Paid', 'link': 'https://www.tensorflow.org/certificate'}
        ],
        'platforms': ['Papers With Code', 'AI GitHub repositories', 'PyTorch Forum'],
        'projects': ['Neural network from scratch', 'CNN for image recognition', 'Text generation with RNN']
    },
    'React': {
        'courses': [
            {'name': 'React Official Documentation', 'type': 'Free', 'link': 'https://reactjs.org/docs/getting-started.html'},
            {'name': 'Full Stack Open', 'type': 'Free', 'link': 'https://fullstackopen.com/en/'},
            {'name': 'React - The Complete Guide (Udemy)', 'type': 'Paid', 'link': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/'}
        ],
        'platforms': ['React GitHub repos', 'DEV Community', 'React Patterns'],
        'projects': ['Build a portfolio website', 'Create a React component library', 'E-commerce frontend']
    },
    'AWS': {
        'courses': [
            {'name': 'AWS Certified Solutions Architect', 'type': 'Paid', 'link': 'https://aws.amazon.com/certification/certified-solutions-architect-associate/'},
            {'name': 'AWS Training and Certification', 'type': 'Free', 'link': 'https://aws.amazon.com/training/'},
            {'name': 'AWS Cloud Practitioner Essentials', 'type': 'Free', 'link': 'https://www.aws.training/Details/eLearning?id=60697'}
        ],
        'platforms': ['AWS Documentation', 'Cloud Guru', 'AWS YouTube Channel'],
        'projects': ['Deploy a web app on EC2', 'Build serverless API with Lambda', 'Setup S3 bucket for storage']
    },
    'Data Analysis': {
        'courses': [
            {'name': 'Data Analysis with Python (freeCodeCamp)', 'type': 'Free', 'link': 'https://www.freecodecamp.org/learn/data-analysis-with-python/'},
            {'name': 'Google Data Analytics Professional Certificate', 'type': 'Paid', 'link': 'https://www.coursera.org/professional-certificates/google-data-analytics'},
            {'name': 'Python for Data Science (Udacity)', 'type': 'Free', 'link': 'https://www.udacity.com/course/python-for-data-science--ud1111'}
        ],
        'platforms': ['Mode Analytics', 'DataCamp', 'Kaggle Notebooks'],
        'projects': ['Analyze a dataset', 'Build a dashboard', 'Data cleaning project']
    },
    'Python': {
        'courses': [
            {'name': 'Python for Everybody (Coursera)', 'type': 'Free Audit / Paid Certificate', 'link': 'https://www.coursera.org/specializations/python'},
            {'name': 'Real Python Tutorials', 'type': 'Free', 'link': 'https://realpython.com/'},
            {'name': 'Automate the Boring Stuff with Python', 'type': 'Free', 'link': 'https://automatetheboringstuff.com/'}
        ],
        'platforms': ['Python.org', 'Stack Overflow', 'PyPI Documentation'],
        'projects': ['Build a web scraper', 'Create a data analysis script', 'Automate file management']
    },
    'Docker': {
        'courses': [
            {'name': 'Docker Getting Started', 'type': 'Free', 'link': 'https://docs.docker.com/get-started/'},
            {'name': 'Docker Mastery (Udemy)', 'type': 'Paid', 'link': 'https://www.udemy.com/course/docker-mastery/'},
            {'name': 'Docker and Kubernetes: The Complete Guide', 'type': 'Paid', 'link': 'https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/'}
        ],
        'platforms': ['Docker Documentation', 'Docker Hub', 'Docker Community'],
        'projects': ['Containerize a web application', 'Multi-container app with Docker Compose', 'Dockerize database']
    },
    'JavaScript': {
        'courses': [
            {'name': 'JavaScript Algorithms and Data Structures (freeCodeCamp)', 'type': 'Free', 'link': 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/'},
            {'name': 'The Complete JavaScript Course (Udemy)', 'type': 'Paid', 'link': 'https://www.udemy.com/course/the-complete-javascript-course/'},
            {'name': 'MDN JavaScript Guide', 'type': 'Free', 'link': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide'}
        ],
        'platforms': ['JavaScript.info', 'Stack Overflow', 'GitHub JavaScript Projects'],
        'projects': ['Build a calculator app', 'Create a weather app', 'Interactive portfolio website']
    },
    'SQL': {
        'courses': [
            {'name': 'SQL for Data Science (Coursera)', 'type': 'Free Audit / Paid Certificate', 'link': 'https://www.coursera.org/learn/sql-for-data-science'},
            {'name': 'SQL Bolt Interactive Tutorial', 'type': 'Free', 'link': 'https://sqlbolt.com/'},
            {'name': 'The Complete SQL Bootcamp (Udemy)', 'type': 'Paid', 'link': 'https://www.udemy.com/course/the-complete-sql-bootcamp/'}
        ],
        'platforms': ['Mode SQL Tutorial', 'W3Schools SQL', 'SQLZoo'],
        'projects': ['Database design for library system', 'E-commerce queries', 'Data analysis with complex queries']
    },
    'Node.js': {
        'courses': [
            {'name': 'Node.js Official Documentation', 'type': 'Free', 'link': 'https://nodejs.org/docs/latest/api/'},
            {'name': 'The Complete Node.js Developer Course (Udemy)', 'type': 'Paid', 'link': 'https://www.udemy.com/course/the-complete-nodejs-developer-course-2/'},
            {'name': 'Express.js Guide', 'type': 'Free', 'link': 'https://expressjs.com/en/guide/routing.html'}
        ],
        'platforms': ['Node.js GitHub', 'NPM Documentation', 'Stack Overflow Node.js'],
        'projects': ['Build REST API', 'Real-time chat application', 'Authentication system']
    }
}

def create_sample_dataset():
    """Create sample dataset if not exists"""
    sample_data = {
        'Category': [
            'Information-Technology', 'Information-Technology', 'Information-Technology',
            'Data-Science', 'Data-Science', 'Data-Science', 
            'Business-Development', 'Business-Development',
            'Healthcare', 'Healthcare',
            'Finance', 'Finance',
            'Engineering', 'Engineering'
        ],
        'Resume': [
            "Python developer with 3 years experience in web development using Django Flask and REST APIs. Skills include JavaScript HTML CSS MySQL and MongoDB. Strong problem-solving abilities and team collaboration. Experience with GraphQL and microservices architecture.",
            "Java Developer with 5 years experience in enterprise applications. Skills include Spring Boot Hibernate Microservices AWS and Docker. Team leadership experience and agile methodology. Knowledge of system design and cloud computing.",
            "Full Stack Developer with 4 years experience in JavaScript React Node.js and Python. Expertise in web development database management and cloud platforms. Strong in algorithms and data structures. Experience with TensorFlow and computer vision projects.",
            "Data Scientist with 4 years experience in machine learning and statistical analysis. Proficient in Python R TensorFlow and pandas. Experience with data visualization using Tableau and Power BI. Specialized in healthcare analytics and LLM applications.",
            "Machine Learning Engineer with 3 years experience in deep learning and neural networks. Proficient in PyTorch Keras and computer vision. Masters in AI and data processing. Experience with generative AI and medical imaging analysis.",
            "Data Analyst with 2 years experience in data processing and visualization. Skills include SQL Excel Python and statistical analysis. Strong analytical and communication skills. Experience with healthcare data analysis and EMR systems.",
            "Business Analyst with 5 years experience in market research and strategy development. Skilled in Excel SQL and data analysis. Strong communication and presentation skills. Experience in telemedicine business development.",
            "Project Manager with 7 years experience in IT projects. Skilled in Agile Scrum JIRA and team management. PMP certified with strong leadership skills. Experience managing healthcare IT implementations.",
            "Healthcare Analyst with 6 years experience in healthcare data analysis and patient care systems. Knowledge of medical databases and healthcare regulations. Experience with EMR systems and telemedicine platforms.",
            "Medical Researcher with 4 years experience in clinical trials and data analysis. Proficient in statistical analysis and research methodology. Experience with healthcare analytics and medical AI applications.",
            "Financial Analyst with 3 years experience in financial modeling and risk assessment. Proficient in Excel VBA and financial software. Experience with healthcare finance and medical billing systems.",
            "Investment Banker with 5 years experience in financial markets and portfolio management. Strong analytical skills and market knowledge. Experience in healthcare investments and telemedicine startups.",
            "Software Engineer with 4 years experience in full-stack development. Expertise in Java Python JavaScript React and Node.js. Experience with system design microservices and GraphQL APIs.",
            "DevOps Engineer with 3 years experience in cloud infrastructure and CI/CD pipelines. Skills include AWS Docker Kubernetes and Jenkins. Experience with healthcare cloud solutions and data security."
        ]
    }
    df = pd.DataFrame(sample_data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/UpdatedResumeDataSet.csv', index=False)
    print("✅ Sample dataset created with 14 resumes")
    return df

class ResumeDataset:
    def __init__(self, csv_path):
        if not os.path.exists(csv_path):
            print("📝 Creating sample dataset...")
            self.df = create_sample_dataset()
        else:
            self.df = pd.read_csv(csv_path)
            print(f"✅ Dataset loaded: {len(self.df)} resumes")
        
        self.categories = self.df['Category'].unique().tolist()
        self.label_encoder = LabelEncoder()
        self.encoded_categories = self.label_encoder.fit_transform(self.df['Category'])
        
    def get_category_distribution(self):
        return self.df['Category'].value_counts().to_dict()
    
    def get_sample_resumes_by_category(self, category, n=5):
        return self.df[self.df['Category'] == category].head(n)
    
    def get_all_resumes(self):
        return self.df

class ResumeParser:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Enhanced skills database with all new topics
        self.skills_db = [
            # Healthcare Skills
            'healthcare analysis', 'telemedicine', 'emr systems', 'electronic medical records',
            'healthcare analytics', 'medical ai', 'clinical data', 'patient data',
            'health informatics', 'medical imaging', 'healthcare it',
            
            # AI/ML Skills
            'llm', 'large language models', 'generative ai', 'computer vision',
            'tensorflow', 'pytorch', 'deep learning', 'machine learning',
            'natural language processing', 'nlp', 'neural networks',
            'artificial intelligence', 'ai',
            
            # Technology Skills
            'graphql', 'rest api', 'microservices', 'system design',
            'cloud computing', 'aws', 'azure', 'google cloud',
            'docker', 'kubernetes', 'devops', 'ci/cd',
            
            # Existing skills continue...
            'python', 'data analysis', 'statistics', 'scikit-learn', 'keras', 
            'pandas', 'numpy', 'data visualization', 'sql', 'big data', 
            'hadoop', 'spark', 'javascript', 'html', 'css', 'react', 
            'angular', 'vue', 'node.js', 'django', 'flask', 'php', 
            'laravel', 'java', 'spring', 'ruby', 'rails', 'mysql', 
            'mongodb', 'postgresql', 'oracle', 'sqlite', 'jenkins',
            'tableau', 'power bi', 'excel', 'r', 'sas', 'matlab',
            'c++', 'c#', 'net', 'swift', 'kotlin', 'android', 'ios',
            'git', 'linux', 'unix'
        ]
    
    def extract_text_from_pdf(self, file):
        text = ""
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"PDF extraction error: {e}")
        return text
    
    def extract_text_from_docx(self, file):
        text = ""
        try:
            doc = docx.Document(file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"DOCX extraction error: {e}")
        return text
    
    def extract_text(self, file):
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            return self.extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            return self.extract_text_from_docx(file)
        elif filename.endswith('.txt'):
            try:
                return file.read().decode('utf-8')
            except:
                return file.read().decode('latin-1')
        else:
            return ""
    
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = ' '.join(text.split())
        return text
    
    def extract_skills(self, text):
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.skills_db:
            if len(skill.split()) == 1:
                if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                    found_skills.append(skill.title())
            else:
                if skill in text_lower:
                    found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    def extract_experience(self, text):
        experience_patterns = [
            r'(\d+)\s*(?:years?|yrs?)',
            r'experience\s*(?:of)?\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s*experience',
        ]
        
        years_found = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower())
            years_found.extend([int(match) for match in matches])
        
        return max(years_found) if years_found else 0
    
    def predict_category(self, text, dataset, top_n=3):
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        all_texts = dataset.df['Resume'].tolist() + [text]
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        resume_vector = tfidf_matrix[-1]
        category_vectors = tfidf_matrix[:-1]
        
        similarities = cosine_similarity(resume_vector, category_vectors)[0]
        
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        top_categories = dataset.df.iloc[top_indices]['Category'].values
        top_scores = similarities[top_indices]
        
        category_predictions = []
        for cat, score in zip(top_categories, top_scores):
            category_predictions.append({
                'category': cat,
                'confidence': round(float(score) * 100, 2)
            })
        
        return category_predictions
    
    def analyze_skill_gaps(self, user_skills, target_category):
        """Analyze missing skills compared to trending skills in the category"""
        user_skills_lower = [skill.lower() for skill in user_skills]
        trending_skills = TRENDING_SKILLS.get(target_category, [])
        
        missing_skills = []
        for skill in trending_skills:
            if skill.lower() not in user_skills_lower:
                missing_skills.append(skill)
        
        return missing_skills[:5]  # Return top 5 missing skills
    
    def calculate_profile_strength(self, skills, experience, category_predictions):
        """Calculate overall profile strength"""
        base_score = 0
        
        # Experience score (0-30 points)
        exp_score = min(experience * 6, 30)
        
        # Skills score (0-40 points)
        skills_score = min(len(skills) * 2, 40)
        
        # Category confidence score (0-30 points)
        conf_score = category_predictions[0]['confidence'] * 0.3 if category_predictions else 0
        
        total_score = exp_score + skills_score + conf_score
        strength_level = "Beginner" if total_score < 40 else "Intermediate" if total_score < 70 else "Advanced"
        
        return {
            'total_score': int(total_score),
            'strength_level': strength_level,
            'breakdown': {
                'experience': int(exp_score),
                'skills': int(skills_score),
                'category_fit': int(conf_score)
            }
        }
    
    def get_interview_questions(self, category):
        """Get relevant interview questions for the category"""
        return INTERVIEW_QUESTIONS.get(category, [
            "Tell me about yourself",
            "What are your strengths and weaknesses?",
            "Why do you want this position?",
            "Where do you see yourself in 5 years?"
        ])
    
    def get_learning_recommendations(self, missing_skills):
        """Get learning resources for missing skills with VALID URLs"""
        recommendations = []
        for skill in missing_skills:
            if skill in LEARNING_RESOURCES:
                rec = LEARNING_RESOURCES[skill]
                course_details = []
                for course in rec['courses']:
                    # Ensure the link is a valid URL
                    if course['link'].startswith(('http://', 'https://')):
                        course_link = course['link']
                    else:
                        # Fallback to search URL if link is invalid
                        course_link = f"https://www.google.com/search?q={skill.replace(' ', '+')}+course+{course['name'].replace(' ', '+')}"
                    
                    course_details.append({
                        'name': course['name'],
                        'type': course['type'],
                        'link': course_link  # Now this is guaranteed to be a valid URL
                    })
                
                recommendations.append({
                    'skill': skill,
                    'courses': course_details,
                    'platforms': rec['platforms'],
                    'projects': rec['projects']
                })
            else:
                # Default recommendations with valid Google search URLs
                course_details = [
                    {
                        'name': f'Best online course for {skill}',
                        'type': 'Free/Paid', 
                        'link': f"https://www.google.com/search?q={skill.replace(' ', '+')}+online+course"
                    },
                    {
                        'name': f'YouTube tutorials for {skill}',
                        'type': 'Free',
                        'link': f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial"
                    }
                ]
                
                recommendations.append({
                    'skill': skill,
                    'courses': course_details,
                    'platforms': ['LinkedIn Learning', 'Coursera', 'Udemy'],
                    'projects': [f'Build a project using {skill}', f'Practice {skill} exercises']
                })
        return recommendations[:3]  # Return top 3 recommendations
    
    def parse_resume(self, file, dataset):
        text = self.extract_text(file)
        if not text:
            return None
        
        cleaned_text = self.clean_text(text)
        skills = self.extract_skills(cleaned_text)
        experience = self.extract_experience(text)
        category_predictions = self.predict_category(cleaned_text, dataset)
        
        # Enhanced analysis - with proper error handling
        primary_category = category_predictions[0]['category'] if category_predictions else 'General'
        missing_skills = self.analyze_skill_gaps(skills, primary_category)
        profile_strength = self.calculate_profile_strength(skills, experience, category_predictions)
        interview_questions = self.get_interview_questions(primary_category)
        learning_recommendations = self.get_learning_recommendations(missing_skills)
        
        return {
            'raw_text': text[:500] + "..." if len(text) > 500 else text,
            'cleaned_text': cleaned_text,
            'skills': skills,
            'experience_years': int(experience),
            'skills_text': ' '.join(skills),
            'category_predictions': category_predictions,
            'text_length': len(text),
            'enhanced_analysis': {
                'missing_skills': missing_skills,
                'profile_strength': profile_strength,
                'interview_questions': interview_questions[:5],
                'learning_recommendations': learning_recommendations,
                'trending_skills': TRENDING_SKILLS.get(primary_category, [])[:5]
            }
        }

class JobMatcher:
    def __init__(self, dataset):
        self.dataset = dataset
        self.vectorizer = TfidfVectorizer(max_features=1500, stop_words='english')
    
    def find_similar_resumes(self, parsed_resume, top_n=10):
        all_texts = self.dataset.df['Resume'].tolist()
        query_text = parsed_resume['cleaned_text'] + ' ' + parsed_resume['skills_text']
        
        tfidf_matrix = self.vectorizer.fit_transform([query_text] + all_texts)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        
        results = []
        for idx in top_indices:
            resume_data = self.dataset.df.iloc[idx]
            results.append({
                'id': int(idx),
                'category': resume_data['Category'],
                'similarity_score': round(float(similarities[idx]) * 100, 2),
                'resume_preview': resume_data['Resume'][:200] + "..." if len(resume_data['Resume']) > 200 else resume_data['Resume'],
                'matched_skills': self.find_matching_skills(parsed_resume['skills'], resume_data['Resume'])
            })
        
        return results
    
    def find_matching_skills(self, user_skills, resume_text):
        resume_lower = resume_text.lower()
        matched = []
        for skill in user_skills:
            if skill.lower() in resume_lower:
                matched.append(skill)
        return matched
    
    def get_job_recommendations(self, parsed_resume):
        primary_category = parsed_resume['category_predictions'][0]['category'] if parsed_resume['category_predictions'] else 'General'
        
        category_resumes = self.dataset.df[self.dataset.df['Category'] == primary_category]
        
        recommendations = []
        for idx, resume in category_resumes.head(5).iterrows():
            recommendations.append({
                'job_title': f"{primary_category} Professional",
                'company': "Industry Standard",
                'required_skills': self.extract_top_skills(resume['Resume']),
                'experience_level': self.get_experience_level(parsed_resume['experience_years']),
                'category': primary_category,
                'description': f"Position in {primary_category} requiring skills in {', '.join(self.extract_top_skills(resume['Resume'])[:3])}",
                'salary_range': self.get_salary_range(primary_category, parsed_resume['experience_years'])
            })
        
        return recommendations
    
    def extract_top_skills(self, text, top_n=5):
        parser = ResumeParser()
        skills = parser.extract_skills(text.lower())
        return skills[:top_n]
    
    def get_experience_level(self, years):
        if years < 2:
            return "Entry Level"
        elif years < 5:
            return "Mid Level"
        else:
            return "Senior Level"
    
    def get_salary_range(self, category, experience):
        """Get estimated salary range based on category and experience for Indian market"""
        # Salary ranges in INR LPA (Lakhs Per Annum) for different experience levels
        # [Entry Level, Mid Level, Senior Level, Expert Level]
        indian_salaries = {
            'Data-Science': [
                {'min': 6, 'max': 10},    # 0-2 years - 6-10 LPA
                {'min': 10, 'max': 18},   # 2-5 years - 10-18 LPA
                {'min': 18, 'max': 30},   # 5-8 years - 18-30 LPA
                {'min': 30, 'max': 50}    # 8+ years - 30-50 LPA
            ],
            'Information-Technology': [
                {'min': 4, 'max': 8},     # 0-2 years - 4-8 LPA
                {'min': 8, 'max': 15},    # 2-5 years - 8-15 LPA
                {'min': 15, 'max': 25},   # 5-8 years - 15-25 LPA
                {'min': 25, 'max': 40}    # 8+ years - 25-40 LPA
            ],
            'Engineering': [
                {'min': 5, 'max': 9},     # 0-2 years - 5-9 LPA
                {'min': 9, 'max': 16},    # 2-5 years - 9-16 LPA
                {'min': 16, 'max': 28},   # 5-8 years - 16-28 LPA
                {'min': 28, 'max': 45}    # 8+ years - 28-45 LPA
            ],
            'Business-Development': [
                {'min': 3, 'max': 6},     # 0-2 years - 3-6 LPA
                {'min': 6, 'max': 12},    # 2-5 years - 6-12 LPA
                {'min': 12, 'max': 20},   # 5-8 years - 12-20 LPA
                {'min': 20, 'max': 35}    # 8+ years - 20-35 LPA
            ],
            'Finance': [
                {'min': 4, 'max': 8},     # 0-2 years - 4-8 LPA
                {'min': 8, 'max': 15},    # 2-5 years - 8-15 LPA
                {'min': 15, 'max': 25},   # 5-8 years - 15-25 LPA
                {'min': 25, 'max': 40}    # 8+ years - 25-40 LPA
            ],
            'Healthcare': [
                {'min': 3, 'max': 6},     # 0-2 years - 3-6 LPA
                {'min': 6, 'max': 12},    # 2-5 years - 6-12 LPA
                {'min': 12, 'max': 20},   # 5-8 years - 12-20 LPA
                {'min': 20, 'max': 35}    # 8+ years - 20-35 LPA
            ]
        }
        
        # Experience level mapping
        if experience < 2:
            level = 0  # Entry Level
        elif experience < 5:
            level = 1  # Mid Level
        elif experience < 8:
            level = 2  # Senior Level
        else:
            level = 3  # Expert Level
        
        # Get salary range for the category and level
        salary_range = indian_salaries.get(category, [
            {'min': 4, 'max': 8},
            {'min': 8, 'max': 15},
            {'min': 15, 'max': 25},
            {'min': 25, 'max': 40}
        ])[level]
        
        return f"₹{salary_range['min']}L - ₹{salary_range['max']}L PA"

# Initialize components
print("🚀 Initializing Enhanced Resume Parser...")
dataset = ResumeDataset('data/UpdatedResumeDataSet.csv')
resume_parser = ResumeParser()
job_matcher = JobMatcher(dataset)

@app.route('/')
def index():
    category_dist = dataset.get_category_distribution()
    return render_template('index.html', 
                         categories=dataset.categories,
                         category_dist=category_dist,
                         total_resumes=len(dataset.df))

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    try:
        parsed_resume = resume_parser.parse_resume(file, dataset)
        if not parsed_resume:
            return jsonify({'error': 'Could not parse resume. Please try a different file format.'})
        
        similar_resumes = job_matcher.find_similar_resumes(parsed_resume)
        job_recommendations = job_matcher.get_job_recommendations(parsed_resume)
        
        # Enhanced response with proper error handling
        enhanced_features = parsed_resume.get('enhanced_analysis', {})
        
        # Format learning recommendations for better display
        formatted_recommendations = []
        for rec in enhanced_features.get('learning_recommendations', []):
            formatted_courses = []
            for course in rec.get('courses', []):
                formatted_courses.append({
                    'name': course.get('name', 'Unknown Course'),
                    'type': course.get('type', 'Unknown Type'),
                    'link': course.get('link', '#')
                })
            
            formatted_recommendations.append({
                'skill': rec.get('skill', 'Unknown Skill'),
                'courses': formatted_courses,
                'platforms': rec.get('platforms', []),
                'projects': rec.get('projects', [])
            })
        
        response = {
            'resume_info': {
                'skills_found': parsed_resume['skills'],
                'experience_years': int(parsed_resume['experience_years']),
                'skills_count': len(parsed_resume['skills']),
                'category_predictions': parsed_resume['category_predictions'],
                'text_preview': parsed_resume['raw_text'],
                'text_length': int(parsed_resume['text_length'])
            },
            'similar_resumes': similar_resumes[:5],
            'job_recommendations': job_recommendations,
            'analysis': {
                'total_matches': len(similar_resumes),
                'avg_similarity': float(np.mean([r['similarity_score'] for r in similar_resumes[:5]])) if similar_resumes else 0,
                'top_category': parsed_resume['category_predictions'][0]['category'] if parsed_resume['category_predictions'] else 'General'
            },
            'enhanced_features': {
                'missing_skills': enhanced_features.get('missing_skills', []),
                'profile_strength': enhanced_features.get('profile_strength', {'total_score': 0, 'strength_level': 'Beginner', 'breakdown': {'experience': 0, 'skills': 0, 'category_fit': 0}}),
                'interview_questions': enhanced_features.get('interview_questions', []),
                'learning_recommendations': formatted_recommendations,
                'trending_skills': enhanced_features.get('trending_skills', [])
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'})

@app.route('/category/<category_name>')
def get_category_examples(category_name):
    examples = dataset.get_sample_resumes_by_category(category_name, 3)
    examples_data = []
    for idx, row in examples.iterrows():
        examples_data.append({
            'id': int(idx),
            'preview': row['Resume'][:300] + "..." if len(row['Resume']) > 300 else row['Resume'],
            'skills': resume_parser.extract_skills(row['Resume'].lower())
        })
    
    return jsonify({
        'category': category_name,
        'examples': examples_data,
        'count': int(len(dataset.df[dataset.df['Category'] == category_name])),
        'trending_skills': TRENDING_SKILLS.get(category_name, [])[:5],
        'interview_questions': INTERVIEW_QUESTIONS.get(category_name, [])[:3]
    })

@app.route('/stats')
def get_stats():
    category_dist = dataset.get_category_distribution()
    
    stats = {
        'total_resumes': int(len(dataset.df)),
        'total_categories': int(len(category_dist)),
        'avg_resume_length': int(dataset.df['Resume'].str.len().mean()),
        'top_categories': dict(sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:5])
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    print("🎯 Enhanced Job Matcher & Resume Parser Ready!")
    print("📊 Now supporting: Healthcare Analysis, Telemedicine, EMR Systems, LLM, Generative AI, Computer Vision, GraphQL, TensorFlow, PyTorch")
    print("🔗 All course links are fixed and will open in new tabs")
    print("🌐 Starting server at: http://localhost:5000")
    print("Press CTRL+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)