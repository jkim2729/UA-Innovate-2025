import streamlit as st

# Set page config
st.set_page_config(page_title="Dinero Dossier", page_icon="💰", layout="centered")

# Apply custom styles
st.markdown("""
    <style>
        body {
            background-color: #f4f4f4;
        }
        .login-container {
            max-width: 400px;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .login-title {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
        }
        .btn-login {
            background-color: #2ecc71 !important;
            color: white !important;
            font-size: 16px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Dummy user credentials
USER_CREDENTIALS = {"admin": "password123", "user": "1234"}

# Function to check login
def check_login(username, password):
    return USER_CREDENTIALS.get(username) == password

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login screen
def login():
    st.markdown("<h1 style='text-align: center;'>💰 Dinero Dossier</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Your Smart Financial Advisor</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    
    if st.button("Login", key="login-btn"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Main content (only shown when logged in)
def main_app():
    st.markdown(f"<h1>Welcome, {st.session_state.username}! 🎉</h1>", unsafe_allow_html=True)
    st.write("You have successfully logged into Dinero Dossier.")
    
    st.markdown("### Your Financial Insights Await 📊")
    
    if st.button("Logout", key="logout-btn"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# Show login or main app
if not st.session_state.logged_in:
    login()
else:
    main_app()