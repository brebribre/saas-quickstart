from flask import Blueprint, request, jsonify, current_app, url_for, send_file, Response, stream_with_context
from controller.supabase.supabase_controller import SupabaseController
import traceback
from flasgger import swag_from
from uuid import UUID, uuid4
import os
from werkzeug.utils import secure_filename
import mimetypes

# Create a Blueprint for file routes
file_bp = Blueprint('file', __name__)

# Initialize the Supabase controller
supabase_controller = SupabaseController()

@file_bp.route('/<agent_id>', methods=['POST'])
@swag_from({
    "tags": ["Files"],
    "summary": "Upload a file for an agent",
    "consumes": ["multipart/form-data"],
    "parameters": [
        {
            "name": "agent_id",
            "in": "path",
            "required": True,
            "type": "string",
            "format": "uuid",
            "description": "Agent ID"
        },
        {
            "name": "file",
            "in": "formData",
            "required": True,
            "type": "file",
            "description": "File to upload"
        },
        {
            "name": "user_id",
            "in": "formData",
            "required": True,
            "type": "string",
            "format": "uuid",
            "description": "User ID"
        }
    ],
    "responses": {
        "200": {"description": "File uploaded successfully"},
        "400": {"description": "Bad request"},
        "403": {"description": "Not authorized"},
        "500": {"description": "Server error"}
    }
})
def upload_file(agent_id):
    try:
        # Check if file part exists in request
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        # Get the file and user_id
        file = request.files['file']
        user_id = request.form.get('user_id')
        
        if not file or file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Read file content
        file_content = file.read()
        file_size = len(file_content)
        
        # Create a unique filename
        import uuid
        import os
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = f"{agent_id}/{unique_filename}"
        
        # Get content type as string
        content_type = str(file.content_type) if file.content_type else "application/octet-stream"
        
        # Upload to Supabase Storage - important fix here
        storage_client = supabase_controller.client.storage.from_("files")
        storage_result = storage_client.upload(
            file_path,
            file_content,
            file_options={"contentType": content_type}  # Use contentType key, not content-type
        )
        
        if hasattr(storage_result, 'error') and storage_result.error:
            return jsonify({"error": f"Storage error: {storage_result.error}"}), 500
            
        # Create file record in database
        file_data = {
            "agent_id": agent_id,
            "user_id": user_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": content_type
        }
        
        db_result = supabase_controller.insert("files", file_data)
        
        if not db_result:
            # Try to delete the uploaded file if database insert fails
            storage_client.remove([file_path])
            return jsonify({"error": "Failed to create file record"}), 500
            
        return jsonify(db_result[0]), 200
        
    except Exception as e:
        import traceback
        print(f"Error uploading file: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@file_bp.route('/agent/<agent_id>', methods=['GET'])
@swag_from({
    "tags": ["Files"],
    "summary": "List all files for an agent",
    "parameters": [{
        "name": "agent_id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid"
    }, {
        "name": "user_id",
        "in": "query",
        "required": True,
        "type": "string",
        "format": "uuid"
    }],
    "responses": {
        "200": {"description": "List of files"},
        "403": {"description": "Not authorized"},
        "500": {"description": "Server error"}
    }
})
def list_agent_files(agent_id):
    try:
        user_id = request.args.get('user_id')
        
        # Validate user access to agent
        agent_result = supabase_controller.select(
            "ai_agents",
            filters={"id": agent_id, "user_id": user_id}
        )
        
        if not agent_result:
            return jsonify({"error": "Not authorized to access files for this agent"}), 403
        
        # Get files
        result = supabase_controller.select(
            "files",
            filters={"agent_id": agent_id},
            order_by={"uploaded_at": "desc"}
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@file_bp.route('/<file_id>', methods=['DELETE'])
@swag_from({
    "tags": ["Files"],
    "summary": "Delete a file",
    "parameters": [{
        "name": "file_id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid",
        "description": "The unique ID of the file record"
    }, {
        "name": "user_id",
        "in": "query",
        "required": True,
        "type": "string",
        "format": "uuid"
    }],
    "responses": {
        "200": {"description": "File deleted successfully"},
        "403": {"description": "Not authorized"},
        "404": {"description": "File not found"},
        "500": {"description": "Server error"}
    }
})
def delete_file(file_id):
    try:
        user_id = request.args.get('user_id')
        
        # Get file details and verify ownership
        file_result = supabase_controller.select(
            "files",
            filters={"id": file_id, "user_id": user_id}
        )
        
        if not file_result:
            return jsonify({"error": "File not found or not authorized"}), 404
        
        file_data = file_result[0]
        file_path = file_data.get("file_path")
        
        # Delete from storage
        storage_result = supabase_controller.delete_file("files", file_path)
        
        # Delete from database (even if storage delete fails)
        db_result = supabase_controller.delete(
            "files",
            filters={"id": file_id}
        )
        
        if not db_result:
            return jsonify({"error": "Failed to delete file record"}), 500
        
        return jsonify({"message": "File deleted successfully"}), 200
        
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@file_bp.route('/<file_id>/url', methods=['GET'])
@swag_from({
    "tags": ["Files"],
    "summary": "Get a signed URL for a file",
    "parameters": [{
        "name": "file_id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid"
    }, {
        "name": "user_id",
        "in": "query",
        "required": True,
        "type": "string",
        "format": "uuid"
    }],
    "responses": {
        "200": {"description": "Signed URL for the file"},
        "403": {"description": "Not authorized"},
        "404": {"description": "File not found"},
        "500": {"description": "Server error"}
    }
})
def get_file_url(file_id):
    try:
        user_id = request.args.get('user_id')
        
        # Get file details and verify ownership
        file_result = supabase_controller.select(
            "files",
            filters={"id": file_id, "user_id": user_id}
        )
        
        if not file_result:
            return jsonify({"error": "File not found or not authorized"}), 404
        
        file_data = file_result[0]
        file_path = file_data.get("file_path")
        filename = file_data.get("filename")
        
        # Create a proxy URL for the frontend to use
        # This URL points to our proxy endpoint that will fetch and stream the file content
        proxy_url = url_for('file.proxy_file', file_id=file_id, user_id=user_id, _external=True)
        
        return jsonify({
            "signedUrl": proxy_url,
            "filename": filename
        }), 200
        
    except Exception as e:
        print(f"Error getting file URL: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Add a proxy endpoint to stream the file from Supabase to the client
@file_bp.route('/proxy/<file_id>', methods=['GET'])
def proxy_file(file_id):
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        # Get file details and verify ownership
        file_result = supabase_controller.select(
            "files",
            filters={"id": file_id, "user_id": user_id}
        )
        
        if not file_result:
            return jsonify({"error": "File not found or not authorized"}), 404
        
        file_data = file_result[0]
        file_path = file_data.get("file_path")
        filename = file_data.get("filename")
        mime_type = file_data.get("mime_type")
        
        # Get signed URL from Supabase
        url_result = supabase_controller.get_signed_url("files", file_path, 3600)
        
        if not url_result or "error" in url_result:
            return jsonify({"error": "Failed to generate signed URL"}), 500
        
        supabase_signed_url = url_result.get("signedURL")
        
        # Stream the file content from Supabase to the client
        import requests
        from flask import Response, stream_with_context
        
        # Make a streaming request to Supabase
        supabase_response = requests.get(supabase_signed_url, stream=True)
        
        # Return a streaming response to the client
        return Response(
            stream_with_context(supabase_response.iter_content(chunk_size=1024)),
            content_type=mime_type or 'application/octet-stream',
            headers={
                'Content-Disposition': f'inline; filename="{filename}"'
            }
        )
        
    except Exception as e:
        print(f"Error proxying file: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500