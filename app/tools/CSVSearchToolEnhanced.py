from pydantic import BaseModel, Field
from crewai_tools.rag.data_types import DataType
from crewai_tools.tools.rag.rag_tool import RagTool
from typing import Any, Optional, Type

class FixedCSVSearchToolSchema(BaseModel):
    """Input for CSVSearchTool when CSV is pre-loaded."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the CSV's content",
    )


class CSVSearchToolSchema(FixedCSVSearchToolSchema):
    """Input for CSVSearchTool when CSV needs to be specified."""

    csv: str = Field(..., description="File path or URL of a CSV file to be searched")

class CSVSearchToolEnhanced(RagTool):
    name: str = "Search a CSV's content"
    description: str = (
        "A tool that can be used to semantic search a query from a CSV's content."
    )
    args_schema: Type[BaseModel] = CSVSearchToolSchema

    def __init__(
        self, 
        csv: Optional[str] = None,
        **kwargs
    ):
        """Initialize the enhanced CSV search tool.
        
        Args:
            csv: Optional path to CSV file. If provided, tool will be pre-configured for this file.
            **kwargs: Additional arguments passed to RagTool, including:
                - name: Optional custom name for the tool.
                - description: Optional custom description for the tool.
                - similarity_threshold: Minimum similarity score (default: 0.6).
                - limit: Maximum number of results (default: 5).
        """
        # Auto-generate description if CSV provided and no custom description
        if csv and "description" not in kwargs:
            kwargs["description"] = f"A tool that can be used to semantic search a query the {csv} CSV's content."
        
        # If CSV is provided, switch to fixed schema (no csv parameter needed)
        if csv:
            kwargs["args_schema"] = FixedCSVSearchToolSchema
        
        # Initialize parent
        super().__init__(**kwargs)
        
        # Pre-load CSV if provided
        if csv:
            self.add(csv, data_type=DataType.CSV)
            self._generate_description()

    def add(self, csv: str, **kwargs: Any) -> None:
        """Add a CSV file to the knowledge base.
        
        Args:
            csv: Path or URL to the CSV file.
            **kwargs: Additional arguments passed to the parent add method.
        """
        if "data_type" not in kwargs:
            kwargs["data_type"] = DataType.CSV
        super().add(csv, **kwargs)

    def _run(  # type: ignore[override]
        self,
        search_query: str,
        csv: Optional[str] = None,
        similarity_threshold: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> str:
        """Execute the search query.
        
        Args:
            search_query: The query to search for in the CSV.
            csv: Optional CSV file path (only used if tool wasn't pre-configured).
            similarity_threshold: Optional similarity threshold override.
            limit: Optional limit override.
            
        Returns:
            Search results as a formatted string.
        """
        # Validate inputs
        if not search_query:
            return "Error: Please provide a search query to search the CSV's content."
        
        # If CSV provided dynamically and tool not pre-configured, add it
        if csv is not None and self.args_schema == CSVSearchToolSchema:
            self.add(csv, data_type=DataType.CSV)
        elif csv is None and self.args_schema == CSVSearchToolSchema:
            return "Error: Please provide a CSV file path to search."
        
        # Execute search using parent's _run method
        return super()._run(
            query=search_query,
            similarity_threshold=similarity_threshold,
            limit=limit
        )

