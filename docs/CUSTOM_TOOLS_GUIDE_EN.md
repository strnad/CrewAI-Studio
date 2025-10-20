# CrewAI Studio Custom Tools Development Guide

A complete guide for developing custom tools in CrewAI Studio.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Development Steps](#development-steps)
4. [Practical Examples](#practical-examples)
5. [Registration & Integration](#registration--integration)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### What are Custom Tools?

Custom tools in CrewAI Studio are modules that provide **specialized functions** for CrewAI Agents to use.

**Built-in Tools vs Custom Tools**:

| Category | Built-in Tools (crewai-tools) | Custom Tools (app/tools/) |
|----------|------------------------------|---------------------------|
| Location | crewai-tools package | `app/tools/` directory |
| Modification | Not possible (external package) | Possible (self-developed) |
| Examples | CSVSearchTool, PDFSearchTool | CustomApiTool, DuckDuckGoSearchTool |

### Current Custom Tools List

```
app/tools/
├── CustomApiTool.py                   # REST API calls
├── CustomCodeInterpreterTool.py       # Code execution and interpretation
├── CustomFileWriteTool.py             # File write/append
├── DuckDuckGoSearchTool.py            # Web search
├── ScrapeWebsiteToolEnhanced.py       # Web scraping (enhanced)
└── ScrapflyScrapeWebsiteTool.py       # Scrapfly-based scraping
```

---

## Architecture

### 2-Layer Structure

Custom tools in CrewAI Studio consist of **2 layers**:

```
┌─────────────────────────────────────────┐
│  Layer 2: Wrapper Class (my_tools.py)  │ ← Streamlit UI integration
│  Example: MyCustomApiTool               │
└─────────────────────────────────────────┘
              ↓ wraps
┌─────────────────────────────────────────┐
│  Layer 1: Tool Implementation           │ ← Actual logic
│  (app/tools/CustomApiTool.py)           │
│  Example: CustomApiTool (inherits BaseTool) │
└─────────────────────────────────────────┘
```

#### Layer 1: Tool Implementation (app/tools/*.py)

**Purpose**: Implement the actual business logic of the tool

**Required Elements**:
1. **Input Schema** (Pydantic BaseModel)
   - Define parameters that Agent will pass to the tool
2. **Tool Class** (inherits BaseTool)
   - `name`: Tool name
   - `description`: Tool description
   - `args_schema`: Input Schema class
   - `_run()`: Actual execution logic

#### Layer 2: Wrapper Class (app/my_tools.py)

**Purpose**: Adapter connecting Streamlit UI and Tool

**Required Elements**:
1. **Inherit MyTool**
2. **parameters_metadata**: Define configuration values from UI
3. **create_tool()**: Create Layer 1 Tool instance

---

## Development Steps

### Step 1: Define Requirements

Answer these questions:

1. **What is the tool's purpose?**
   - Example: "Call external REST API to fetch data"

2. **What inputs should the Agent provide?**
   - Example: `endpoint`, `method`, `headers`, `body`

3. **What output will the tool return?**
   - Example: `{"status_code": 200, "response": {...}}`

4. **What values should be preset in UI?**
   - Example: `base_url`, `default_headers`

---

### Step 2: Implement Layer 1 (Tool Implementation)

#### 2-1. Define Input Schema

```python
from pydantic.v1 import BaseModel, Field
from typing import Optional

class YourToolInputSchema(BaseModel):
    """Parameters passed by Agent when calling the tool"""

    # Required parameters
    query: str = Field(..., description="Query string to search")

    # Optional parameters
    max_results: int = Field(5, description="Maximum number of results")
    region: Optional[str] = Field(None, description="Search region")
```

**Important**: Must use `pydantic.v1` (CrewAI compatibility)

#### 2-2. Implement Tool Class

```python
from crewai.tools import BaseTool
from typing import Type, Optional, Any

class YourCustomTool(BaseTool):
    # 1. Required attributes
    name: str = "Your Tool Name"
    description: str = "What your tool does in detail"
    args_schema: Type[BaseModel] = YourToolInputSchema

    # 2. Custom attributes (optional, set from UI)
    base_url: Optional[str] = None
    api_key: Optional[str] = None

    # 3. Initialization method
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.api_key = api_key
        self._generate_description()  # Auto-generate description (optional)

    # 4. Execution method (Core!)
    def _run(self, query: str, max_results: int = 5, region: Optional[str] = None) -> Any:
        """
        Implement actual tool logic

        Args:
            query: Parameters defined in Input Schema
            max_results: ...
            region: ...

        Returns:
            Tool execution result (string, dict, list, etc.)
        """
        try:
            # Implement actual logic here
            result = self._perform_task(query, max_results, region)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    # 5. Helper methods (optional)
    def _perform_task(self, query, max_results, region):
        # Perform actual work
        pass
```

---

### Step 3: Implement Layer 2 (Wrapper Class)

Add to `app/my_tools.py`:

```python
class MyYourCustomTool(MyTool):
    """
    Wrapper class for UI integration
    """

    def __init__(self, tool_id=None, base_url=None, api_key=None):
        # 1. Define parameters to receive from UI
        parameters = {
            'base_url': {'mandatory': True},   # Required
            'api_key': {'mandatory': False}    # Optional
        }

        # 2. Initialize parent class
        super().__init__(
            tool_id,
            'YourCustomTool',                  # Must match TOOL_CLASSES key
            t('tools.desc_your_custom_tool'),  # i18n translation key (or direct string)
            parameters,
            base_url=base_url,
            api_key=api_key
        )

    # 3. Tool instance creation method
    def create_tool(self) -> YourCustomTool:
        return YourCustomTool(
            base_url=self.parameters.get('base_url'),
            api_key=self.parameters.get('api_key')
        )
```

---

### Step 4: Register Tool

**Top of** `app/my_tools.py` (import section):

```python
# Existing imports...
from tools.YourCustomTool import YourCustomTool
```

Add to **TOOL_CLASSES dictionary** in `app/my_tools.py`:

```python
TOOL_CLASSES = {
    # Existing tools...
    'CustomApiTool': MyCustomApiTool,
    'CustomFileWriteTool': MyCustomFileWriteTool,

    # Add new tool
    'YourCustomTool': MyYourCustomTool,  # ← Add here!
}
```

---

### Step 5: Add i18n (Optional)

`app/i18n/en.json`:

```json
{
  "tools": {
    "desc_your_custom_tool": "Description of your custom tool"
  }
}
```

`app/i18n/kr.json`:

```json
{
  "tools": {
    "desc_your_custom_tool": "커스텀 도구에 대한 설명"
  }
}
```

---

## Practical Examples

### Example 1: Simple Tool - Weather Checker

**Requirement**: Check weather for a specific city using OpenWeatherMap API

#### Layer 1: `app/tools/WeatherTool.py`

```python
from crewai.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, Optional
import requests

class WeatherToolInputSchema(BaseModel):
    """Weather query input schema"""
    city: str = Field(..., description="City name to query (e.g., Seoul, Tokyo)")
    units: str = Field("metric", description="Temperature units (metric, imperial, kelvin)")

class WeatherTool(BaseTool):
    name: str = "Weather Checker"
    description: str = "Checks current weather for a given city using OpenWeatherMap API"
    args_schema: Type[BaseModel] = WeatherToolInputSchema

    # Set from UI
    api_key: Optional[str] = None

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self._generate_description()

    def _run(self, city: str, units: str = "metric") -> str:
        """Execute weather query"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Format result
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']

            return f"Weather in {city}: {weather}, Temperature: {temp}°C, Humidity: {humidity}%"

        except Exception as e:
            return f"Error fetching weather: {str(e)}"
```

#### Layer 2: Add to `app/my_tools.py`

```python
# Add to import section
from tools.WeatherTool import WeatherTool

# Add class
class MyWeatherTool(MyTool):
    def __init__(self, tool_id=None, api_key=None):
        parameters = {
            'api_key': {'mandatory': True}
        }
        super().__init__(tool_id, 'WeatherTool',
                        'Check current weather for any city',
                        parameters, api_key=api_key)

    def create_tool(self) -> WeatherTool:
        return WeatherTool(api_key=self.parameters.get('api_key'))

# Add to TOOL_CLASSES
TOOL_CLASSES = {
    # ...
    'WeatherTool': MyWeatherTool,
}
```

---

### Example 2: Intermediate - Database Query Tool

**Requirement**: Execute SQL queries on PostgreSQL database

#### Layer 1: `app/tools/DatabaseQueryTool.py`

```python
from crewai.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseQueryToolInputSchema(BaseModel):
    """Database query input schema"""
    query: str = Field(..., description="SQL query to execute (SELECT only)")
    limit: int = Field(100, description="Maximum number of results")

class DatabaseQueryTool(BaseTool):
    name: str = "Database Query Tool"
    description: str = "Execute SELECT queries on PostgreSQL database and return results"
    args_schema: Type[BaseModel] = DatabaseQueryToolInputSchema

    # Set from UI
    connection_string: str

    def __init__(self, connection_string: str, **kwargs):
        super().__init__(**kwargs)
        self.connection_string = connection_string
        self._generate_description()

    def _run(self, query: str, limit: int = 100) -> str:
        """Execute SQL query"""
        try:
            # Security: Allow SELECT only
            if not query.strip().upper().startswith('SELECT'):
                return "Error: Only SELECT queries are allowed"

            # Add LIMIT
            if 'LIMIT' not in query.upper():
                query = f"{query} LIMIT {limit}"

            # DB connection
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Execute query
            cursor.execute(query)
            results = cursor.fetchall()

            # Cleanup
            cursor.close()
            conn.close()

            # Format results
            if not results:
                return "Query returned no results"

            return self._format_results(results)

        except Exception as e:
            return f"Database error: {str(e)}"

    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """Convert results to readable format"""
        output = f"Found {len(results)} rows:\n\n"

        for i, row in enumerate(results, 1):
            output += f"Row {i}:\n"
            for key, value in row.items():
                output += f"  {key}: {value}\n"
            output += "\n"

        return output
```

#### Layer 2: Add to `app/my_tools.py`

```python
from tools.DatabaseQueryTool import DatabaseQueryTool

class MyDatabaseQueryTool(MyTool):
    def __init__(self, tool_id=None, connection_string=None):
        parameters = {
            'connection_string': {'mandatory': True}
        }
        super().__init__(tool_id, 'DatabaseQueryTool',
                        'Execute SELECT queries on PostgreSQL database',
                        parameters, connection_string=connection_string)

    def create_tool(self) -> DatabaseQueryTool:
        return DatabaseQueryTool(
            connection_string=self.parameters.get('connection_string')
        )

TOOL_CLASSES = {
    # ...
    'DatabaseQueryTool': MyDatabaseQueryTool,
}
```

---

### Example 3: Advanced - Variable Input Schema Tool

**Requirement**: Exclude from Input Schema when file path is fixed

#### Layer 1: `app/tools/FlexibleFileTool.py`

```python
from crewai.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, Optional

# Define 2 Input Schemas
class FixedFileInputSchema(BaseModel):
    """When file path is fixed"""
    content: str = Field(..., description="Content to write to file")

class FlexibleFileInputSchema(BaseModel):
    """When Agent specifies file path"""
    filepath: str = Field(..., description="File path")
    content: str = Field(..., description="Content to write to file")

class FlexibleFileTool(BaseTool):
    name: str = "Flexible File Writer"
    description: str = "Write content to a file (flexible or fixed path)"
    args_schema: Type[BaseModel] = FlexibleFileInputSchema

    # Fixed file path (optional)
    fixed_filepath: Optional[str] = None

    def __init__(self, fixed_filepath: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.fixed_filepath = fixed_filepath

        # Change Schema if file path is fixed
        if fixed_filepath:
            self.args_schema = FixedFileInputSchema

        self._generate_description()

    def _run(self, content: str, filepath: Optional[str] = None) -> str:
        """Execute file write"""
        try:
            # Determine file path
            target_path = self.fixed_filepath or filepath

            if not target_path:
                return "Error: No filepath specified"

            # Write file
            with open(target_path, 'w') as f:
                f.write(content)

            return f"Successfully wrote to {target_path}"

        except Exception as e:
            return f"File write error: {str(e)}"
```

#### Layer 2: Add to `app/my_tools.py`

```python
from tools.FlexibleFileTool import FlexibleFileTool

class MyFlexibleFileTool(MyTool):
    def __init__(self, tool_id=None, fixed_filepath=None):
        parameters = {
            'fixed_filepath': {'mandatory': False}
        }
        super().__init__(tool_id, 'FlexibleFileTool',
                        'Write content to a file (flexible or fixed path)',
                        parameters, fixed_filepath=fixed_filepath)

    def create_tool(self) -> FlexibleFileTool:
        return FlexibleFileTool(
            fixed_filepath=self.parameters.get('fixed_filepath') if self.parameters.get('fixed_filepath') else None
        )

TOOL_CLASSES = {
    # ...
    'FlexibleFileTool': MyFlexibleFileTool,
}
```

---

## Registration & Integration

### Checklist

- [ ] **Create Layer 1 file**: `app/tools/YourTool.py`
  - [ ] Define Input Schema (use pydantic.v1)
  - [ ] Inherit BaseTool
  - [ ] Set `name`, `description`, `args_schema`
  - [ ] Implement `_run()` method

- [ ] **Register Layer 2**: `app/my_tools.py`
  - [ ] Add import (top of file)
  - [ ] Create wrapper class (inherit MyTool)
  - [ ] Implement `create_tool()` method
  - [ ] Add to `TOOL_CLASSES` dictionary

- [ ] **Add i18n** (optional)
  - [ ] `app/i18n/en.json`
  - [ ] `app/i18n/kr.json`

- [ ] **Test**
  - [ ] Check if tool is selectable in Streamlit UI
  - [ ] Test tool execution from Agent

---

## Best Practices

### 1. Input Schema Design

**DO ✅**:
```python
class GoodInputSchema(BaseModel):
    query: str = Field(..., description="Clear and specific description")
    max_results: int = Field(10, ge=1, le=100, description="Value between 1-100")
```

**DON'T ❌**:
```python
class BadInputSchema(BaseModel):
    q: str  # No description, unclear parameter name
    n: int = 10  # No range limitation
```

### 2. Error Handling

**DO ✅**:
```python
def _run(self, query: str) -> str:
    try:
        result = self._perform_task(query)
        return result
    except ValueError as e:
        return f"Invalid input: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

**DON'T ❌**:
```python
def _run(self, query: str) -> str:
    result = self._perform_task(query)  # No error handling
    return result
```

### 3. Security

**DO ✅**:
```python
def _run(self, filepath: str) -> str:
    # Validate path
    if '..' in filepath or filepath.startswith('/'):
        return "Invalid filepath"

    full_path = os.path.join(self.base_folder, filepath)

    # Prevent path traversal
    if not full_path.startswith(os.path.abspath(self.base_folder)):
        return "Access denied"
```

**DON'T ❌**:
```python
def _run(self, filepath: str) -> str:
    with open(filepath, 'r') as f:  # No path validation
        return f.read()
```

### 4. Return Value Format

**DO ✅**:
```python
def _run(self, query: str) -> str:
    results = self._search(query)

    # Human-readable format
    output = "Search Results:\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. {result['title']}\n"
        output += f"   {result['description']}\n\n"

    return output
```

**DON'T ❌**:
```python
def _run(self, query: str) -> str:
    results = self._search(query)
    return str(results)  # Just convert dict to string
```

### 5. Required Parameter Validation

**DO ✅**:
```python
class MyCustomTool(MyTool):
    def __init__(self, tool_id=None, api_key=None):
        parameters = {
            'api_key': {'mandatory': True}  # Mark as required
        }
        super().__init__(tool_id, 'CustomTool', 'Description', parameters, api_key=api_key)
```

### 6. Pydantic Version Caution

**DO ✅**:
```python
from pydantic.v1 import BaseModel, Field  # Use v1
```

**DON'T ❌**:
```python
from pydantic import BaseModel, Field  # v2 not compatible with CrewAI
```

### 7. Type Annotation

**DO ✅**:
```python
from typing import Type

class CustomTool(BaseTool):
    args_schema: Type[BaseModel] = CustomInputSchema  # Type annotation required
```

**DON'T ❌**:
```python
class CustomTool(BaseTool):
    args_schema = CustomInputSchema  # Causes Pydantic v2 error
```

---

## Troubleshooting

### Issue 1: "Field 'args_schema' defined on a base class was overridden"

**Cause**: Pydantic v2 compatibility issue

**Solution**:
```python
# Before ❌
class CustomTool(BaseTool):
    args_schema = CustomInputSchema

# After ✅
from typing import Type

class CustomTool(BaseTool):
    args_schema: Type[BaseModel] = CustomInputSchema
```

---

### Issue 2: "ModuleNotFoundError: No module named 'pydantic.v1'"

**Cause**: pydantic v1 not installed

**Solution**:
```bash
pip install 'pydantic<2.0.0'
# or
pip install pydantic==1.10.13
```

---

### Issue 3: Tool doesn't appear in UI

**Checklist**:

1. Check `app/my_tools.py` **Import section**:
   ```python
   from tools.YourTool import YourTool
   ```

2. Check **Wrapper class** is written:
   ```python
   class MyYourTool(MyTool):
       # ...
   ```

3. Check **TOOL_CLASSES** dictionary registration:
   ```python
   TOOL_CLASSES = {
       # ...
       'YourTool': MyYourTool,
   }
   ```

4. **Restart Streamlit**:
   ```bash
   # Stop with Ctrl+C then restart
   streamlit run app/app.py
   ```

---

### Issue 4: "Tool execution failed"

**Debugging**:

1. **Add print to _run() method**:
   ```python
   def _run(self, query: str) -> str:
       print(f"[DEBUG] Query: {query}")  # Check input
       try:
           result = self._perform_task(query)
           print(f"[DEBUG] Result: {result}")  # Check result
           return result
       except Exception as e:
           print(f"[ERROR] {e}")  # Check error
           return f"Error: {str(e)}"
   ```

2. **Check terminal logs**:
   - Check error messages in terminal where Streamlit runs

---

### Issue 5: Input Schema not passed to Agent

**Cause**: Missing or incorrect Input Schema definition

**Solution**:
```python
# Check required elements
class YourInputSchema(BaseModel):
    param: str = Field(..., description="Description required!")  # description required!

class YourTool(BaseTool):
    args_schema: Type[BaseModel] = YourInputSchema  # Type annotation required!
```

---

## Appendix: Reference Code Examples

### Recommended Existing Tools

| Tool | File Location | Features |
|------|--------------|----------|
| **CustomApiTool** | `app/tools/CustomApiTool.py` | Basic REST API call pattern |
| **CustomFileWriteTool** | `app/tools/CustomFileWriteTool.py` | Variable Input Schema pattern |
| **DuckDuckGoSearchTool** | `app/tools/DuckDuckGoSearchTool.py` | External library integration |
| **ScrapeWebsiteToolEnhanced** | `app/tools/ScrapeWebsiteToolEnhanced.py` | Complex logic + multiple helper methods |

### Additional Learning Resources

- **CrewAI Official Docs**: https://docs.crewai.com/core-concepts/Tools/
- **Pydantic v1 Docs**: https://docs.pydantic.dev/1.10/
- **BaseTool Source Code**: https://github.com/joaomdmoura/crewAI/blob/main/src/crewai/tools/base_tool.py

---

## Conclusion

Follow this guide to develop new custom tools.

**Development Flow Summary**:
1. Define requirements
2. Implement Layer 1 (Input Schema + Tool Class)
3. Implement Layer 2 (Wrapper Class)
4. Register (import + TOOL_CLASSES)
5. Test and debug

**If you have questions or issues**:
- Reference existing tool code
- Check CrewAI official documentation
- Search GitHub Issues for similar cases

Happy Coding! 🚀
