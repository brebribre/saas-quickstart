from langchain_core.tools import tool
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import json

SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON")
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
if SERVICE_ACCOUNT_JSON:
    creds = service_account.Credentials.from_service_account_info(
        json.loads(SERVICE_ACCOUNT_JSON), scopes=SCOPES
    )
else:
    raise ValueError("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON is not set! Please set the environment variable.")

drive_service = build("drive", "v3", credentials=creds)

ALLOWED_FILE_IDS = {"1a2YLu3wLWBbx_nAj8Zp_pH4mbLN0AHjQ5_o1CMC1KMs"}  # List of allowed folder IDs

@tool
def list_allowed_files() -> list:
    """
    Returns a list of file names and IDs that are **explicitly allowed**.

    :return: List of file names and their corresponding allowed IDs.
    """
    try:
        file_details = []
        
        for file_id in ALLOWED_FILE_IDS:
            file_metadata = drive_service.files().get(fileId=file_id, fields="id, name").execute()
            file_details.append(f"{file_metadata['name']} (ID: {file_metadata['id']})")

        return file_details if file_details else ["No allowed files available."]

    except Exception as e:
        return [f"Error retrieving allowed files: {str(e)}"]

@tool
def get_drive_file_content(file_id: str) -> str:
    """
    Fetches the content of a file from Google Drive and converts Google Docs, Sheets, and PDFs to readable formats.
    
    :param file_id: The ID of the file to retrieve.
    :return: The content of the file if it's a readable format; otherwise, a warning message.
    """
    try:
        file_metadata = drive_service.files().get(fileId=file_id, fields="mimeType, name").execute()
        file_name = file_metadata["name"]
        mime_type = file_metadata["mimeType"]

        if "text" in mime_type or "json" in mime_type:
            request = drive_service.files().get_media(fileId=file_id)
            content = request.execute().decode("utf-8")  
            return content

        elif mime_type == "application/vnd.google-apps.document":
            export_mime_type = "text/plain"
            request = drive_service.files().export_media(fileId=file_id, mimeType=export_mime_type)
            content = request.execute().decode("utf-8")
            return f"📄 Google Docs File: {file_name}\n\n{content}"

        elif mime_type == "application/vnd.google-apps.spreadsheet":
            export_mime_type = "text/csv"
            request = drive_service.files().export_media(fileId=file_id, mimeType=export_mime_type)
            content = request.execute().decode("utf-8")
            return f"📊 Google Sheets File: {file_name} (CSV Format)\n\n{content}"

        elif "application/pdf" in mime_type:
            return f"📕 This is a PDF file: {file_name} (ID: {file_id}). Convert it to text using a PDF parser."

        # ❌ Unsupported File Type
        else:
            return f"⚠️ Unsupported file type: {mime_type} for file '{file_name}'."

    except Exception as e:
        return f"❌ Error fetching file content: {str(e)}"

