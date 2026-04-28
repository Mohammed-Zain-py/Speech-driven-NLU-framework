# Speech-Driven NLU Framework for Data Analytics 🎙️📊

**Project Overview**
An intelligent chatbot that translates natural voice commands into executable Python code to query and analyze datasets instantly. It bridges the gap between non-technical users and complex data analysis tools by allowing them to "talk" to their data.

**Tech Stack**
* **Core:** Python
* **NLU & AI:** Google Gemini API
* **Backend:** Flask
* **Data Processing:** Pandas
* **Database:** SQLite, Flask-SQLAlchemy
* **Speech Services:** gTTS (Google Text-to-Speech), Web Speech API (Speech-to-Text)

**Architecture**
The system follows a multi-stage pipeline to ensure accurate data retrieval and natural interaction:
1. **Input:** User speaks a query (e.g., "What is the average salary in Sales?").
2. **Processing:** Speech-to-Text converts audio input into a text string.
3. **Code Generation:** The Gemini API translates the natural language query into executable Pandas code.
4. **Execution:** The system executes the generated code against the dataset safely to retrieve a factual result.
5. **Answer Formatting:** The Gemini API takes the raw result and converts it into a natural, conversational sentence.
6. **Output:** Text-to-Speech converts the final text response back into audio for the user.

📸 **Screenshots / Demos**
<img width="1041" height="539" alt="Screenshot 2026-04-29 025800" src="https://github.com/user-attachments/assets/9fb998fd-b471-47f7-b7a6-515c2b7c7a23" />
<img width="1044" height="472" alt="Screenshot 2026-04-29 025812" src="https://github.com/user-attachments/assets/48213827-daeb-4226-8808-2d75d2f1d8f3" />


