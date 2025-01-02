from pydantic import BaseModel, Field, model_validator
from crewai_tools import RagTool
from embedchain.models.data_type import DataType
from typing import Any, Optional, Type
from embedchain import App
from crewai_tools.tools.rag.rag_tool import Adapter

class CSVEmbedchainAdapter(Adapter):
    embedchain_app: App
    summarize: bool = False
    src: Optional[str] = None

    def query(self, question: str) -> str:
        where = (
            {"app_id": self.embedchain_app.config.id, "url": self.src}
            if self.src
            else None
        )
        result, sources = self.embedchain_app.query(
            question, citations=True, dry_run=(not self.summarize), where=where
        )
        if self.summarize:
            return result
        return "\n\n".join([source[0] for source in sources])

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.src = args[0] if args else None
        self.embedchain_app.add(*args, **kwargs)

class FixedCSVSearchToolSchema(BaseModel):
    """Input for CSVSearchTool."""

    query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the CSV's content",
    )

class CSVSearchToolSchema(FixedCSVSearchToolSchema):
    """Input for CSVSearchTool."""

    csv: str = Field(..., description="Mandatory csv path you want to search")

class CSVSearchToolEnhanced(RagTool):
    name: str = "Search a CSV's content"
    description: str = (
        "A tool that can be used to semantic search a query from a CSV's content."
    )
    args_schema: Type[BaseModel] = CSVSearchToolSchema

    @model_validator(mode="after")
    def _set_default_adapter(self):
        if isinstance(self.adapter, RagTool._AdapterPlaceholder):
            from embedchain import App

            app = App.from_config(config=self.config) if self.config else App()
            self.adapter = CSVEmbedchainAdapter(
                embedchain_app=app, summarize=self.summarize
            )
        return self

    def __init__(self, csv: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = None, **kwargs):
        if csv and description is None:
            kwargs["description"] = f"A tool that can be used to semantic search a query the {csv} CSV's content."
        if name:
            kwargs["name"] = name
        if description:
            kwargs["description"] = description
        if csv:
            kwargs["data_type"] = DataType.CSV
            kwargs["args_schema"] = FixedCSVSearchToolSchema
            super().__init__(**kwargs)
            self.add(csv)            
            #self._generate_description()
        else:
            super().__init__(**kwargs)

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().add(*args, **kwargs)

    def _before_run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        if "csv" in kwargs:
            self.add(kwargs["csv"])

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        if not "query" in kwargs:
            return "Please provide a query to search the CSV's content."
        if not "csv" in kwargs and not self.args_schema == FixedCSVSearchToolSchema:
            return "Please provide a CSV to search."
        return super()._run(**kwargs)
    

    

