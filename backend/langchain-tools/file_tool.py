from langchain_core.tools import tool, InjectedToolArg
from typing_extensions import Annotated
from controller.supabase.supabase_controller import SupabaseController
import json
import os
import mimetypes
import logging
from datetime import datetime, timedelta
from langchain_core.runnables import RunnableConfig
# Set up logging
logger = logging.getLogger("file_tool")

# Initialize the Supabase controller for database operations
supabase_controller = SupabaseController()

@tool
def list_uploaded_files(
    config: RunnableConfig
) -> list:
    """
    Returns a list of files that have been uploaded for a specific agent.

    :param user_id: The ID of the user making the request (injected)
    :param agent_id: The ID of the agent making the request (injected)
    :return: List of dictionaries containing file details
    """
    try:
       

        user_id = config.get("configurable", {}).get("user_id")
        agent_id = config.get("configurable", {}).get("agent_id")

        logger.info(f"list_uploaded_files called with user_id={user_id}, agent_id={agent_id}")
        
        # Check if we have the required parameters
        if not user_id or not agent_id:
            logger.error("Missing required parameters - user_id or agent_id is None")
            return [{"id": None, "name": "Missing required parameters: user_id and agent_id are required"}]
        
        # Validate user access to agent
        agent_result = supabase_controller.select(
            "ai_agents",
            filters={"id": agent_id, "user_id": user_id}
        )
        
        if not agent_result:
            logger.warning(f"Authorization failed: user_id={user_id}, agent_id={agent_id}")
            return [{"id": None, "name": "Not authorized to access files for this agent"}]
        
        # Get files
        result = supabase_controller.select(
            "files",
            filters={"agent_id": agent_id},
            order_by={"uploaded_at": "desc"}
        )
        
        if not result or len(result) == 0:
            logger.info(f"No files found for agent_id={agent_id}")
            return [{"id": None, "name": "No files found for this agent"}]
            
        # Format file information
        file_details = []
        for file in result:
            file_details.append({
                "id": file.get("id"),
                "name": file.get("filename"),
                "size": _format_file_size(file.get("file_size", 0)),
                "type": file.get("mime_type"),
                "uploaded_at": file.get("uploaded_at")
            })
        
        logger.info(f"Returning {len(file_details)} files")
        return file_details
    except Exception as e:
        logger.error(f"Error in list_uploaded_files: {str(e)}", exc_info=True)
        return [{"id": None, "name": f"Error listing files: {str(e)}"}]

