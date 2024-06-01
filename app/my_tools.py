import streamlit as st
import os
from utils import rnd_id
from crewai_tools import ScrapeWebsiteTool, FileReadTool, DirectorySearchTool, DirectoryReadTool, CodeDocsSearchTool, YoutubeVideoSearchTool,SerperDevTool,YoutubeChannelSearchTool,WebsiteSearchTool
from custom_tools import CustomFileWriteTool
class MyTool:
    def __init__(self, tool_id, name, description, parameters, **kwargs):
        self.tool_id = tool_id or "T_" +rnd_id()
        self.name = name
        self.description = description
        self.parameters = kwargs
        self.parameters_metadata = parameters

    def create_tool(self):
        pass

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, **kwargs):
        self.parameters.update(kwargs)

    def get_parameter_names(self):
        return list(self.parameters_metadata.keys())

    def is_parameter_mandatory(self, param_name):
        return self.parameters_metadata.get(param_name, {}).get('mandatory', False)

    def is_valid(self,show_warning=False):
        for param_name, metadata in self.parameters_metadata.items():
            if metadata['mandatory'] and not self.parameters.get(param_name):
                if show_warning:
                    st.warning(f"Parameter '{param_name}' is mandatory for tool '{self.name}'")
                return False
        return True

class MyScrapeWebsiteTool(MyTool):
    def __init__(self, tool_id=None, website_url=None):
        parameters = {
            'website_url': {'mandatory': False}
        }
        super().__init__(tool_id, 'ScrapeWebsiteTool', "A tool that can be used to read website content.", parameters, website_url=website_url)

    def create_tool(self):
        return ScrapeWebsiteTool(self.parameters.get('website_url'))

class MyFileReadTool(MyTool):
    def __init__(self, tool_id=None, file_path=None):
        parameters = {
            'file_path': {'mandatory': False}
        }
        super().__init__(tool_id, 'FileReadTool', "A tool that can be used to read a file's content.", parameters, file_path=file_path)

    def create_tool(self):
        return FileReadTool(self.parameters.get('file_path'))

class MyDirectorySearchTool(MyTool):
    def __init__(self, tool_id=None, directory=None):
        parameters = {
            'directory': {'mandatory': False}
        }
        super().__init__(tool_id, 'DirectorySearchTool', "A tool that can be used to semantic search a query from a directory's content.", parameters, directory_path=directory)

    def create_tool(self):
        return DirectorySearchTool(self.parameters.get('directory'))

class MyDirectoryReadTool(MyTool):
    def __init__(self, tool_id=None, directory_contents=None):
        parameters = {
            'directory_contents': {'mandatory': True}
        }
        super().__init__(tool_id, 'DirectoryReadTool', "Use the tool to list the contents of the specified directory", parameters, directory_contents=directory_contents)

    def create_tool(self):
        return DirectoryReadTool(self.parameters.get('directory_contents'))

class MyCodeDocsSearchTool(MyTool):
    def __init__(self, tool_id=None, code_docs=None):
        parameters = {
            'code_docs': {'mandatory': False}
        }
        super().__init__(tool_id, 'CodeDocsSearchTool', "A tool that can be used to search through code documentation.", parameters, code_docs=code_docs)

    def create_tool(self):
        return CodeDocsSearchTool(self.parameters.get('code_docs'))

class MyYoutubeVideoSearchTool(MyTool):
    def __init__(self, tool_id=None, youtube_video_url=None):
        parameters = {
            'youtube_video_url': {'mandatory': False}
        }
        super().__init__(tool_id, 'YoutubeVideoSearchTool', "A tool that can be used to semantic search a query from a Youtube Video content.", parameters, youtube_video_url=youtube_video_url)

    def create_tool(self):
        return YoutubeVideoSearchTool(self.parameters.get('youtube_video_url'))

class MySerperDevTool(MyTool):
    def __init__(self, tool_id=None, SERPER_API_KEY=None):
        parameters = {
            'SERPER_API_KEY': {'mandatory': True}
        }

        super().__init__(tool_id, 'SerperDevTool', "A tool that can be used to search the internet with a search_query", parameters)

    def create_tool(self):
        os.environ['SERPER_API_KEY'] = self.parameters.get('SERPER_API_KEY')
        return SerperDevTool()
    
class MyYoutubeChannelSearchTool(MyTool):
    def __init__(self, tool_id=None, youtube_channel_handle=None):
        parameters = {
            'youtube_channel_handle': {'mandatory': False}
        }
        super().__init__(tool_id, 'YoutubeChannelSearchTool', "A tool that can be used to semantic search a query from a Youtube Channels content. Channel can be added as @channel", parameters, youtube_channel_handle=youtube_channel_handle)

    def create_tool(self):
        return YoutubeChannelSearchTool(self.parameters.get('youtube_channel_handle'))

class MyWebsiteSearchTool(MyTool):
    def __init__(self, tool_id=None, website=None):
        parameters = {
            'website': {'mandatory': False}
        }
        super().__init__(tool_id, 'WebsiteSearchTool', "A tool that can be used to semantic search a query from a specific URL content.", parameters, website=website)

    def create_tool(self):
        return WebsiteSearchTool(self.parameters.get('website'))
   
class MyCustomFileWriteTool(MyTool):
    def __init__(self, tool_id=None, allowed_directory=None):
        parameters = {'allowed_directory': {'mandatory': True}}
        super().__init__(tool_id, 'CustomFileWriteTool', "Writes the provided text content to a specified file within the allowed directory.", parameters, allowed_directory=allowed_directory)

    def create_tool(self):
        allowed_directory = self.parameters.get('allowed_directory')
        tool = CustomFileWriteTool(allowed_directory=allowed_directory)
        return tool

# Register all tools here
TOOL_CLASSES = {
    'ScrapeWebsiteTool': MyScrapeWebsiteTool,
    'FileReadTool': MyFileReadTool,
    'DirectorySearchTool': MyDirectorySearchTool,
    'DirectoryReadTool': MyDirectoryReadTool,
    'CodeDocsSearchTool': MyCodeDocsSearchTool,
    'YoutubeVideoSearchTool': MyYoutubeVideoSearchTool,
    'YoutubeChannelSearchTool' :MyYoutubeChannelSearchTool,
    'SerperDevTool': MySerperDevTool,
    'WebsiteSearchTool': MyWebsiteSearchTool,
    'CustomFileWriteTool': MyCustomFileWriteTool  
}
