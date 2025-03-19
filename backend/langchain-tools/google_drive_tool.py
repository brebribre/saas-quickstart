from langchain_core.tools import tool, InjectedToolArg
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import json
import pandas as pd
from io import StringIO
import re
from typing_extensions import Annotated

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
def list_allowed_files(user_id: Annotated[str, InjectedToolArg]) -> list:
    """
    Returns a list of file names and IDs that are allowed for a specific user.

    :return: List of dictionaries containing 'id' and 'name' for each allowed file.
    """

    # TODO: Implement logic to get allowed files for the user
    try:
        file_details = []
        
        # Here you would implement logic to get allowed files for the user
        # For now, using the hardcoded ALLOWED_FILE_IDS
        for file_id in ALLOWED_FILE_IDS:
            try:
                file_metadata = drive_service.files().get(fileId=file_id, fields="id, name").execute()
                file_details.append({"id": file_metadata["id"], "name": file_metadata["name"]})
            except Exception as e:
                file_details.append({"id": file_id, "name": f"Error: {str(e)}"})

        return file_details if file_details else [{"id": None, "name": "No allowed files available."}]

    except Exception as e:
        return [{"id": None, "name": f"Critical error: {str(e)}"}]

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
            request = drive_service.files().export_media(fileId=file_id, mimeType="text/csv")
            content = request.execute().decode("utf-8")

            # Load CSV into Pandas DataFrame
            df = pd.read_csv(StringIO(content))
            summary = df.to_json(orient="records")
            cleaned_string = summary.replace('\\', '').replace('"', '').strip()  # Remove all backslashes
            cleaned_string = re.sub(r'"\s+|\s+"', '"', cleaned_string)
            
            return cleaned_string


        elif "application/pdf" in mime_type:
            return f"📕 This is a PDF file: {file_name} (ID: {file_id}). Convert it to text using a PDF parser."

        # ❌ Unsupported File Type
        else:
            return f"⚠️ Unsupported file type: {mime_type} for file '{file_name}'."

    except Exception as e:
        return f"❌ Error fetching file content: {str(e)}"

