Iyyappan AI Assistant
A secure, intelligent, and user-centric AI chatbot built using Streamlit, LangChain, and Groq LLMs, featuring authentication, conversation memory, model selection, and persistent chat history.

🚀 Features
User Authentication

Sign Up & Sign In system

Secure password hashing (SHA-256)

Session-based login management

AI Chat Assistant

Powered by Groq LLMs (LLaMA models)

Context-aware conversations using LangChain memory

Personalized responses with stored user context

Conversation Management

Persistent chat history (last 7 days)

Multiple chat sessions per user

Delete and reload previous conversations

Model Control

Switch between multiple Groq LLaMA models

Adjustable temperature for response creativity

Professional UI

Fully customized Streamlit UI

Modern login & signup interface

Sidebar dashboard with metrics and context memory

Custom Identity Response

Built-in override for personal identity queries
(e.g., "Who is Iyyappan")

File Upload Support

Upload text, PDF, DOCX, and image files (extensible)

🛠️ Tech Stack
Frontend: Streamlit

Backend Logic: Python

LLM Framework: LangChain

LLM Provider: Groq

Models: LLaMA 3.x series

Data Storage: JSON (lightweight local persistence)

Authentication: SHA-256 password hashing

Environment Management: python-dotenv

📁 Project Structure
bash
Copy code
.
├── app.py                     # Main Streamlit application
├── users_data.json             # User authentication data
├── conversations_data.json     # Chat history storage
├── user_context.json           # User interaction context
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
🔑 Environment Setup
1. Clone the Repository
bash
Copy code
git clone https://github.com/your-username/iyyappan-ai-assistant.git
cd iyyappan-ai-assistant
2. Create Virtual Environment (Recommended)
bash
Copy code
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
requirements.txt :
streamlit
langchain
langchain-groq
langchain-classic
python-dotenv
🔐 Environment Variables
Create a .env file in the project root:

ini
Copy code
GROQ_API_KEY=your_groq_api_key_here
Never commit your .env file to GitHub.

▶️ Run the Application
bash
Copy code
streamlit run app.py
Then open your browser at:

arduino
Copy code
http://localhost:8501
🧠 Supported Models
Model	Description
llama-3.1-8b-instant	Fast & lightweight
llama-3.3-70b-versatile	Balanced & intelligent
llama-3.2-90b-text-preview	Advanced reasoning

🔒 Security Notes
Passwords are never stored in plain text

Authentication data is hashed using SHA-256

API keys are loaded securely via environment variables

Session state prevents unauthorized access

📌 Custom Behavior
The assistant includes hard-coded logic for personal identity questions:

vbnet
Copy code
User: Who is Iyyappan?
AI: Displays a predefined professional profile
This avoids unnecessary LLM calls and ensures consistent branding.

📈 Future Enhancements
Database migration (PostgreSQL / MongoDB)

OAuth (Google, GitHub login)

File content analysis using LLMs

Role-based access (Admin / User)

Deployment on Streamlit Cloud or AWS

Vector memory (ChromaDB / FAISS)

👨‍💻 Author
Iyyappan

Aspiring AI & Software Developer with a strong focus on building intelligent, scalable, and user-centric applications using modern AI technologies.

📜 License
This project is open-source and available under the MIT License.
