# Speech-Driven NLU Framework for Data Analytics

A web application that enables users to perform basic data analysis on CSV datasets using natural language through text and voice interaction.

Developed as part of a final year project to explore how LLMs can reduce the data literacy gap by simplifying dataset exploration and analytical workflows.

---

## Overview

Traditional data analysis tools often require familiarity with spreadsheets, SQL, programming, or BI platforms.

This project allows users to upload a dataset and ask questions in natural language. The system interprets the request, generates executable Pandas operations, executes them on the uploaded data, and returns responses through text, audio, and visual outputs.

---

## Features

### Core Functionality

* CSV dataset upload and analysis
* Natural language analytics through text input
* Voice-based interaction
* Dynamic Pandas code generation and execution

### User Experience

* Conversational interface
* Audio responses
* Chart generation for supported analytical requests
* Interaction history tracking

### V2 Improvements

* Conversation memory using recent interactions
* Multilingual interaction support
* In-chat data visualization

### Monitoring and Evaluation

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
├── README.md
│
├── templates/
└── static/
```

---

## Setup

Clone repository:

```bash
git clone https://github.com/Mohammed-Zain-py/Speech-driven-NLU-framework.git

cd Speech-driven-NLU-framework
```

Create environment:

```bash
python -m venv venv
```

Activate:

```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```env
GEMINI_API_KEY=your_key
SECRET_KEY=your_secret
ADMIN_USER=your_admin
ADMIN_PASS=your_password
```

Run application:

```bash
python app.py
```

---

## Project Evolution

The project went through multiple iterations during development.

Most iterations focused on improving usability and extending interaction modes. The largest changes between V1 and V2 introduced conversation memory, multilingual support, and integrated visualization capabilities.

---

## Future Improvements

* Introduce sandboxed execution for generated code
* Improve system scalability and deployment architecture
* Redesign frontend experience for larger analytical workflows
* Extend conversational memory capabilities
* Support larger datasets and asynchronous processing
* Add containerized deployment

---

## My Contributions

* Backend development
* LLM integration
* Analytics workflow
* Evaluation pipeline
* Conversation memory and visualization features
