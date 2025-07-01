from crewai.tools import BaseTool
from typing import Optional, List
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field, model_validator

class DuckDuckGoSearchToolInputSchema(BaseModel):
    query: str = Field(..., description="The specific query")
    max_results: int = Field(5, description="Maximum results")
    region: str = Field("fr-fr", description="Search region")
    safesearch: str = Field("moderate", description="Safesearch type")

class DuckDuckGoSearchToolInputSchemaFull(DuckDuckGoSearchToolInputSchema):
    domains: Optional[List[str]] = Field(default=None, description="Specific domains to search")
    time: Optional[str] = Field(None, description="Time range for results (d=day, w=week, m=month, y=year)")


class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "Search the web using DuckDuckGo and return relevant results."
    args_schema: DuckDuckGoSearchToolInputSchema | DuckDuckGoSearchToolInputSchemaFull = DuckDuckGoSearchToolInputSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._generate_description()

    def _run(self, query: str, max_results: int = 5, region: str = "fr-fr",
             safesearch: str = "moderate", time: Optional[str] = None,
             domains: Optional[List[str]] = None) -> str:
        """
        Search the web using DuckDuckGo and return formatted results.

        Args:
            query: The search query string
            max_results: Maximum number of results to return (default: 5)
            region: Region code for localized results (default: wt-wt for worldwide)
            safesearch: SafeSearch setting (off, moderate, strict)
            time: Time range for results (d=day, w=week, m=month, y=year)
            domains: List of domains to filter results by (e.g. ["wikipedia.org", "github.com"])

        Returns:
            A string containing the search results with titles, snippets, and URLs
        """
        try:
            # Initialize the DuckDuckGo Search client
            ddgs = DDGS()

            # Format domains for the query if provided
            domain_filter = ""
            if domains:
                domain_filter = " " + " ".join(f"site:{domain}" for domain in domains)

            # Perform the search with parameters
            results = list(ddgs.text(
                query + domain_filter,
                region=region,
                safesearch=safesearch,
                timelimit=time,
                max_results=max_results
            ))

            # Format the results
            if not results:
                return "No results found for the query."

            formatted_results = "Search Results:\n\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result['title']}\n"
                formatted_results += f"   {result['body']}\n"
                formatted_results += f"   URL: {result['href']}\n\n"

            return formatted_results

        except Exception as e:
            return f"Error performing search: {str(e)}"

    def run(self, inputs: DuckDuckGoSearchToolInputSchema | DuckDuckGoSearchToolInputSchemaFull):
        return self._run(
            inputs.query,
            inputs.max_results,
            inputs.region,
            inputs.safesearch
        )