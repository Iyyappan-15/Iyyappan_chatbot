import streamlit as st
from langchain_groq import ChatGroq
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
import hashlib

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Iyyappan AI ",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database simulation 
class UserDatabase:
    def __init__(self):
        self.users_file = "users_data.json"
        self.conversations_file = "conversations_data.json"
        self.context_file = "user_context.json"
        
    def load_data(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_data(self, filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username, password):
        users = self.load_data(self.users_file)
        if username in users:
            return users[username]['password'] == self.hash_password(password)
        return False
    
    def create_user(self, username, password):
        users = self.load_data(self.users_file)
        if username in users:
            return False
        users[username] = {
            'password': self.hash_password(password),
            'created_at': datetime.now().isoformat(),
            'preferences': {
                'model': 'llama-3.3-70b-versatile',
                'temperature': 0.7,
                'theme': 'light'
            }
        }
        self.save_data(self.users_file, users)
        return True
    
    def get_user_conversations(self, username):
        conversations = self.load_data(self.conversations_file)
        user_convs = conversations.get(username, [])
        # Filter conversations from last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        filtered_convs = [
            conv for conv in user_convs 
            if datetime.fromisoformat(conv['created_at']) > seven_days_ago
        ]
        return filtered_convs
    
    def save_conversation(self, username, conv_id, messages, title="New Chat"):
        conversations = self.load_data(self.conversations_file)
        if username not in conversations:
            conversations[username] = []
        
        # Update existing or create new
        existing = next((c for c in conversations[username] if c['id'] == conv_id), None)
        if existing:
            existing['messages'] = messages
            existing['updated_at'] = datetime.now().isoformat()
        else:
            conversations[username].append({
                'id': conv_id,
                'title': title,
                'messages': messages,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
        
        self.save_data(self.conversations_file, conversations)
    
    def delete_conversation(self, username, conv_id):
        conversations = self.load_data(self.conversations_file)
        if username in conversations:
            conversations[username] = [c for c in conversations[username] if c['id'] != conv_id]
            self.save_data(self.conversations_file, conversations)
    
    def get_user_context(self, username):
        context_data = self.load_data(self.context_file)
        return context_data.get(username, {
            'topics_discussed': [],
            'preferences': {},
            'interaction_count': 0,
            'last_interaction': None
        })
    
    def update_user_context(self, username, message):
        context_data = self.load_data(self.context_file)
        if username not in context_data:
            context_data[username] = {
                'topics_discussed': [],
                'preferences': {},
                'interaction_count': 0,
                'last_interaction': None
            }
        
        # Update context
        context_data[username]['topics_discussed'].append({
            'message': message[:100],
            'timestamp': datetime.now().isoformat()
        })
        # Keep only last 50 topics
        context_data[username]['topics_discussed'] = context_data[username]['topics_discussed'][-50:]
        context_data[username]['interaction_count'] += 1
        context_data[username]['last_interaction'] = datetime.now().isoformat()
        
        self.save_data(self.context_file, context_data)

# Initialize database
db = UserDatabase()

# Available models
MODELS = {
    'llama-3.1-8b-instant': {'name': 'Fast (8B)', 'speed': '', 'cost': '$'},
    'llama-3.3-70b-versatile': {'name': 'Smart (70B)', 'speed': '', 'cost': '$$$'},
    'llama-3.2-90b-text-preview': {'name': 'Advanced (90B)', 'speed': '', 'cost': '$$$$'}
}

# Fixed response for personal identity
IYYAPPAN_PROFILE_RESPONSE = """
Iyyappan is an aspiring AI and Software Developer with a strong interest in building intelligent, user-centric applications.

He is the creator of this AI assistant, designed to provide smart, efficient, and user-friendly interactions.

He works extensively with Python, Streamlit, LangChain, Groq LLMs, and modern web technologies, focusing on developing AI-powered tools such as chatbots, learning platforms, and productivity applications.

Currently, Iyyappan is focused on strengthening his expertise in Artificial Intelligence, Full-Stack Development, and system design, with the objective of building scalable, real-world solutions that enhance learning and work efficiency.

He values clean architecture, practical problem-solving, and continuous professional growth.
"""

# Authentication
def login_page():
    st.markdown(
        """
        <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Full page background */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        .block-container {
            padding: 2rem 1rem !important;
            max-width: 100% !important;
        }
        
        /* Login container */
        .login-container {
            background: white;
            border-radius: 24px;
            padding: 48px 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            max-width: 440px;
            margin: 40px auto;
        }
        
        /* Logo */
        .login-logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
            border-radius: 50%;
            margin: 0 auto 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .login-logo::before {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
            border-radius: 50%;
            filter: blur(20px);
            opacity: 0.4;
            z-index: -1;
        }
        
        .logo-lines {
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding: 20px;
        }
        
        .logo-line {
            width: 40px;
            height: 4px;
            background: white;
            border-radius: 10px;
        }
        
        /* Title */
        .login-title {
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            color: #1a1a1a;
            margin: 0 0 8px 0;
        }
        
        /* Subtitle */
        .login-subtitle {
            text-align: center;
            font-size: 15px;
            color: #6b7280;
            margin-bottom: 32px;
            font-weight: 400;
        }
        
        /* Social buttons container */
        .social-buttons {
            display: flex;
            gap: 12px;
            margin-bottom: 28px;
        }
        
            /* Social button styling */
    .social-auth-btn {
        width: 100%;
        background: white !important;
        border: 1.5px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        height: 56px !important;
        cursor: pointer;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .social-auth-btn:hover {
        background: #f9fafb !important;
        border-color: #d1d5db !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }

    div[data-testid="column"] > div > div > button {
        background: white !important;
        border: 1.5px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        font-size: 22px !important;
        height: 56px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }

    div[data-testid="column"] > div > div > button:hover {
        background: #f9fafb !important;
        border-color: #d1d5db !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
            
            div[data-testid="column"] > div > div > button:hover {
                background: #f9fafb !important;
                border-color: #d1d5db !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
            }
            
        /* Divider */
        .divider {
            margin: 28px 0;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .divider-line {
            flex: 1;
            height: 1px;
            background: #e5e7eb;
        }
        
        .divider-text {
            font-size: 13px;
            color: #9ca3af;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Form labels */
        .stTextInput > label {
            font-size: 14px !important;
            font-weight: 600 !important;
            color: #1f2937 !important;
            margin-bottom: 8px !important;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            border-radius: 12px !important;
            border: 1.5px solid #e5e7eb !important;
            padding: 14px 16px !important;
            font-size: 15px !important;
            background: #f9fafb !important;
            transition: all 0.2s ease !important;
            color: #1f2937 !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #3b82f6 !important;
            background: white !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
            outline: none !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #9ca3af !important;
        }
        
        /* Checkbox and forgot password row */
        .remember-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0;
        }
        
        .stCheckbox {
            margin: 0 !important;
        }
        
        .stCheckbox > label {
            font-size: 14px !important;
            color: #4b5563 !important;
            font-weight: 500 !important;
        }
        
        .forgot-link {
            font-size: 14px;
            color: #3b82f6;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }
        
        .forgot-link:hover {
            color: #2563eb;
            text-decoration: underline;
        }
        
        /* Sign in button */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 16px 24px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            width: 100% !important;
            margin-top: 8px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #111827 0%, #000000 100%) !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25) !important;
        }
        
        /* Footer */
        .login-footer {
            text-align: center;
            margin-top: 24px;
            font-size: 14px;
            color: #6b7280;
        }
        
        .signup-link {
            color: #3b82f6;
            text-decoration: none;
            font-weight: 600;
            margin-left: 4px;
        }
        
        .signup-link:hover {
            color: #2563eb;
            text-decoration: underline;
        }
        
        /* Alerts */
        .stAlert {
            border-radius: 12px !important;
            margin: 16px 0 !important;
            border: none !important;
        }
        
        /* Remove form border */
        .stForm {
            border: none !important;
            padding: 0 !important;
        }
        
        /* Tab styling for Sign Up */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: transparent;
            border: none;
            margin-bottom: 24px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border: none !important;
            color: #6b7280 !important;
            font-weight: 600;
            padding: 8px 16px;
        }
        
        .stTabs [aria-selected="true"] {
            color: #1f2937 !important;
            border-bottom: 2px solid #1f2937 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create centered container
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        
        # Title & Subtitle
        st.markdown('<div class="login-title">Welcome </div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Please enter your details to sign in.</div>', unsafe_allow_html=True)

        # Social login buttons
        social_col1, social_col2, social_col3 = st.columns(3, gap="small")

        with social_col1:
            st.markdown('''
                <a href="https://appleid.apple.com/account" target="_blank" style="text-decoration: none;">
                    <button class="social-auth-btn">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg" 
                            alt="Apple" 
                            style="width: 24px; height: 24px;">
                    </button>
                </a>
            ''', unsafe_allow_html=True)

        with social_col2:
            st.markdown('''
                <a href="https://accounts.google.com/signup" target="_blank" style="text-decoration: none;">
                    <button class="social-auth-btn">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" 
                            alt="Google" 
                            style="width: 24px; height: 24px;">
                    </button>
                </a>
            ''', unsafe_allow_html=True)

        with social_col3:
            st.markdown('''
                <a href="https://twitter.com/i/flow/signup" target="_blank" style="text-decoration: none;">
                    <button class="social-auth-btn">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6f/Logo_of_Twitter.svg" 
                            alt="Twitter" 
                            style="width: 24px; height: 24px;">
                    </button>
                </a>
            ''', unsafe_allow_html=True)

        # Divider
        st.markdown(
            '<div class="divider"><div class="divider-line"></div><div class="divider-text">or</div><div class="divider-line"></div></div>',
            unsafe_allow_html=True
        )

        # Tabs for Sign In / Sign Up
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

        # ==================== SIGN IN TAB ====================
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("E-Mail Address", placeholder="Enter your email...")
                password = st.text_input("Password", type="password", placeholder="••••••••••")

                # Remember me & Forgot password
                col_check, col_forgot = st.columns([1, 1])
                with col_check:
                    remember = st.checkbox("Remember me")
                with col_forgot:
                    st.markdown(
                        '<a href="#" class="forgot-link" style="float: right; margin-top: 8px;">Forgot password?</a>',
                        unsafe_allow_html=True
                    )

                submit = st.form_submit_button("Sign in", type="primary", use_container_width=True)

                if submit:
                    if not email or not password:
                        st.error(" Please fill in all fields")
                    elif db.verify_user(email, password):
                        st.session_state.logged_in = True
                        st.session_state.username = email
                        st.success(" Login successful!")
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(" Invalid email or password")

            # Footer
            st.markdown(
                '<div class="login-footer">Don\'t have an account yet? <a href="#" class="signup-link">Sign Up</a></div>',
                unsafe_allow_html=True
            )

        # ==================== SIGN UP TAB ====================
        with tab2:
            with st.form("signup_form", clear_on_submit=False):
                new_email = st.text_input("E-Mail Address", placeholder="Enter your email...", key="signup_email")
                new_password = st.text_input("Password", type="password", placeholder="Create password", key="signup_pass")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="confirm_pass")
                
                terms = st.checkbox("I agree to Terms & Conditions")

                signup = st.form_submit_button("Create account", type="primary", use_container_width=True)

                if signup:
                    if not new_email or not new_password or not confirm_password:
                        st.error(" Please fill all fields")
                    elif not terms:
                        st.error(" Please agree to terms first")
                    elif new_password != confirm_password:
                        st.error(" Passwords don't match")
                    elif len(new_password) < 6:
                        st.error(" Password must be at least 6 characters")
                    elif db.create_user(new_email, new_password):
                        st.success(" Account created! Please sign in.")
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(" User already exists")

            st.markdown(
                '<div class="login-footer">Already have an account? <a href="#" class="signup-link">Sign In</a></div>',
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if "username" not in st.session_state:
        st.session_state.username = None
    
    if "current_conv_id" not in st.session_state:
        st.session_state.current_conv_id = None
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "llama-3.3-70b-versatile"

def init_llm(model_name, temperature=0.7):
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name=model_name,
        temperature=temperature
    )
    
    # Get user context for memory
    context = db.get_user_context(st.session_state.username)
    
    # Add context to memory initialization
    memory = ConversationBufferMemory()
    
    # Add context summary to memory
    if context['topics_discussed']:
        recent_topics = context['topics_discussed'][-5:]
        context_summary = "Previous context: " + "; ".join([t['message'] for t in recent_topics])
        memory.save_context(
            {"input": "System: Loading previous context"},
            {"output": context_summary}
        )
    
    return ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

def main_app():
    # Sidebar
    with st.sidebar:
        st.markdown(f"###  {st.session_state.username}")
        
        if st.button(" Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        
        st.markdown("---")
        
        # New Chat Button
        if st.button(" New Chat", use_container_width=True):
            st.session_state.current_conv_id = datetime.now().isoformat()
            st.session_state.chat_history = []
            st.session_state.conversation = init_llm(st.session_state.selected_model)
            st.rerun()
        
        st.markdown("---")
        
        # Model Selection
        st.markdown("####  Model Selection")
        selected_model = st.selectbox(
            "Choose Model",
            options=list(MODELS.keys()),
            format_func=lambda x: f"{MODELS[x]['name']} {MODELS[x]['speed']} {MODELS[x]['cost']}",
            key="model_selector"
        )
        
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.session_state.conversation = init_llm(selected_model)
        
        # Temperature
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        st.markdown("---")
        
        # User Context Display
        st.markdown("####  Context Memory")
        context = db.get_user_context(st.session_state.username)
        
        st.metric("Total Interactions", context['interaction_count'])
        
        if context['last_interaction']:
            last_time = datetime.fromisoformat(context['last_interaction'])
            time_ago = datetime.now() - last_time
            if time_ago.days > 0:
                st.write(f"Last seen: {time_ago.days} days ago")
            else:
                hours = time_ago.seconds // 3600
                st.write(f"Last seen: {hours} hours ago")
        
        if context['topics_discussed']:
            st.markdown("*Recent Topics:*")
            for topic in context['topics_discussed'][-3:]:
                st.caption(f"• {topic['message'][:50]}...")
        
        st.markdown("---")
        
        # Conversation History (Last 7 days)
        st.markdown("####  Recent Chats (7 days)")
        conversations = db.get_user_conversations(st.session_state.username)
        
        if conversations:
            for conv in conversations:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(
                        f" {conv['title'][:20]}...",
                        key=f"load_{conv['id']}",
                        use_container_width=True
                    ):
                        st.session_state.current_conv_id = conv['id']
                        st.session_state.chat_history = conv['messages']
                        st.rerun()
                with col2:
                    if st.button("", key=f"del_{conv['id']}"):
                        db.delete_conversation(st.session_state.username, conv['id'])
                        st.rerun()
        else:
            st.info("No recent chats")
    
    # Main chat area
    col_title, col_clear = st.columns([6, 1])
    with col_title:
        st.title(" Iyyappan's AI Assistant")
    with col_clear:
        if st.button(" Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_conv_id = None
            st.session_state.conversation = init_llm(st.session_state.selected_model)
            st.rerun()
    
    # Initialize conversation if not exists
    if st.session_state.conversation is None:
        st.session_state.conversation = init_llm(st.session_state.selected_model)
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for role, msg in st.session_state.chat_history:
            if role == "user":
                with st.chat_message("user"):
                    st.markdown(msg)
            else:
                with st.chat_message("assistant"):
                    st.markdown(msg)
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📎 Upload file (optional)",
        type=['txt', 'pdf', 'docx', 'jpg', 'png']
    )
    
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        db.update_user_context(st.session_state.username, user_input)

        # Normalize input
        normalized_input = user_input.strip().lower()

        # Custom fixed response
        if normalized_input == "who is iyyappan":
            response = IYYAPPAN_PROFILE_RESPONSE
            st.session_state.chat_history.append(("assistant", response))
        else:
            with st.spinner("Thinking..."):
                response = st.session_state.conversation.predict(input=user_input)
                st.session_state.chat_history.append(("assistant", response))

        
        if st.session_state.current_conv_id is None:
            st.session_state.current_conv_id = datetime.now().isoformat()
        
        title = user_input[:30] if len(st.session_state.chat_history) == 2 else "Chat"
        
        db.save_conversation(
            st.session_state.username,
            st.session_state.current_conv_id,
            st.session_state.chat_history,
            title
        )
        
        st.rerun()
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")

# Main execution
init_session_state()

if not st.session_state.logged_in:
    login_page()
else:
    main_app()