from flask import Blueprint, request, jsonify
from controller.supabase.supabase_controller import SupabaseController
import traceback
from flasgger import swag_from
from uuid import UUID

# Create a Blueprint for the AI Agents routes
ai_agents_bp = Blueprint('ai_agents', __name__)

# Initialize the Supabase controller
supabase_controller = SupabaseController()

@ai_agents_bp.route('/', methods=['POST'])
@swag_from({
    "tags": ["AI Agents"],
    "summary": "Create a new AI agent",
    "parameters": [{
        "in": "body",
        "name": "body",
        "required": True,
        "schema": {
            "type": "object",
            "required": ["name", "model_id", "user_id"],
            "properties": {
                "name": {"type": "string", "example": "My Assistant"},
                "description": {"type": "string", "example": "A helpful AI assistant"},
                "model_id": {"type": "string", "example": "claude-3-5-haiku-20241022"},
                "user_id": {"type": "string", "format": "uuid"},
                "tool_categories": {"type": "array", "items": {"type": "string"}},
                "custom_instructions": {"type": "string"},
                "configuration": {"type": "object"}
            }
        }
    }],
    "responses": {
        "200": {"description": "AI agent created successfully"},
        "400": {"description": "Bad request"},
        "500": {"description": "Server error"}
    }
})
def create_agent():
    try:
        data = request.get_json()
        result = supabase_controller.insert("ai_agents", data)
        return jsonify(result[0]), 200
    except Exception as e:
        print(f"Error creating agent: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/<agent_id>', methods=['GET'])
@swag_from({
    "tags": ["AI Agents"],
    "summary": "Get an AI agent by ID",
    "parameters": [{
        "name": "agent_id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid"
    }],
    "responses": {
        "200": {"description": "AI agent details"},
        "404": {"description": "Agent not found"},
        "500": {"description": "Server error"}
    }
})
def get_agent(agent_id):
    try:
        result = supabase_controller.select(
            "ai_agents",
            filters={"id": agent_id}
        )
        if not result:
            return jsonify({"error": "Agent not found"}), 404
        return jsonify(result[0]), 200
    except Exception as e:
        print(f"Error getting agent: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/user/<user_id>', methods=['GET'])
@swag_from({
    "tags": ["AI Agents"],
    "summary": "List all AI agents for a user",
    "parameters": [{
        "name": "user_id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid"
    }],
    "responses": {
        "200": {"description": "List of AI agents"},
        "500": {"description": "Server error"}
    }
})
def list_agents(user_id):
    try:
        result = supabase_controller.select(
            "ai_agents",
            filters={"user_id": user_id},
            order_by={"created_at": "desc"}
        )
        return jsonify(result), 200
    except Exception as e:
        print(f"Error listing agents: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/<agent_id>', methods=['PATCH'])
@swag_from({
    "tags": ["AI Agents"],
    "summary": "Update an AI agent",
    "parameters": [
        {
            "name": "agent_id",
            "in": "path",
            "required": True,
            "type": "string",
            "format": "uuid"
        },
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "model_id": {"type": "string"},
                    "tool_categories": {"type": "array", "items": {"type": "string"}},
                    "custom_instructions": {"type": "string"},
                    "is_active": {"type": "boolean"},
                    "configuration": {"type": "object"}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "AI agent updated successfully"},
        "404": {"description": "Agent not found"},
        "500": {"description": "Server error"}
    }
})
def update_agent(agent_id):
    try:
        data = request.get_json()
        result = supabase_controller.update(
            "ai_agents",
            data=data,
            filters={"id": agent_id}
        )
        if not result:
            return jsonify({"error": "Agent not found"}), 404
        return jsonify(result[0]), 200
    except Exception as e:
        print(f"Error updating agent: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/<agent_id>', methods=['DELETE'])
@swag_from({
    "tags": ["AI Agents"],
    "summary": "Delete an AI agent",
    "parameters": [{
        "name": "agent_id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid"
    }],
    "responses": {
        "200": {"description": "AI agent deleted successfully"},
        "404": {"description": "Agent not found"},
        "500": {"description": "Server error"}
    }
})
def delete_agent(agent_id):
    try:
        result = supabase_controller.delete(
            "ai_agents",
            filters={"id": agent_id}
        )
        if not result:
            return jsonify({"error": "Agent not found"}), 404
        return jsonify({"message": "Agent deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting agent: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/<agent_id>/increment-usage', methods=['POST'])
@swag_from({
    "tags": ["AI Agents"],
    "summary": "Increment the usage count of an AI agent",
    "parameters": [{
        "name": "agent_id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid"
    }],
    "responses": {
        "200": {"description": "Usage count incremented successfully"},
        "500": {"description": "Server error"}
    }
})
def increment_usage(agent_id):
    try:
        result = supabase_controller.execute_rpc(
            "increment_agent_usage",
            {"agent_id": agent_id}
        )
        return jsonify({"message": "Usage count incremented successfully"}), 200
    except Exception as e:
        print(f"Error incrementing usage: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@ai_agents_bp.route('/<agent_id>/clear-history', methods=['POST'])
@swag_from({
    "tags": ["AI Agents"],
    "summary": "Clear chat history for an AI agent",
    "parameters": [{
        "name": "agent_id",
        "in": "path",
        "required": True,
        "type": "string",
        "format": "uuid"
    }],
    "responses": {
        "200": {"description": "Chat history cleared successfully"},
        "404": {"description": "Agent not found"},
        "500": {"description": "Server error"}
    }
})
def clear_chat_history(agent_id):
    try:
        result = supabase_controller.update(
            "ai_agents",
            data={"chat_history": []},
            filters={"id": agent_id}
        )
        if not result:
            return jsonify({"error": "Agent not found"}), 404
        return jsonify({"message": "Chat history cleared successfully"}), 200
    except Exception as e:
        print(f"Error clearing chat history: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500 