from flask import Blueprint, request, jsonify
from controller.langchain.langchain_controller import LangChainController
import traceback
from flasgger import swag_from
from datetime import datetime
from controller.supabase.supabase_controller import SupabaseController

# Create a Blueprint for the LangChain routes
langchain_bp = Blueprint('langchain', __name__)

# Initialize the LangChain controller
langchain_controller = LangChainController()

# Initialize the Supabase controller
supabase_controller = SupabaseController()

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

@langchain_bp.route('/agent/ask', methods=['POST'])
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
                "required": ["question", "user_id", "agent_id"],
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the AI model",
                        "example": "What is 7 multiplied by 5, then add 12?"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user making the request",
                        "example": "123e4567-e89b-12d3-a456-426614174000"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "The ID of the agent to use",
                        "example": "agent-123"
                    },
                    "model": {
                        "type": "string",
                        "description": "The ID of the model to use",
                        "enum": ["claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"],
                        "default": "claude-3-5-haiku-20241022",
                        "example": "claude-3-5-haiku-20241022"
                    },
                    "tool_categories": {
                        "type": "array",
                        "items": { "type": "string" },
                        "description": "List of tool categories to enable (e.g. ['math']). If not provided, all tools are available.",
                        "example": ["math", "web"]
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Successful response with agent's reasoning steps and final answer",
            "schema": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "description": "The reasoning steps taken by the agent, including tools used",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step": {
                                    "type": "string",
                                    "description": "Step identifier",
                                    "example": "Step 1"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Agent's reasoning for this step",
                                    "example": "I need to multiply 7 by 5 first"
                                },
                                "tool_used": {
                                    "type": "string",
                                    "description": "Name of the tool used in this step",
                                    "example": "multiply"
                                },
                                "input": {
                                    "type": "object",
                                    "description": "Input parameters provided to the tool",
                                    "example": {"a": 7, "b": 5}
                                },
                                "output": {
                                    "type": ["number", "string"],
                                    "description": "Result returned by the tool",
                                    "example": 35
                                }
                            }
                        }
                    },
                    "final_answer": {
                        "type": "string",
                        "description": "The agent's final answer after completing all reasoning steps",
                        "example": "The result is 47."
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
    try:
        # Get the request data
        data = request.get_json()
        
        # Validate the request
        if not data or 'question' not in data or 'user_id' not in data or 'agent_id' not in data:
            return jsonify({
                'error': 'Question, user_id, and agent_id are required'
            }), 400
        
        question = data['question']
        user_id = data['user_id']
        agent_id = data['agent_id']
        model_id = data.get('model', 'claude-3-5-haiku-20241022')
        tool_categories = data.get('tool_categories', None)
        
        # Create user message timestamp when request is received
        user_timestamp = datetime.utcnow().isoformat()
        
        # Process the query using the LangChain agent
        result = langchain_controller.ask_agent(question, model_id, tool_categories, user_id, agent_id)
        
        # Get current agent data to access existing chat history
        agent_data = supabase_controller.select("ai_agents", filters={"id": agent_id})[0]
        existing_history = agent_data.get("chat_history", [])
        
        # Create new messages
        new_messages = [
            {
                "role": "user",
                "content": question,
                "timestamp": user_timestamp
            },
            {
                "role": "assistant",
                "content": result["final_answer"],
                "steps": result["steps"],
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        # Combine existing history with new messages
        updated_history = existing_history + new_messages if existing_history else new_messages
        
        # Update both chat_history and increment usage_count
        supabase_controller.update(
            "ai_agents",
            {
                "chat_history": updated_history,
                "usage_count": agent_data.get("usage_count", 0) + 1
            },
            filters={"id": agent_id}
        )
        
        # Return the answer
        return jsonify(result), 200
    
    except Exception as e:
        # Log the error
        print(f"Error in /agent endpoint: {str(e)}")
        print(traceback.format_exc())
        
        # Return an error response
        return jsonify({
            'error': str(e)
        }), 500

@langchain_bp.route('/models', methods=['GET'])
@swag_from({
    "tags": ["LangChain"],
    "summary": "Get list of supported AI models",
    "description": "Returns a list of all supported AI models with their details including ID, name, and provider",
    "responses": {
        "200": {
            "description": "List of supported models",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "The model identifier",
                            "example": "claude-3-5-haiku-20241022"
                        },
                        "name": {
                            "type": "string",
                            "description": "The actual model name",
                            "example": "claude-3-5-haiku-20241022"
                        },
                        "provider": {
                            "type": "string",
                            "description": "The model provider",
                            "example": "anthropic"
                        }
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
                        "example": "Failed to get supported models: [some error message]"
                    }
                }
            }
        }
    }
})
def get_models():
    try:
        # Get the list of supported models from the controller
        models = langchain_controller.get_supported_models()
        
        # Return the models list
        return jsonify(models), 200
    
    except Exception as e:
        # Log the error
        print(f"Error in /models endpoint: {str(e)}")
        print(traceback.format_exc())
        
        # Return an error response
        return jsonify({
            'error': f"Failed to get supported models: {str(e)}"
        }), 500

@langchain_bp.route('/tools', methods=['GET'])
@swag_from({
    "tags": ["LangChain"],
    "summary": "Get list of available tools",
    "description": "Returns a list of all available tools organized by category with their names and descriptions",
    "responses": {
        "200": {
            "description": "Available tools by category",
            "schema": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Display name of the tool category",
                            "example": "Math Tools"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the tool category",
                            "example": "Mathematical operations and calculations"
                        },
                        "tools": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "The tool's name",
                                        "example": "multiply"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "The tool's description",
                                        "example": "Multiplies two numbers"
                                    }
                                }
                            }
                        }
                    }
                },
                "example": {
                    "math": {
                        "name": "Math Tools",
                        "description": "Mathematical operations and calculations",
                        "tools": [
                            {
                                "name": "multiply",
                                "description": "Multiplies two numbers"
                            },
                            {
                                "name": "add",
                                "description": "Adds two numbers"
                            }
                        ]
                    },
                    "web": {
                        "name": "Web Search",
                        "description": "Web search and information retrieval",
                        "tools": [
                            {
                                "name": "web_search",
                                "description": "Search the web for information"
                            }
                        ]
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
                        "example": "Failed to get available tools: [some error message]"
                    }
                }
            }
        }
    }
})
def get_tools():
    try:
        # Get the list of available tools from the controller
        tools = langchain_controller.get_available_tools()
        
        # Return the tools dictionary
        return jsonify(tools), 200
    
    except Exception as e:
        # Log the error
        print(f"Error in /tools endpoint: {str(e)}")
        print(traceback.format_exc())
        
        # Return an error response
        return jsonify({
            'error': f"Failed to get available tools: {str(e)}"
        }), 500