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
                        "example": "claude-3-5-haiku-20241022"
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
        model_id = data.get('model', 'claude-3-5-haiku-20241022')
        
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

@langchain_bp.route('/agent', methods=['POST'])
@swag_from({
    "tags": ["LangChain"],
    "summary": "Ask a question using a ReAct Agent (multi-step with tools)",
    "description": (
        "Send a question to one of the supported AI models, allowing the agent "
        "to decide whether and how to use available tools for multi-step reasoning."
    ),
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
                        "example": "What is 7 multiplied by 5, then add 12?"
                    },
                    "model": {
                        "type": "string",
                        "description": "The ID of the model to use",
                        "enum": ["claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022"],
                        "default": "claude-3-5-haiku-20241022",
                        "example": "claude-3-5-haiku-20241022"
                    },
                    "tool_categories": {
                        "type": "array",
                        "items": { "type": "string" },
                        "description": "List of tool categories to enable (e.g. ['math']). If not provided, all tools are available.",
                        "example": ["math"]
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Successful response with agent's final answer",
            "schema": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The agent's final answer after potentially using tools",
                        "example": "The result is 47."
                    },
                    "model": {
                        "type": "string",
                        "description": "The ID of the model used",
                        "example": "claude-3-5-haiku-20241022"
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
                        "example": "Failed to process query: [some error message]"
                    }
                }
            }
        }
    }
})
def agent():
    """
    POST endpoint: Uses an Agent with possible tool usage (multi-step reasoning).
    """
    try:
        # Get the request data
        data = request.get_json()
        
        # Validate the request
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question']
        model_id = data.get('model', 'claude-3-5-haiku-20241022')
        tool_categories = data.get('tool_categories', None)
        
        # Use the agent-based approach, passing the optional tool categories
        result = langchain_controller.ask_agent(
            question=question,
            model_id=model_id,
            tool_categories=tool_categories
        )
        
        # Return the answer
        return jsonify(result), 200
    
    except Exception as e:
        # Log the error
        print(f"Error in /agent endpoint: {str(e)}")
        print(traceback.format_exc())
        
        # Return an error response
        return jsonify({'error': str(e)}), 500