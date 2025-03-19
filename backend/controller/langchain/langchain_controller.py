from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.prebuilt import create_react_agent

from controller.supabase.supabase_controller import SupabaseController

supabase_controller = SupabaseController()


import asyncio

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '../../langchain-tools'))

# Import tools here
from math_tool import (
    multiply, add, subtract, divide
)
from web_search_tool import web_search
from time_tool import get_current_date, get_current_time
from wikipedia_tool import wikipedia_search
from google_drive_tool import list_allowed_files, get_drive_file_content
load_dotenv()

class LangChainController:
    """Controller for handling LangChain operations with different models."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Initialize tool collections
        self.tools = {
            "math": {
                "name": "Math Tools",
                "description": "Mathematical operations and calculations",
                "tools": [multiply, add, subtract, divide]
            },
            "web": {
                "name": "Web Search",
                "description": "Web search and information retrieval",
                "tools": [web_search]
            },
            "time": {
                "name": "Time & Date",
                "description": "Date and time related operations",
                "tools": [get_current_date, get_current_time]
            },
            "wiki": {
                "name": "Wikipedia",
                "description": "Wikipedia search and article retrieval",
                "tools": [wikipedia_search]
            },
            "drive": {
                "name": "Google Drive",
                "description": "Google Drive file operations",
                "tools": [list_allowed_files, get_drive_file_content]
            }
            # Add more tool categories here 
        }
        
        # Model configurations
        self.models = {
            "claude-3-7-sonnet-20250219": {
                "provider": "anthropic",
                "name": "claude-3-7-sonnet-20250219"
            },
            "claude-3-5-haiku-20241022": {
                "provider": "anthropic",
                "name": "claude-3-5-haiku-20241022"
            },
            "claude-3-5-sonnet-20241022": {
                "provider": "anthropic",
                "name": "claude-3-5-sonnet-20241022"
            },
            # add more models here
        }
    
    def get_model_instance(self, model_id):
        """Get the appropriate model instance based on the model ID."""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not supported")
        
        model_config = self.models[model_id]
        provider = model_config["provider"]
        model_name = model_config["name"]
        
        if provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not found")
            return ChatOpenAI(
                model_name=model_name,
                openai_api_key=self.openai_api_key,
                temperature=0.7
            )
        
        elif provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key not found")
            return ChatAnthropic(
                model_name=model_name,
                anthropic_api_key=self.anthropic_api_key,
                temperature=0.7
            )
        
        elif provider == "google":
            if not self.google_api_key:
                raise ValueError("Google API key not found")
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=self.google_api_key,
                temperature=0.7
            )
        
        raise ValueError(f"Provider {provider} not supported")
    
    def get_supported_models(self):
        """Get a list of all supported AI models with their details.
        
        Returns:
            list: A list of dictionaries containing model information:
                - id: The model identifier
                - name: The actual model name
                - provider: The model provider (e.g., 'anthropic', 'openai', 'google')
        """
        return [
            {
                "id": model_id,
                "name": config["name"],
                "provider": config["provider"]
            }
            for model_id, config in self.models.items()
        ]
    
    def ask_question(self, question, model_id="claude-3-5-haiku-20241022"):
        """Ask a question to the specified model and return the answer."""
        try:
            model = self.get_model_instance(model_id)
            message = HumanMessage(content=question)
            response = model.invoke([message])
            
            return {
                "answer": response.content,
                "model": model_id
            }
        
        except Exception as e:
            print(f"Error in ask_question: {str(e)}")
            raise Exception(f"Failed to get answer: {str(e)}")
    
    def parse_agent_response(self, raw_response):
        """
        Parses the response from a Claude LangGraph ReAct agent into structured JSON.

        :param raw_response: The raw output from agent.ainvoke()
        :return: A dictionary containing structured steps and the final answer
        """
        steps = []
        final_answer = ""

        if isinstance(raw_response, dict) and "messages" in raw_response:
            messages = raw_response["messages"]
        else:
            messages = [raw_response] if isinstance(raw_response, (HumanMessage, AIMessage, ToolMessage)) else []

        step_description = None  

        for message in messages:
            if isinstance(message, AIMessage):
                if isinstance(message.content, list):  
                    for content in message.content:
                        if content.get("type") == "text":
                            step_description = content["text"]
                        elif content.get("type") == "tool_use":
                            steps.append({
                                "step": f"Step {len(steps) + 1}",
                                "description": step_description,
                                "tool_used": content["name"],
                                "input": content["input"],
                                "output": None 
                            })
                else:
                    final_answer = message.content  
                
            elif isinstance(message, ToolMessage):
                for step in steps:
                    if step["tool_used"] == message.name and step["output"] is None:
                        try:
                            step["output"] = float(message.content)
                        except ValueError:
                            step["output"] = message.content 

        return {
            "steps": steps,
            "final_answer": final_answer
        }

    def ask_agent(self, question, model_id="claude-3-5-haiku-20241022", tool_categories=None, user_id=None, agent_id=None):
        """
        Use LangGraph's ReAct agent approach to answer a question with multi-step reasoning.
        The agent decides if it needs any of the provided tools.
        
        :param question: The user's query
        :param model_id: The ID of the model to use (default: 'claude-3-5-haiku-20241022')
        :param tool_categories: (Optional) List of tool category names to enable (e.g. ["math"])
                            If None, all available tools are used.
        :param user_id: The ID of the user making the request
        :param agent_id: The ID of the agent being used
        :return: dict with steps and final answer
        """
        try:
            model = self.get_model_instance(model_id)
            
            if tool_categories:
                selected_tools = []
                for cat in tool_categories:
                    selected_tools.extend(self.tools.get(cat, [])["tools"])
            else:
                selected_tools = []
                for cat_tools in self.tools.values():
                    selected_tools.extend(cat_tools["tools"])
            
            # Create config with user_id and agent_id
            config = {
                "configurable": {
                    "user_id": user_id,
                    "agent_id": agent_id
                }
            } if user_id or agent_id else {}

            # Get full history
            history = supabase_controller.select("ai_agents", filters={"id": agent_id})[0]["chat_history"] or []

            messages = []
            token_count = 0
            token_budget = 3000  # Model-dependent, adjust as needed
            MAX_RECENT_MESSAGES = 5  # Always include the most recent exchanges

            # Always include the N most recent messages
            recent_messages = history[-MAX_RECENT_MESSAGES:] if len(history) >= MAX_RECENT_MESSAGES else history
            older_messages = history[:-MAX_RECENT_MESSAGES] if len(history) >= MAX_RECENT_MESSAGES else []

            # Add older messages until we approach token budget
            for msg in reversed(older_messages):  # Start from more recent older messages
                # Rough token estimation (3 tokens per word + 4 for role)
                msg_tokens = len(msg["content"].split()) * 3 + 4
                if token_count + msg_tokens > token_budget:
                    break
                
                if msg["role"] == "user":
                    messages.insert(0, HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.insert(0, AIMessage(content=msg["content"]))
                
                token_count += msg_tokens

            # Add all recent messages
            for msg in recent_messages:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

            # Add current question
            messages.append(HumanMessage(content=question))
            
            agent = create_react_agent(
                model=model,
                tools=selected_tools,
                prompt=(
                    "You are a helpful assistant. \n\n"             
                    "You have access to specialized tools to help you answer the question. \n\n"
                    "You don't need to specify that you used a tool, just answer the question."
                    "Never assume the current date or time, use the tools to get the current date and time."
                    "Always write your answer in markdown format and use bullet points and numbered lists when appropriate."
                )
            )
            
            async def _run_agent():
                # Pass the message history instead of just the current question
                result = await agent.ainvoke(
                    {"messages": messages},
                    config=config
                )
                return result

            raw_response = asyncio.run(_run_agent())
            parsed_response = self.parse_agent_response(raw_response)
            
            return parsed_response
            
        except Exception as e:
            print(f"Error in ask_agent: {str(e)}")
            raise Exception(f"Failed to process query: {str(e)}")

    def get_available_tools(self):
        """Get a list of all available tools organized by category.
        
        Returns:
            dict: A dictionary where:
                - keys are tool category names (e.g., 'math', 'web')
                - values are dictionaries containing:
                    - name: Category display name
                    - description: Category description
                    - tools: List of tools with their name and description
        """
        available_tools = {}
        
        for category, config in self.tools.items():
            tools_list = []
            for tool in config["tools"]:
                tool_info = {
                    "name": tool.name,
                    "description": tool.description
                }
                tools_list.append(tool_info)
            
            available_tools[category] = {
                "name": config["name"],
                "description": config["description"],
                "tools": tools_list
            }
        
        return available_tools