# Speech-Driven NLU Framework for Data Analytics

A web application that enables users to perform basic data analysis on CSV datasets using natural language through text and voice interaction.

Developed as a final year project to explore how LLMs can reduce the data literacy gap for non-technical users by simplifying dataset exploration and analytical workflows.

---

## Overview

Traditional data analysis tools often require familiarity with spreadsheets, SQL, programming, or BI platforms.

This project allows users to upload a dataset and ask questions in natural language. The system interprets the request, generates executable Pandas operations, executes them on the uploaded data, and returns results as text, audio, and visual output.

---

## Features

### Core Functionality

* CSV dataset upload and session-based analysis
* Natural language analytics through text input
* Voice-based interaction support
* Dynamic Pandas code generation and execution

### User Experience

* Conversational interface
* Audio responses
* Chart generation for supported analytical requests
* Interaction history tracking

### V2 Improvements

* Conversation memory using recent interactions
* Multilingual support
* In-chat data visualization

### Monitoring

* Admin dashboard
* Conversation logging
* Benchmark-based evaluation
* Accuracy tracking

---

## Tech Stack

| Layer           | Technologies                               |
| --------------- | ------------------------------------------ |
| Backend         | Python, Flask, SQLAlchemy                  |
| Data Processing | Pandas                                     |
| AI              | Gemini API                                 |
| Frontend        | HTML, CSS, JavaScript, Bootstrap, Chart.js |
| Database        | SQLite                                     |

---

## Workflow

```text
Upload CSV
   ↓
Ask Question (Text / Voice)
   ↓
LLM → Generate Pandas Operation
   ↓
Execute on Dataset
   ↓
Generate Response
   ↓
Return Text / Audio / Visualization
```

---

## Project Structure

```text
Speech-driven-NLU-framework/
│
├── app.py
├── benchmark.json
├── evaluate.py
├── check_models.py
├── requirements.txt
│
├── templates/
├── static/
└── README.md
```

---

## Setup

```bash
git clone https://github.com/Mohammed-Zain-py/Speech-driven-NLU-framework.git

cd Speech-driven-NLU-framework

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

python app.py
```

Create `.env`

```env
GEMINI_API_KEY=your_key
SECRET_KEY=your_secret
ADMIN_USER=your_admin
ADMIN_PASS=your_password
```

---

## Development Notes

This project went through multiple iterations during development.

Most changes focused on improving usability and expanding interaction modes. The largest changes between V1 and V2 were conversation memory, multilingual interaction, and integrated visualization support.

---

## Future Improvements

- Introduce sandboxed execution for generated code
- Improve system scalability and deployment architecture
- Redesign frontend experience for larger analytical workflows
- Extend conversational memory capabilities
- Support larger datasets and asynchronous processing
- Add containerized deployment

---

## Contributions

This project was developed as a group final year project.

Primary contribution areas:

* Backend development
* LLM integration
* Analytics workflow
* Evaluation pipeline
* Conversation and visualization features
