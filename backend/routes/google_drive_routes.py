from flask import Blueprint, request, jsonify
from controller.supabase.supabase_controller import SupabaseController
import traceback
from flasgger import swag_from
from uuid import UUID

# Create a Blueprint for the Google Drive routes
google_drive_bp = Blueprint('google_drive', __name__)

# Initialize the Supabase controller
supabase_controller = SupabaseController()

@google_drive_bp.route('/file', methods=['POST'])
@swag_from({
    "tags": ["Google Drive"],
    "summary": "Create a new file access permission",
    "parameters": [{
        "in": "body",
        "name": "body",
        "required": True,
        "schema": {
            "type": "object",
            "required": ["user_id", "file_id"],
            "properties": {
                "user_id": {"type": "string", "format": "uuid"},
                "file_id": {"type": "string"}
            }
        }
    }],
    "responses": {
        "200": {"description": "File access granted successfully"},
        "400": {"description": "Bad request"},
        "500": {"description": "Server error"}
    }
})
def create_file_access():
    try:
        data = request.get_json()
        result = supabase_controller.insert("user_drive_permissions", data)
        return jsonify(result[0]), 200
    except Exception as e:
        print(f"Error creating file access: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@google_drive_bp.route('/file/user/<user_id>', methods=['GET'])
@swag_from({
    "tags": ["Google Drive"],
    "summary": "List all accessible files for a user",
    "parameters": [{
        "name": "user_id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid"
    }],
    "responses": {
        "200": {"description": "List of accessible files"},
        "500": {"description": "Server error"}
    }
})
def list_user_files(user_id):
    try:
        result = supabase_controller.select(
            "user_drive_permissions",
            filters={"user_id": user_id},
            order_by={"created_at": "desc"}
        )
        return jsonify(result), 200
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@google_drive_bp.route('/file/<id>', methods=['DELETE'])
@swag_from({
    "tags": ["Google Drive"],
    "summary": "Remove file access",
    "parameters": [{
        "name": "id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid",
        "description": "The unique ID of the permission record"
    }],
    "responses": {
        "200": {"description": "File access removed successfully"},
        "404": {"description": "File access not found"},
        "500": {"description": "Server error"}
    }
})
def delete_file_access(id):
    try:
        result = supabase_controller.delete(
            "user_drive_permissions",
            filters={"id": id}  # Using the table's primary key
        )
        if not result:
            return jsonify({"error": "File access not found"}), 404
        return jsonify({"message": "File access removed successfully"}), 200
    except Exception as e:
        print(f"Error removing file access: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@google_drive_bp.route('/file/batch', methods=['POST'])
@swag_from({
    "tags": ["Google Drive"],
    "summary": "Grant access to multiple files",
    "parameters": [{
        "in": "body",
        "name": "body",
        "required": True,
        "schema": {
            "type": "object",
            "required": ["user_id", "file_ids"],
            "properties": {
                "user_id": {"type": "string", "format": "uuid"},
                "file_ids": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }],
    "responses": {
        "200": {"description": "File access granted successfully"},
        "400": {"description": "Bad request"},
        "500": {"description": "Server error"}
    }
})
def create_batch_file_access():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        file_ids = data.get('file_ids', [])
        
        permissions = [
            {"user_id": user_id, "file_id": file_id}
            for file_id in file_ids
        ]
        
        result = supabase_controller.insert("user_drive_permissions", permissions)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error granting batch file access: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
