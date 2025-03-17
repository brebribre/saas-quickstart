from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LangChainController:
    """Controller for handling LangChain operations with different models."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
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