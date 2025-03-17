from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent, create_react_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
import sys
from dotenv import load_dotenv

# Add the langchain-tools directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../langchain-tools'))

# Import the math tools
from math_tool import (
    multiply, add, subtract, divide, power, square_root,
    calculate_mean, calculate_median, calculate_standard_deviation,
    calculate_percentage, round_number, calculate_factorial,
    calculate_logarithm, solve_quadratic_equation
)

# Load environment variables
load_dotenv()

class LangChainController:
    """Controller for handling LangChain operations with different models."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Initialize tool collections
        self.tools = {
            "math": [
                multiply, add, subtract, divide, power, square_root,
                calculate_mean, calculate_median, calculate_standard_deviation,
                calculate_percentage, round_number, calculate_factorial,
                calculate_logarithm, solve_quadratic_equation
            ],
            # Add more tool categories here as they are developed
            # "web": [...],
            # "data": [...],
            # etc.
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
            # Log the error and return a generic message
            print(f"Error in ask_question: {str(e)}")
            raise Exception(f"Failed to get answer: {str(e)}")
    
    def ask_agent(self, query, model_id="claude-3-5-haiku-20241022", tool_categories=None):
        """
        Generic function to ask a question to an agent with access to tools.
        The agent will decide which tools to use based on the query.
        
        Args:
            query (str): The user's query or problem
            model_id (str): The ID of the model to use
            tool_categories (list, optional): List of tool categories to use. 
                                             If None, all available tools will be used.
        
        Returns:
            dict: The response from the agent, including the answer and tool usage information
        """
        try:
            # Get the model instance
            model = self.get_model_instance(model_id)
            
            # Determine which tools to use
            available_tools = []
            
            if tool_categories:
                # Use only the specified tool categories
                for category in tool_categories:
                    if category in self.tools:
                        available_tools.extend(self.tools[category])
            else:
                # Use all available tools
                for category, tools in self.tools.items():
                    available_tools.extend(tools)
            
            # Create a prompt template for the agent
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant that can use tools to answer the user's questions."),
                ("human", "{input}")
            ])
            
            # Create an agent with the available tools using the OpenAI tools format
            # This format is more compatible with various models
            agent = create_openai_tools_agent(model, available_tools, prompt)
            
            # Create an agent executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=available_tools,
                verbose=True,
                handle_parsing_errors=True
            )
            
            # Run the agent to process the query
            result = agent_executor.invoke({"input": query})
            
            # Determine which tool categories were used
            used_categories = set()
            for step in result.get("intermediate_steps", []):
                tool_name = step[0].tool
                for category, tools in self.tools.items():
                    if any(tool_name == t.name for t in tools):
                        used_categories.add(category)
            
            return {
                "answer": result["output"],
                "model": model_id,
                "tool_usage": result.get("intermediate_steps", []),
                "used_categories": list(used_categories)
            }
            
        except Exception as e:
            # Log the error and return a generic message
            print(f"Error in ask_agent: {str(e)}")
            raise Exception(f"Failed to process query: {str(e)}")