import streamlit as st
import boto3
import os
import datetime
from io import BytesIO
from dotenv import load_dotenv
import emoji

load_dotenv()

# Initialize a session using Amazon S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('aws_access_key_id'),
    aws_secret_access_key=os.getenv('aws_secret_access_key'),
)

def upload_to_s3(file_name, file_data, bucket):
    """Uploads a file to an S3 bucket."""
    try:
        s3_client.upload_fileobj(file_data, bucket, file_name)
        st.success(f"File {file_name} uploaded successfully to {bucket}!")
    except Exception as e:
        st.error(f"Error uploading file: {e}")


def main():
    st.set_page_config(page_title="Admin dashboard for files upload",
                       page_icon=":books:")
    # st.write(css, unsafe_allow_html=True)

    # st.header("Newers Documents Uploader (Admin / Superuser)  ")  
    text_with_emoji = emoji.emojize("Newers Documents Uploader (Admin / Superuser) :books:")
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
        "Choose a file to upload and click on 'Upload'", )
    if st.button("Upload"):
        with st.spinner("Processing"):

            if uploaded_file is not None:
                
                # Convert the uploaded file to BytesIO (in-memory)
                file_data = BytesIO(uploaded_file.read())
                filename, extension = uploaded_file.name.split('.')
                # Call function to upload the file to S3
                upload_to_s3(f'{selected_value}/{filename}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.{extension}', file_data, bucket_name)

                # Show file name and preview
                st.write(f"Uploaded file: {uploaded_file.name}")


if __name__ == '__main__':
    main()