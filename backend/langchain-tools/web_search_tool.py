from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper
import os

# Load API Key
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
if not SERPAPI_KEY:
    raise ValueError("Missing SerpAPI Key! Set SERPAPI_API_KEY in environment variables.")

search = SerpAPIWrapper(serpapi_api_key=SERPAPI_KEY)

@tool
def web_search(query: str, num_results: int = 5) -> list:
    """
    Performs a web search using SerpAPI and returns the top search results.
    
    :param query: The search query.
    :param num_results: Number of search results to return (default is 5).
    :return: A list of search result snippets.
    """
    try:
        results = search.run(query) 
        
        if isinstance(results, str): 
            return [results] 

        if isinstance(results, list):
            return results[:num_results]  

        return ["No search results found."]

    except Exception as e:
        return [f"Error: {str(e)}"]
