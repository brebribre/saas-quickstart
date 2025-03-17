from flask import Blueprint, request, jsonify
from controller.langchain.langchain_controller import LangChainController
import traceback
from flasgger import swag_from

# Create a Blueprint for the LangChain routes
langchain_bp = Blueprint('langchain', __name__)

# Initialize the LangChain controller
langchain_controller = LangChainController()

@langchain_bp.route('/ask', methods=['POST'])
@swag_from({
    "tags": ["LangChain"],
    "summary": "Ask a question to an AI model and get an answer",
    "description": "Send a question to one of the supported AI models and receive an answer",
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["question"],
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the AI model",
                        "example": "What is the capital of France?"
                    },
                    "model": {
                        "type": "string",
                        "description": "The ID of the model to use",
                        "enum": ["claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022"],
                        "default": "claude-3-5-haiku-20241022",
                        "example": "claude-3-5-haiku-20241022"
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Successful response with answer",
            "schema": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The AI model's answer to the question",
                        "example": "The capital of France is Paris."
                    },
                    "model": {
                        "type": "string",
                        "description": "The ID of the model that generated the answer",
                        "example": "gpt-3.5-turbo"
                    }
                }
            }
        },
        "400": {
            "description": "Bad request, missing required parameters",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Question is required"
                    }
                }
            }
        },
        "500": {
            "description": "Server error",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Failed to get answer: API key not found"
                    }
                }
            }
        }
    }
})
def ask():
    try:
        # Get the request data
        data = request.get_json()
        
        # Validate the request
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Question is required'
            }), 400
        
        question = data['question']
        model_id = data.get('model', 'gpt-3.5-turbo')
        
        # Ask the question using the LangChain controller
        result = langchain_controller.ask_question(question, model_id)
        
        # Return the answer
        return jsonify(result), 200
    
    except Exception as e:
        # Log the error
        print(f"Error in /ask endpoint: {str(e)}")
        print(traceback.format_exc())
        
        # Return an error response
        return jsonify({
            'error': str(e)
        }), 500 