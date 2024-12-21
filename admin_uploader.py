import streamlit as st
import boto3
import os
import datetime
from io import BytesIO
from dotenv import load_dotenv
import emoji
from update_embeddings import main as update_embedds

# Predefined username and password (this could be replaced by a more secure authentication mechanism)
USERNAME = "admin"
PASSWORD = "password123"

load_dotenv()

# Initialize a session using Amazon S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=st.secrets["aws"]["access_key_id"],  # Accessing secrets from Streamlit's secrets
    aws_secret_access_key=st.secrets["aws"]["secret_access_key"],
)

def upload_to_s3(file_name, file_data, bucket):
    """Uploads a file to an S3 bucket."""
    try:
        s3_client.upload_fileobj(file_data, bucket, file_name)
        st.success(f"File {file_name} uploaded successfully to {bucket}!")
    except Exception as e:
        st.error(f"Error uploading file: {e}")

def authenticate_user(username, password):
    """Check if the provided username and password are correct."""
    return username == USERNAME and password == PASSWORD

def show_login_page():
    """Display the login page."""
    st.title("Admin/Superuser Login ")
    
    # Collect username and password input from the user
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Button to submit login credentials
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.authenticated = True
            st.success("Login successful! Redirecting...")
            return True
        else:
            st.error("Invalid credentials. Please try again.")
            return False
    return False


def show_app():
    """Main app content after successful login."""
    st.set_page_config(page_title="Admin dashboard for files upload",
                       page_icon=":books:")
    col1, col2 = st.columns([6, 1])  # First column for title, second for the button above the title
    
    # Place the logout button in the second column (right-aligned above the title)
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.success("You have been logged out.")
            st.rerun()  # Redirect to login page after logout

    # Create a new row of columns for the title
    col1, _ = st.columns([7, 1])

    # st.header("Newers Documents Uploader (Admin / Superuser)  ")  
    text_with_emoji = emoji.emojize("Newers Documents Uploader (Admin / Superuser) :books:")  
    with col1:
        st.title(text_with_emoji)

    st.subheader("Upload employee manuals, policies or respective documents : ")

    
    # Define a dictionary of key-value pairs for dropdown
    options = {
        "10 things NOT to be done in Office":"Office_not_to_do",
        'FAQs - FBP & Reimbursement Process':'FBP_FAQ',
        'Flexible Benefit Plan':'FBP_PLUXEE',
        'Insurance Claim Reimbursement Process':'INSURANCE_CLAIMS',
        'Newers Handbook - Hybrid Work Model':'NEWERS_HANDBOOK',
        'NW Important Links - Holiday Calendar':'HOLIDAY_CALENDAR',
        'Payroll - FAQs':'PAYROLL_FAQ',
        'PF Process Manual':'PF_PROCESS',
        'TTN Car Lease Plan':'TTN_CAR_LEASE_PLAN',
        'TTN Core Values':'TTN_CORE_VALUES',
        'TTN Corporate Tie-Ups':'TTN_CORPORATE_TIE_UPS',
        'TTN Distribution List - Commonly used DLs':'TTN_DISTRIBUTION_LIST',
        'Understanding Pluxee':'UNDERSTANDING_PLUXEE'
    }


    # Display a dropdown to select an option
    selected_option = st.selectbox('Select the category of document to upload : ', list(options.keys()))

    # Get the corresponding value for the selected option
    selected_value = options[selected_option]
    st.write(f'You selected: {selected_option} (Internal Value: {selected_value})')

    bucket_name= 'gc-ai-spoc-document-ftp'

    uploaded_file = st.file_uploader(
        "Choose a file to upload and click on 'Upload'",type=["pdf"])
    if st.button("Upload"):

        with st.spinner("Processing"):

            if uploaded_file is not None:

                if uploaded_file.type != "application/pdf":
                    st.error("Please upload a valid PDF file.")
                    
                # Convert the uploaded file to BytesIO (in-memory)
                file_data = BytesIO(uploaded_file.read())
                filename, extension = uploaded_file.name.split('.')
                # Call function to upload the file to S3
                upload_to_s3(f'{selected_value}/{filename}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.{extension}', file_data, bucket_name)
                update_embedds()
                # Show file name and preview
                st.write(f"Uploaded file: {uploaded_file.name}")
            

# Main logic for controlling flow
def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Show the login page if the user is not authenticated
        if show_login_page():
            st.rerun()  # Rerun the script to reload the authenticated state
    else:
        # Show the main app content if the user is authenticated
        show_app()

if __name__ == '__main__':
    main()