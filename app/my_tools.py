import streamlit as st
import os
from utils import rnd_id
from crewai_tools import ScrapeElementFromWebsiteTool,TXTSearchTool,SeleniumScrapingTool,PGSearchTool,PDFSearchTool,MDXSearchTool,JSONSearchTool,GithubSearchTool,EXASearchTool,DOCXSearchTool,CSVSearchTool,ScrapeWebsiteTool, FileReadTool, DirectorySearchTool, DirectoryReadTool, CodeDocsSearchTool, YoutubeVideoSearchTool,SerperDevTool,YoutubeChannelSearchTool,WebsiteSearchTool
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

class MyCSVSearchTool(MyTool):
    def __init__(self, tool_id=None, csv=None):
        parameters = {
            'csv': {'mandatory': False}
        }
        super().__init__(tool_id, 'CSVSearchTool', "A tool that can be used to semantic search a query from a CSV's content.", parameters, csv=csv)

    def create_tool(self):
        return CSVSearchTool(csv=self.parameters.get('csv'))

class MyDocxSearchTool(MyTool):
    def __init__(self, tool_id=None, docx=None):
        parameters = {
            'docx': {'mandatory': False}
        }
        super().__init__(tool_id, 'DOCXSearchTool', "A tool that can be used to semantic search a query from a DOCX's content.", parameters, docx=docx)

    def create_tool(self):
        return DOCXSearchTool(docx=self.parameters.get('docx'))

class MyEXASearchTool(MyTool):
    def __init__(self, tool_id=None, EXA_API_KEY=None):
        parameters = {
            'EXA_API_KEY': {'mandatory': True}
        }
        super().__init__(tool_id, 'EXASearchTool', "A tool that can be used to search the internet from a search_query", parameters, EXA_API_KEY=EXA_API_KEY)

    def create_tool(self):
        os.environ['EXA_API_KEY'] = self.parameters.get('EXA_API_KEY')
        return EXASearchTool()

class MyGithubSearchTool(MyTool):
    def __init__(self, tool_id=None, github_repo=None, gh_token=None, content_types=None):
        parameters = {
            'github_repo': {'mandatory': False},
            'gh_token': {'mandatory': True},
            'content_types': {'mandatory': True}
        }
        super().__init__(tool_id, 'GithubSearchTool', "A tool that can be used to semantic search a query from a Github repository's content. Valid content_types: code,repo,pr,issue (comma sepparated)", parameters, github_repo=github_repo, gh_token=gh_token, content_types=content_types)

    def create_tool(self):
        return GithubSearchTool(
            github_repo=self.parameters.get('github_repo'),
            gh_token=self.parameters.get('gh_token'),
            content_types=self.parameters.get('search_query').split(","),
        )

class MyJSONSearchTool(MyTool):
    def __init__(self, tool_id=None, json_path=None):
        parameters = {
            'json_path': {'mandatory': False}
        }
        super().__init__(tool_id, 'JSONSearchTool', "A tool that can be used to semantic search a query from a JSON's content.", parameters, json_path=json_path)

    def create_tool(self):
        return JSONSearchTool(json_path=self.parameters.get('json_path'))

class MyMDXSearchTool(MyTool):
    def __init__(self, tool_id=None, mdx=None):
        parameters = {
            'mdx': {'mandatory': False}
        }
        super().__init__(tool_id, 'MDXSearchTool', "A tool that can be used to semantic search a query from a MDX's content.", parameters, mdx=mdx)

    def create_tool(self):
        return MDXSearchTool(mdx=self.parameters.get('mdx'))
    
class MyPDFSearchTool(MyTool):
    def __init__(self, tool_id=None, pdf=None):
        parameters = {
            'pdf': {'mandatory': False}
        }
        super().__init__(tool_id, 'PDFSearchTool', "A tool that can be used to semantic search a query from a PDF's content.", parameters, pdf=pdf)

    def create_tool(self):
        return PDFSearchTool(self.parameters.get('pdf'))

