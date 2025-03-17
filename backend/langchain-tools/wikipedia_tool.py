from langchain_core.tools import tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wiki_api_wrapper = WikipediaAPIWrapper()

@tool
def wikipedia_search(query: str, num_results: int = 3) -> list:
    """
    Searches Wikipedia and returns the top summaries.

    :param query: Search term for Wikipedia.
    :param num_results: Number of search results to return (default: 3).
    :return: List of Wikipedia article summaries.
    """
    try:
        wiki_search = WikipediaQueryRun(api_wrapper=wiki_api_wrapper)
        results = wiki_search.run(query)

        if isinstance(results, str):
            return [results]  # Return as a list if a single string result

        if isinstance(results, list):
            return results[:num_results]

        return ["No Wikipedia results found."]

    except Exception as e:
        return [f"Error: {str(e)}"]
