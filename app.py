import streamlit as st
from supabase import create_client, Client

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="My Social App",
    page_icon="💬",
    layout="centered"
)

# -----------------------------
# SUPABASE CONNECTION
# -----------------------------
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

except Exception:
    st.error("Supabase is not configured correctly.")
    st.info("Add SUPABASE_URL and SUPABASE_KEY to Streamlit Secrets.")
    st.stop()


# -----------------------------
# SESSION STATE
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None


# -----------------------------
# LOGIN / SIGNUP
# -----------------------------
def authentication():
    st.title("💬 My Social App")
    st.write("Create an account or log in.")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    # LOGIN
    with tab1:
        st.subheader("Login")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):

            if not email or not password:
                st.warning("Please enter your email and password.")
                return

            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                st.session_state.user = response.user

                st.success("Login successful!")
                st.rerun()

            except Exception as e:
                st.error(f"Login failed: {e}")

    # SIGN UP
    with tab2:
        st.subheader("Create Account")

        new_email = st.text_input(
            "Email",
            key="signup_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button("Create Account", use_container_width=True):

            if not new_email or not new_password:
                st.warning("Please fill in all fields.")
                return

            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return

            if len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
                return

            try:
                response = supabase.auth.sign_up({
                    "email": new_email,
                    "password": new_password
                })

                if response.user:
                    st.success(
                        "Account created! Check your email if email confirmation is enabled."
                    )

            except Exception as e:
                st.error(f"Signup failed: {e}")


# -----------------------------
# MAIN APP
# -----------------------------
def main_app():

    user = st.session_state.user

    # SIDEBAR
    with st.sidebar:
        st.title("💬 Social App")

        st.write("### 👤 Profile")

        if user:
            st.write(f"**Email:** {user.email}")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):

            try:
                supabase.auth.sign_out()
            except Exception:
                pass

            st.session_state.user = None
            st.rerun()

    # HOME
    st.title("🏠 Home")

    st.success("You are logged in!")

    st.write(
        "Welcome to your social app. "
        "We'll add posts, images, videos and private chat next."
    )

    st.divider()

    st.subheader("🚀 Coming Next")

    col1, col2 = st.columns(2)

    with col1:
        st.info("📝 Text Posts")
        st.info("🖼️ Image Posts")
        st.info("🎥 Video Posts")

    with col2:
        st.info("❤️ Likes")
        st.info("💬 Comments")
        st.info("🔐 Private Chat")


# -----------------------------
# RUN APP
# -----------------------------
if st.session_state.user is None:
    authentication()
else:
    main_app()