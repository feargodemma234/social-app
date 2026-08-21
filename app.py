import streamlit as st
from supabase import create_client, Client
from datetime import datetime


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Social App",
    page_icon="💬",
    layout="wide"
)


# =========================================================
# SUPABASE
# =========================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# SESSION
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Home"


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_profile(user_id):

    result = (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if result.data:
        return result.data[0]

    return None


def get_username(user_id):

    profile = get_profile(user_id)

    if profile:
        return profile["username"]

    return "User"


def create_profile(user, username):

    try:

        supabase.table("profiles").insert({
            "id": user.id,
            "username": username,
            "bio": ""
        }).execute()

    except Exception:
        pass


def upload_media(file):

    if not file:
        return None, None

    filename = file.name.replace(" ", "_")

    unique_name = (
        f"{st.session_state.user.id}/"
        f"{datetime.now().timestamp()}_{filename}"
    )

    file_bytes = file.getvalue()

    supabase.storage.from_("posts").upload(
        unique_name,
        file_bytes,
        {
            "content-type": file.type
        }
    )

    public_url = (
        supabase.storage
        .from_("posts")
        .get_public_url(unique_name)
    )

    if file.type.startswith("image"):
        media_type = "image"

    elif file.type.startswith("video"):
        media_type = "video"

    else:
        media_type = "file"

    return public_url, media_type


# =========================================================
# LOGIN / SIGNUP
# =========================================================

def authentication():

    st.title("💬 Social App")

    st.write(
        "Connect with people, share posts and chat privately."
    )

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )


    # ---------------- LOGIN ----------------

    with login_tab:

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

        if st.button(
            "Login",
            use_container_width=True
        ):

            if not email or not password:

                st.warning(
                    "Enter your email and password."
                )

            else:

                try:

                    response = (
                        supabase.auth
                        .sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                    )

                    st.session_state.user = response.user

                    st.success("Welcome back!")

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Login failed: {e}"
                    )


    # ---------------- SIGNUP ----------------

    with signup_tab:

        st.subheader("Create Account")

        username = st.text_input(
            "Username"
        )

        email = st.text_input(
            "Email",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not username or not email or not password:

                st.warning(
                    "Please complete all fields."
                )

            elif password != confirm:

                st.error(
                    "Passwords don't match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                try:

                    response = (
                        supabase.auth
                        .sign_up({
                            "email": email,
                            "password": password
                        })
                    )

                    if response.user:

                        if response.session:

                            st.session_state.user = response.user

                            create_profile(
                                response.user,
                                username
                            )

                            st.success(
                                "Account created!"
                            )

                            st.rerun()

                        else:

                            st.success(
                                "Account created! "
                                "Check your email to confirm your account."
                            )

                except Exception as e:

                    st.error(
                        f"Signup failed: {e}"
                    )


# =========================================================
# HOME / FEED
# =========================================================

def home():

    st.title("🏠 Home")

    st.subheader("Create a post")

    content = st.text_area(
        "What's on your mind?",
        placeholder="Write something..."
    )

    media = st.file_uploader(
        "Add an image or video",
        type=[
            "jpg",
            "jpeg",
            "png",
            "gif",
            "mp4",
            "mov",
            "webm"
        ]
    )

    if st.button(
        "🚀 Publish",
        use_container_width=True
    ):

        if not content and not media:

            st.warning(
                "Write something or upload media."
            )

        else:

            try:

                media_url = None
                media_type = None

                if media:

                    media_url, media_type = upload_media(
                        media
                    )

                supabase.table("posts").insert({

                    "user_id":
                        st.session_state.user.id,

                    "content":
                        content,

                    "media_url":
                        media_url,

                    "media_type":
                        media_type

                }).execute()

                st.success(
                    "Post published!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not publish post: {e}"
                )


    st.divider()

    st.subheader("📰 Feed")

    result = (
        supabase
        .table("posts")
        .select("*")
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )

    posts = result.data

    if not posts:

        st.info(
            "No posts yet. Be the first to post!"
        )

        return


    for post in posts:

        username = get_username(
            post["user_id"]
        )

        st.markdown(
            f"### 👤 @{username}"
        )

        if post["content"]:

            st.write(
                post["content"]
            )

        if post["media_url"]:

            if post["media_type"] == "image":

                st.image(
                    post["media_url"],
                    use_container_width=True
                )

            elif post["media_type"] == "video":

                st.video(
                    post["media_url"]
                )


        # ---------------- LIKE ----------------

        like_result = (
            supabase
            .table("likes")
            .select("id")
            .eq("post_id", post["id"])
            .execute()
        )

        like_count = len(
            like_result.data
        )


        col1, col2 = st.columns(2)

        with col1:

            user_like = (
                supabase
                .table("likes")
                .select("id")
                .eq(
                    "post_id",
                    post["id"]
                )
                .eq(
                    "user_id",
                    st.session_state.user.id
                )
                .execute()
            )

            if user_like.data:

                if st.button(
                    f"💔 Unlike ({like_count})",
                    key=f"unlike_{post['id']}"
                ):

                    supabase.table(
                        "likes"
                    ).delete().eq(
                        "id",
                        user_like.data[0]["id"]
                    ).execute()

                    st.rerun()

            else:

                if st.button(
                    f"❤️ Like ({like_count})",
                    key=f"like_{post['id']}"
                ):

                    supabase.table(
                        "likes"
                    ).insert({

                        "post_id":
                            post["id"],

                        "user_id":
                            st.session_state.user.id

                    }).execute()

                    st.rerun()


        # ---------------- COMMENTS ----------------

        st.write("💬 Comments")

        comments = (
            supabase
            .table("comments")
            .select("*")
            .eq(
                "post_id",
                post["id"]
            )
            .order(
                "created_at"
            )
            .execute()
        )

        for comment in comments.data:

            comment_user = get_username(
                comment["user_id"]
            )

            st.write(
                f"**@{comment_user}:** "
                f"{comment['content']}"
            )


        comment_text = st.text_input(
            "Write a comment...",
            key=f"comment_{post['id']}"
        )

        if st.button(
            "Send",
            key=f"send_comment_{post['id']}"
        ):

            if comment_text.strip():

                supabase.table(
                    "comments"
                ).insert({

                    "post_id":
                        post["id"],

                    "user_id":
                        st.session_state.user.id,

                    "content":
                        comment_text.strip()

                }).execute()

                st.rerun()


        st.divider()


# =========================================================
# PRIVATE CHAT
# =========================================================

def private_chat():
    st.title("🔐 Private Chat")
    st.caption("Find people and start a private conversation.")

    # Get current user's ID
    current_user = st.session_state.user.id

    # Search people
    search = st.text_input(
        "🔎 Search people",
        placeholder="Search by username..."
    )

    # Get profiles
    query = (
        supabase
        .table("profiles")
        .select("id, username, bio")
        .neq("id", current_user)
        .order("username")
    )

    if search.strip():
        query = query.ilike("username", f"%{search.strip()}%")

    response = query.execute()
    users = response.data or []

    st.subheader("👥 People")

    if not users:
        if search.strip():
            st.info(f'No users found for "{search}".')
        else:
            st.info("There are no other users yet.")
        return

    # Show people
    for user in users:
        username = user.get("username") or "Unknown"
        bio = user.get("bio") or "No bio yet."

        with st.container(border=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### 👤 @{username}")
                st.caption(bio)

            with col2:
                if st.button(
                    "💬 Chat",
                    key=f"chat_{user['id']}"
                ):
                    st.session_state.chat_user_id = user["id"]
                    st.session_state.chat_username = username
                    st.rerun()

    # Open selected conversation
    if "chat_user_id" not in st.session_state:
        return

    chat_user_id = st.session_state.chat_user_id
    chat_username = st.session_state.chat_username

    st.divider()

    st.subheader(f"💬 Chat with @{chat_username}")

    # Load messages
    messages = (
        supabase
        .table("messages")
        .select("*")
        .or_(
            f"and(sender_id.eq.{current_user},receiver_id.eq.{chat_user_id}),"
            f"and(sender_id.eq.{chat_user_id},receiver_id.eq.{current_user})"
        )
        .order("created_at")
        .execute()
    )

    for message in messages.data or []:
        if message["sender_id"] == current_user:
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

    # Send message
    message = st.chat_input(
        f"Message @{chat_username}..."
    )

    if message:
        supabase.table("messages").insert({
            "sender_id": current_user,
            "receiver_id": chat_user_id,
            "content": message
        }).execute()

        st.rerun()
# =========================================================
# PROFILE
# =========================================================

def profile():

    user = st.session_state.user

    st.title("👤 My Profile")

    current_profile = get_profile(
        user.id
    )

    if current_profile:

        username = current_profile["username"]

        st.subheader(
            f"@{username}"
        )

        st.write(
            current_profile.get(
                "bio",
                ""
            )
        )

    else:

        st.warning(
            "Your profile has not been created yet."
        )


# =========================================================
# MAIN APP
# =========================================================

def main_app():

    user = st.session_state.user

    # SIDEBAR

    with st.sidebar:

        st.title("💬 Social App")

        st.write(
            f"👤 {get_username(user.id)}"
        )

        st.divider()

        if st.button(
            "🏠 Home",
            use_container_width=True
        ):

            st.session_state.page = "Home"

        if st.button(
            "🔐 Private Chat",
            use_container_width=True
        ):

            st.session_state.page = "Chat"

        if st.button(
            "👤 Profile",
            use_container_width=True
        ):

            st.session_state.page = "Profile"

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            supabase.auth.sign_out()

            st.session_state.user = None

            st.rerun()


    # PAGE ROUTING

    if st.session_state.page == "Home":

        home()

    elif st.session_state.page == "Chat":

        private_chat()

    elif st.session_state.page == "Profile":

        profile()


# =========================================================
# START
# =========================================================

if st.session_state.user:

    main_app()

else:

    authentication()