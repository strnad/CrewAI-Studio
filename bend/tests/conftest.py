"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_llm_models():
    """Sample LLM provider/model list for testing"""
    return [
        "openai:gpt-4",
        "openai:gpt-3.5-turbo",
        "anthropic:claude-3-opus",
        "groq:mixtral-8x7b",
    ]


@pytest.fixture
def mock_tool():
    """Mock tool for testing"""
    from dataclasses import dataclass

    @dataclass
    class MockTool:
        id: str
        name: str
        parameters: dict

        def create_tool(self):
            """Mock create_tool method"""
            return f"MockTool({self.name})"

        def validate(self):
            """Mock validate method"""
            errors = []
            if not self.name:
                errors.append("Tool has no name")
            return {'errors': errors, 'warnings': [], 'is_valid': len(errors) == 0}

    return MockTool


@pytest.fixture
def mock_knowledge_source():
    """Mock knowledge source for testing"""
    from dataclasses import dataclass

    @dataclass
    class MockKnowledgeSource:
        id: str
        name: str

        def get_crewai_knowledge_source(self):
            """Mock get_crewai_knowledge_source method"""
            return f"MockKnowledgeSource({self.name})"

    return MockKnowledgeSource
