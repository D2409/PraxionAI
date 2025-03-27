import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Base API URL
BASE_URL = "http://127.0.0.1:5000"

# Initialize session_state for logged_in and session_cookie
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "session_cookie" not in st.session_state:
    st.session_state.session_cookie = None

st.title("🔒 Admin Dashboard - Ethics & Compliance Policies")

# Login Page
if not st.session_state.logged_in:
    st.header("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state.session_cookie = response.cookies.get_dict()
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials.")

# Main Dashboard
else:
    st.success("✅ You are logged in!")
    
    # Logout Button
    if st.button("Logout"):
        requests.get(f"{BASE_URL}/logout", cookies=st.session_state.session_cookie)
        st.session_state.logged_in = False
        st.session_state.session_cookie = None
        st.rerun()

    # Tabs for Managing Policies and Analytics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ Add Policy", 
        "📋 View and Manage Policies", 
        "📊 Analytics Dashboard", 
        "📄 Upload Policies", 
        "📂 View Uploaded Policies"
    ])

    # Add Policy
    with tab1:
        st.header("➕ Add a New Policy")
        question = st.text_input("Policy Question:")
        answer = st.text_area("Policy Answer:")
        if st.button("Submit Policy"):
            response = requests.post(
                f"{BASE_URL}/add_policy",
                json={"question": question, "answer": answer},
                cookies=st.session_state.session_cookie
            )
            if response.status_code == 200:
                st.success("Policy added successfully!")
                st.rerun()
            else:
                st.error(f"Failed to add policy: {response.json().get('error', 'Unknown error')}")

# View and Manage Policies
    with tab2:
        st.header("📋 View and Manage Policies")
        try:
            response = requests.get(f"{BASE_URL}/view_policies", cookies=st.session_state.session_cookie)
            if response.status_code == 200:
                policies = response.json().get("policies", [])
                if not policies:
                    st.warning("No policies found. Add a policy to get started.")
                else:
                    for policy in policies:
                        st.write(f"**Question:** {policy['question']}")
                        st.write(f"**Answer:** {policy['answer']}")

                        # Edit Policy
                        new_question = st.text_input(f"Edit Question {policy['id']}", value=policy["question"])
                        new_answer = st.text_area(f"Edit Answer {policy['id']}", value=policy["answer"])
                        if st.button(f"Save Changes {policy['id']}"):
                            edit_response = requests.put(
                                f"{BASE_URL}/edit_policy/{policy['id']}",
                                json={"question": new_question, "answer": new_answer},
                                cookies=st.session_state.session_cookie
                            )
                            if edit_response.status_code == 200:
                                st.success("Policy updated successfully!")
                                st.experimental_rerun()
                            else:
                                st.error(f"Failed to update policy: {edit_response.json().get('error', 'Unknown error')}")

                        # Delete Policy
                        if st.button(f"Delete Policy {policy['id']}"):
                            delete_response = requests.delete(
                                f"{BASE_URL}/delete_policy/{policy['id']}",
                                cookies=st.session_state.session_cookie
                            )
                            if delete_response.status_code == 200:
                                st.success("Policy deleted successfully!")
                                st.experimental_rerun()
                            else:
                                st.error(f"Failed to delete policy: {delete_response.json().get('error', 'Unknown error')}")
                        st.write("---")
            else:
                st.error(f"Failed to fetch policies: {response.text}")
        except requests.exceptions.JSONDecodeError as e:
            st.error(f"Invalid response format from server: {e}. Response content: {response.text}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    # Analytics Dashboard
    with tab3:
        st.header("📊 Analytics Dashboard")
        response = requests.get(f"{BASE_URL}/analytics", cookies=st.session_state.session_cookie)
        if response.status_code == 200:
            logs = response.json().get("logs", [])
            if not logs:
                st.warning("No analytics data available. Perform some actions to see analytics.")
            else:
                df = pd.DataFrame(logs)
                st.write("### All Logs")
                st.dataframe(df)

                st.write("### Action Distribution")
                action_counts = df['action'].value_counts()
                st.bar_chart(action_counts)

                st.write("### Activity Over Time")
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                timeline = df.groupby('date')['action'].count()
                st.line_chart(timeline)
        else:
            st.error(f"Failed to fetch analytics: {response.json().get('error', 'Unknown error')}")

    # Upload Policies
    with tab4:
        st.header("📂 Upload Policies")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if st.button("Upload Policy"):
            if uploaded_file is not None:
                files = {"file": uploaded_file.getvalue()}
                try:
                    response = requests.post(
                        f"{BASE_URL}/upload_policy",
                        files=files,
                        cookies=st.session_state.session_cookie
                    )
                    if response.status_code == 200:
                        st.success("Policy uploaded successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to upload policy.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("Please select a file before uploading.")

    # View Uploaded Policies
    with tab5:
        st.header("📜 View Uploaded Policies")
        response = requests.get(f"{BASE_URL}/view_uploaded_policies", cookies=st.session_state.session_cookie)
        if response.status_code == 200:
            uploaded_policies = response.json().get("uploaded_policies", [])
            if not uploaded_policies:
                st.warning("No uploaded policies found.")
            else:
                for policy in uploaded_policies:
                    st.write(f"**Filename:** {policy['filename']}")
                    st.write(f"**Content Preview:** {policy['content']}")

                    # Delete Uploaded Policy
                    if st.button(f"Delete Uploaded Policy {policy['id']}"):
                        delete_response = requests.delete(
                            f"{BASE_URL}/delete_uploaded_policy/{policy['id']}",
                            cookies=st.session_state.session_cookie
                        )
                        if delete_response.status_code == 200:
                            st.success("Uploaded policy deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete uploaded policy.")
                    st.write("---")
        else:
            st.error("Failed to fetch uploaded policies.")