class MyPGSearchTool(MyTool):
    def __init__(self, tool_id=None, db_uri=None):
        parameters = {
            'db_uri': {'mandatory': True}
        }
        super().__init__(tool_id, 'PGSearchTool', "A tool that can be used to semantic search a query from a database table's content.", parameters, db_uri=db_uri)

    def create_tool(self):
        return PGSearchTool(self.parameters.get('db_uri'))

class MySeleniumScrapingTool(MyTool):
    def __init__(self, tool_id=None, website_url=None, css_element=None, cookie=None, wait_time=None):
        parameters = {
            'website_url': {'mandatory': False},
            'css_element': {'mandatory': False},
            'cookie': {'mandatory': False},
            'wait_time': {'mandatory': False}
        }
        super().__init__(tool_id, 'SeleniumScrapingTool', "A tool that can be used to read a specific part of website content.", parameters, website_url=website_url, css_element=css_element, cookie=cookie, wait_time=wait_time)

    def create_tool(self):
        cookie_arrayofdicts = [{k: v} for k, v in (item.strip('{}').split(':') for item in self.parameters.get('cookie').split(','))],

        return SeleniumScrapingTool(
            website_url=self.parameters.get('website_url'),
            css_element=self.parameters.get('css_element').split(","),
            cookie=cookie_arrayofdicts,
            wait_time=self.parameters.get('wait_time')
        )

class MyTXTSearchTool(MyTool):
    def __init__(self, tool_id=None, txt=None):
        parameters = {
            'txt': {'mandatory': False}
        }
        super().__init__(tool_id, 'TXTSearchTool', "A tool that can be used to semantic search a query from a TXT's content.", parameters, txt=txt)

    def create_tool(self):
        return TXTSearchTool(self.parameters.get('txt'))

class MyScrapeElementFromWebsiteTool(MyTool):
    def __init__(self, tool_id=None, website_url=None, css_element=None, cookie=None):
        parameters = {
            'website_url': {'mandatory': False},
            'css_element': {'mandatory': False},
            'cookie': {'mandatory': False}
        }
        super().__init__(tool_id, 'ScrapeElementFromWebsiteTool', "A tool that can be used to read a specific part of website content.", parameters, website_url=website_url, css_element=css_element, cookie=cookie)

    def create_tool(self):
        cookie_arrayofdicts = [{k: v} for k, v in (item.strip('{}').split(':') for item in self.parameters.get('cookie').split(','))],
        return ScrapeElementFromWebsiteTool(
            website_url=self.parameters.get('website_url'),
            css_element=self.parameters.get('css_element').split(","),
            cookie=cookie_arrayofdicts
        )
# Register all tools here
TOOL_CLASSES = {
    'SerperDevTool': MySerperDevTool,
    'WebsiteSearchTool': MyWebsiteSearchTool,
    'ScrapeWebsiteTool': MyScrapeWebsiteTool,
    'SeleniumScrapingTool': MySeleniumScrapingTool,
    'ScrapeElementFromWebsiteTool': MyScrapeElementFromWebsiteTool,

    'FileReadTool': MyFileReadTool,
    'CustomFileWriteTool': MyCustomFileWriteTool,
    'DirectorySearchTool': MyDirectorySearchTool,
    'DirectoryReadTool': MyDirectoryReadTool,

    'YoutubeVideoSearchTool': MyYoutubeVideoSearchTool,
    'YoutubeChannelSearchTool' :MyYoutubeChannelSearchTool,
    'GithubSearchTool': MyGithubSearchTool,
    'CodeDocsSearchTool': MyCodeDocsSearchTool,

    'TXTSearchTool': MyTXTSearchTool,
    'CSVSearchTool': MyCSVSearchTool,
    'DOCXSearchTool': MyDocxSearchTool, 
    'EXASearchTool': MyEXASearchTool,
    'JSONSearchTool': MyJSONSearchTool,
    'MDXSearchTool': MyMDXSearchTool,
    'PDFSearchTool': MyPDFSearchTool,
    'PGSearchTool': MyPGSearchTool    
}