@tool
def get_file_content(
    file_id: str,
    config: RunnableConfig
) -> str:
    """
    Retrieves the content of a file from storage.
    
    :param file_id: The ID of the file to retrieve.
    :param config: The config containing user_id (injected)
    :return: The content of the file if it's a readable format; otherwise, a warning message.
    """
    try:
        # Extract user_id from the config
        user_id = config.get("configurable", {}).get("user_id")
        
        logger.info(f"get_file_content called with file_id={file_id}, user_id={user_id}")
        
        # Check if we have the required parameters
        if not user_id:
            logger.error("Missing required parameter - user_id is None")
            return "⚠️ Missing required parameter: user_id is required"
            
        if not file_id:
            logger.error("Missing required parameter - file_id is None")
            return "⚠️ Missing required parameter: file_id is required"
        
        # Get file details and verify ownership
        file_result = supabase_controller.select(
            "files",
            filters={"id": file_id}
        )
        
        if not file_result:
            return "⚠️ File not found."
            
        file_data = file_result[0]
        
        # Verify user has access to the agent that owns this file
        agent_id = file_data.get("agent_id")
        agent_result = supabase_controller.select(
            "ai_agents",
            filters={"id": agent_id, "user_id": user_id}
        )
        
        if not agent_result:
            return "⚠️ Not authorized to access this file."
            
        file_path = file_data.get("file_path")
        file_name = file_data.get("filename")
        mime_type = file_data.get("mime_type")
        
        # Generate a signed URL for the file
        storage_client = supabase_controller.client.storage.from_("files")
        url_result = storage_client.create_signed_url(file_path, 60*60) # 1 hour expiry
        
        if hasattr(url_result, 'error') and url_result.error:
            return f"⚠️ Error generating URL: {url_result.error}"
            
        signed_url = url_result.get("signedURL")
        
        # For text-based files, fetch the content
        if mime_type and ("text/" in mime_type or "application/json" in mime_type):
            import requests
            response = requests.get(signed_url)
            if response.status_code == 200:
                return f"📄 File: {file_name}\n\n{response.text}"
            else:
                return f"⚠️ Failed to fetch file content: HTTP {response.status_code}"
                
        # For CSV files, try to parse as CSV
        if mime_type and ("text/csv" in mime_type):
            import requests
            import pandas as pd
            from io import StringIO
            
            response = requests.get(signed_url)
            if response.status_code == 200:
                try:
                    df = pd.read_csv(StringIO(response.text))
                    summary = df.to_json(orient="records")
                    return f"📊 CSV File: {file_name}\n\n{summary}"
                except Exception as e:
                    return f"⚠️ Failed to parse CSV: {str(e)}\n\nRaw content:\n{response.text[:1000]}..."
            else:
                return f"⚠️ Failed to fetch file content: HTTP {response.status_code}"

        # For PDFs specifically
        if mime_type and "application/pdf" in mime_type:
            import requests
            import io
            
            try:
                # First, download the PDF content
                response = requests.get(signed_url)
                if response.status_code != 200:
                    return f"⚠️ Failed to fetch PDF: HTTP {response.status_code}"
                
                # Use PyPDF2 to extract text from the PDF
                from PyPDF2 import PdfReader
                
                # Create a PDF reader object
                pdf_file = io.BytesIO(response.content)
                pdf_reader = PdfReader(pdf_file)
                
                # Extract text from all pages
                text_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += f"\n--- Page {page_num + 1} ---\n"
                    text_content += page.extract_text() or "[No extractable text on this page]"
                
                # Return the extracted text with a header
                return f"📄 PDF File: {file_name} ({len(pdf_reader.pages)} pages)\n\n{text_content}"
            
            except Exception as e:
                return f"⚠️ Error processing PDF: {str(e)}"

        # For other binary formats
        return f"�� File available at: {file_name} (ID: {file_id})\nFile type: {mime_type}\nThis file cannot be directly read. Please use external tools to process this file type."
        
    except Exception as e:
        return f"❌ Error fetching file content: {str(e)}"

@tool
def search_files(
    config: RunnableConfig,
    query: str = None,
    **kwargs
) -> list:
    """
    Searches for files by name or type that match the query.
    
    :param query: The search query for finding files.
    :param user_id: The ID of the user making the request (injected)
    :param agent_id: The ID of the agent making the request (injected)
    :return: List of dictionaries containing file details that match the query
    """
    try:
        user_id = config.get("configurable", {}).get("user_id")
        agent_id = config.get("configurable", {}).get("agent_id")

        logger.info(f"search_files called with user_id={user_id}, agent_id={agent_id}")
        
        # Handle cases where query may be passed as a positional argument
        if query is None and len(kwargs) == 1 and 'query' in kwargs:
            query = kwargs['query']
        
        logger.info(f"search_files called with query={query}, user_id={user_id}, agent_id={agent_id}")
        
        # Check if we have the required parameters
        if not user_id or not agent_id:
            logger.error("Missing required parameters - user_id or agent_id is None")
            return [{"id": None, "name": "Missing required parameters: user_id and agent_id are required"}]
            
        if not query:
            logger.error("Missing query parameter")
            return [{"id": None, "name": "Missing query parameter"}]
            
        # First list all files for this agent
        all_files = list_uploaded_files(user_id=user_id, agent_id=agent_id)
        
        # Check if there was an error or no files
        if len(all_files) == 1 and all_files[0].get("id") is None:
            return all_files
            
        # Filter files by name or type
        query = str(query).lower()
        matched_files = []
        
        for file in all_files:
            file_name = file.get("name", "").lower()
            file_type = file.get("type", "").lower()
            
            if query in file_name or query in file_type:
                matched_files.append(file)
                
        if not matched_files:
            return [{"id": None, "name": f"No files found matching '{query}'"}]
            
        logger.info(f"Found {len(matched_files)} matching files")
        return matched_files
    except Exception as e:
        logger.error(f"Error in search_files: {str(e)}", exc_info=True)
        return [{"id": None, "name": f"Error searching files: {str(e)}"}]

def _format_file_size(bytes: int) -> str:
    """Helper function to format file size in human-readable format"""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1048576:
        return f"{bytes/1024:.1f} KB"
    else:
        return f"{bytes/1048576:.1f} MB"
