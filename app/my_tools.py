import streamlit as st
import os
import ast
from utils import rnd_id
from crewai_tools import CodeInterpreterTool,ScrapeElementFromWebsiteTool,TXTSearchTool,SeleniumScrapingTool,PDFSearchTool,MDXSearchTool,JSONSearchTool,GithubSearchTool,EXASearchTool,DOCXSearchTool,CSVSearchTool,ScrapeWebsiteTool, FileReadTool, DirectorySearchTool, DirectoryReadTool, CodeDocsSearchTool, YoutubeVideoSearchTool,SerperDevTool,YoutubeChannelSearchTool,WebsiteSearchTool
from tools.CSVSearchToolEnhanced import CSVSearchToolEnhanced
from tools.CustomApiTool import CustomApiTool
from tools.CustomCodeInterpreterTool import CustomCodeInterpreterTool
from tools.CustomFileWriteTool import CustomFileWriteTool
from tools.ScrapeWebsiteToolEnhanced import ScrapeWebsiteToolEnhanced
from tools.ScrapflyScrapeWebsiteTool import ScrapflyScrapeWebsiteTool

from tools.DuckDuckGoSearchTool import DuckDuckGoSearchTool

from langchain_community.tools import YahooFinanceNewsTool
from i18n import t, get_tool_label_variants

class MyTool:
    def __init__(self, tool_id, name, description, parameters, **kwargs):
        self.tool_id = tool_id or rnd_id()
        # `name` is the STABLE internal identifier of the tool type.
        # It is a key of TOOL_CLASSES, it is persisted in the database and
        # it must NEVER be translated. Use `display_name` for anything
        # shown in the UI.
        self.name = name
        self.description = description
        self.parameters = kwargs
        self.parameters_metadata = parameters

    @property
    def display_name(self):
        """Translated, human-readable label for the UI.

        Never use this value as a lookup key — use `name` for that.
        Falls back to the stable internal name when no translation exists.
        """
        i18n_key = TOOL_I18N_KEYS.get(self.name)
        if i18n_key:
            label = t(f'tool.{i18n_key}')
            if label != f'tool.{i18n_key}':
                return label
        return self.name

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
                    st.warning(t('warning.parameter_mandatory', param=param_name, tool=self.display_name))
                return False
        return True

class MyScrapeWebsiteTool(MyTool):
    def __init__(self, tool_id=None, website_url=None):
        parameters = {
            'website_url': {'mandatory': False}
        }
        super().__init__(tool_id, 'ScrapeWebsiteTool', t('tool.scrape_website_desc'), parameters, website_url=website_url)

    def create_tool(self) -> ScrapeWebsiteTool:
        return ScrapeWebsiteTool(self.parameters.get('website_url') if self.parameters.get('website_url') else None)

class MyFileReadTool(MyTool):
    def __init__(self, tool_id=None, file_path=None):
        parameters = {
            'file_path': {'mandatory': False}
        }
        super().__init__(tool_id, 'FileReadTool', t('tool.file_read_desc'), parameters, file_path=file_path)

    def create_tool(self) -> FileReadTool:
        return FileReadTool(self.parameters.get('file_path') if self.parameters.get('file_path') else None)

class MyDirectorySearchTool(MyTool):
    def __init__(self, tool_id=None, directory=None):
        parameters = {
            'directory': {'mandatory': False}
        }
        super().__init__(tool_id, 'DirectorySearchTool', t('tool.directory_search_desc'), parameters, directory_path=directory)

    def create_tool(self) -> DirectorySearchTool:
        return DirectorySearchTool(self.parameters.get('directory') if self.parameters.get('directory') else None)

class MyDirectoryReadTool(MyTool):
    def __init__(self, tool_id=None, directory_contents=None):
        parameters = {
            'directory_contents': {'mandatory': True}
        }
        super().__init__(tool_id, 'DirectoryReadTool', t('tool.directory_read_desc'), parameters, directory_contents=directory_contents)

    def create_tool(self) -> DirectoryReadTool:
        return DirectoryReadTool(self.parameters.get('directory_contents'))

class MyCodeDocsSearchTool(MyTool):
    def __init__(self, tool_id=None, code_docs=None):
        parameters = {
            'code_docs': {'mandatory': False}
        }
        super().__init__(tool_id, 'CodeDocsSearchTool', t('tool.code_docs_search_desc'), parameters, code_docs=code_docs)

    def create_tool(self) -> CodeDocsSearchTool:
        return CodeDocsSearchTool(self.parameters.get('code_docs') if self.parameters.get('code_docs') else None)

class MyYoutubeVideoSearchTool(MyTool):
    def __init__(self, tool_id=None, youtube_video_url=None):
        parameters = {
            'youtube_video_url': {'mandatory': False}
        }
        super().__init__(tool_id, 'YoutubeVideoSearchTool', t('tool.youtube_video_search_desc'), parameters, youtube_video_url=youtube_video_url)

    def create_tool(self) -> YoutubeVideoSearchTool:
        return YoutubeVideoSearchTool(self.parameters.get('youtube_video_url') if self.parameters.get('youtube_video_url') else None)

class MySerperDevTool(MyTool):
    def __init__(self, tool_id=None, SERPER_API_KEY=None):
        parameters = {
            'SERPER_API_KEY': {'mandatory': True}
        }

        super().__init__(tool_id, 'SerperDevTool', t('tool.serper_dev_desc'), parameters)

    def create_tool(self) -> SerperDevTool:
        os.environ['SERPER_API_KEY'] = self.parameters.get('SERPER_API_KEY')
        return SerperDevTool()
    
class MyYoutubeChannelSearchTool(MyTool):
    def __init__(self, tool_id=None, youtube_channel_handle=None):
        parameters = {
            'youtube_channel_handle': {'mandatory': False}
        }
        super().__init__(tool_id, 'YoutubeChannelSearchTool', t('tool.youtube_channel_search_desc'), parameters, youtube_channel_handle=youtube_channel_handle)

    def create_tool(self) -> YoutubeChannelSearchTool:
        return YoutubeChannelSearchTool(self.parameters.get('youtube_channel_handle') if self.parameters.get('youtube_channel_handle') else None)

class MyWebsiteSearchTool(MyTool):
    def __init__(self, tool_id=None, website=None):
        parameters = {
            'website': {'mandatory': False}
        }
        super().__init__(tool_id, 'WebsiteSearchTool', t('tool.website_search_desc'), parameters, website=website)

    def create_tool(self) -> WebsiteSearchTool:
        return WebsiteSearchTool(self.parameters.get('website') if self.parameters.get('website') else None)
   
class MyCSVSearchTool(MyTool):
    def __init__(self, tool_id=None, csv=None):
        parameters = {
            'csv': {'mandatory': False}
        }
        super().__init__(tool_id, 'CSVSearchTool', t('tool.csv_search_desc'), parameters, csv=csv)

    def create_tool(self) -> CSVSearchTool:
        return CSVSearchTool(csv=self.parameters.get('csv') if self.parameters.get('csv') else None)

class MyDocxSearchTool(MyTool):
    def __init__(self, tool_id=None, docx=None):
        parameters = {
            'docx': {'mandatory': False}
        }
        super().__init__(tool_id, 'DOCXSearchTool', t('tool.docx_search_desc'), parameters, docx=docx)

    def create_tool(self) -> DOCXSearchTool:
        return DOCXSearchTool(docx=self.parameters.get('docx') if self.parameters.get('docx') else None)

class MyEXASearchTool(MyTool):
    def __init__(self, tool_id=None, EXA_API_KEY=None):
        parameters = {
            'EXA_API_KEY': {'mandatory': True}
        }
        super().__init__(tool_id, 'EXASearchTool', t('tool.exa_search_desc'), parameters, EXA_API_KEY=EXA_API_KEY)

    def create_tool(self) -> EXASearchTool:
        os.environ['EXA_API_KEY'] = self.parameters.get('EXA_API_KEY')
        return EXASearchTool()

class MyGithubSearchTool(MyTool):
    def __init__(self, tool_id=None, github_repo=None, gh_token=None, content_types=None):
        parameters = {
            'github_repo': {'mandatory': False},
            'gh_token': {'mandatory': True},
            'content_types': {'mandatory': False}
        }
        super().__init__(tool_id, 'GithubSearchTool', t('tool.github_search_desc'), parameters, github_repo=github_repo, gh_token=gh_token, content_types=content_types)

    def create_tool(self) -> GithubSearchTool:
        return GithubSearchTool(
            github_repo=self.parameters.get('github_repo') if self.parameters.get('github_repo') else None,
            gh_token=self.parameters.get('gh_token'),
            content_types=self.parameters.get('search_query').split(",") if self.parameters.get('search_query') else ["code", "repo", "pr", "issue"]
        )

class MyJSONSearchTool(MyTool):
    def __init__(self, tool_id=None, json_path=None):
        parameters = {
            'json_path': {'mandatory': False}
        }
        super().__init__(tool_id, 'JSONSearchTool', t('tool.json_search_desc'), parameters, json_path=json_path)

    def create_tool(self) -> JSONSearchTool:
        return JSONSearchTool(json_path=self.parameters.get('json_path') if self.parameters.get('json_path') else None)

class MyMDXSearchTool(MyTool):
    def __init__(self, tool_id=None, mdx=None):
        parameters = {
            'mdx': {'mandatory': False}
        }
        super().__init__(tool_id, 'MDXSearchTool', t('tool.mdx_search_desc'), parameters, mdx=mdx)

    def create_tool(self) -> MDXSearchTool:
        return MDXSearchTool(mdx=self.parameters.get('mdx') if self.parameters.get('mdx') else None)
    
class MyPDFSearchTool(MyTool):
    def __init__(self, tool_id=None, pdf=None):
        parameters = {
            'pdf': {'mandatory': False}
        }
        super().__init__(tool_id, 'PDFSearchTool', t('tool.pdf_search_desc'), parameters, pdf=pdf)

    def create_tool(self) -> PDFSearchTool:
        return PDFSearchTool(self.parameters.get('pdf') if self.parameters.get('pdf') else None)

class MySeleniumScrapingTool(MyTool):
    def __init__(self, tool_id=None, website_url=None, css_element=None, cookie=None, wait_time=None):
        parameters = {
            'website_url': {'mandatory': False},
            'css_element': {'mandatory': False},
            'cookie': {'mandatory': False},
            'wait_time': {'mandatory': False}
        }
        super().__init__(
            tool_id,
            'SeleniumScrapingTool',
            t('tool.selenium_scraping_desc'),
            parameters,
            website_url=website_url,
            css_element=css_element,
            cookie=cookie,
            wait_time=wait_time
)
    def create_tool(self) -> SeleniumScrapingTool:
        cookie_arrayofdicts = [{k: v} for k, v in (item.strip('{}').split(':') for item in self.parameters.get('cookie', '').split(','))] if self.parameters.get('cookie') else None

        return SeleniumScrapingTool(
            website_url=self.parameters.get('website_url') if self.parameters.get('website_url') else None,
            css_element=self.parameters.get('css_element').split(',') if self.parameters.get('css_element') else None,
            cookie=cookie_arrayofdicts,
            wait_time=self.parameters.get('wait_time') if self.parameters.get('wait_time') else 10
        )

class MyTXTSearchTool(MyTool):
    def __init__(self, tool_id=None, txt=None):
        parameters = {
            'txt': {'mandatory': False}
        }
        super().__init__(tool_id, 'TXTSearchTool', t('tool.txt_search_desc'), parameters, txt=txt)

    def create_tool(self) -> TXTSearchTool:
        return TXTSearchTool(self.parameters.get('txt'))

class MyScrapeElementFromWebsiteTool(MyTool):
    def __init__(self, tool_id=None, website_url=None, css_element=None, cookie=None):
        parameters = {
            'website_url': {'mandatory': False},
            'css_element': {'mandatory': False},
            'cookie': {'mandatory': False}
        }
        super().__init__(
            tool_id,
            'ScrapeElementFromWebsiteTool',
            t('tool.scrape_element_from_website_desc'),
            parameters,
            website_url=website_url,
            css_element=css_element,
            cookie=cookie
        )

    def create_tool(self) -> ScrapeElementFromWebsiteTool:
        cookie_arrayofdicts = [{k: v} for k, v in (item.strip('{}').split(':') for item in self.parameters.get('cookie', '').split(','))] if self.parameters.get('cookie') else None
        return ScrapeElementFromWebsiteTool(
            website_url=self.parameters.get('website_url') if self.parameters.get('website_url') else None,
            css_element=self.parameters.get('css_element').split(",") if self.parameters.get('css_element') else None,
            cookie=cookie_arrayofdicts
        )
    
class MyYahooFinanceNewsTool(MyTool):
    def __init__(self, tool_id=None):
        parameters = {}
        super().__init__(tool_id, 'YahooFinanceNewsTool', t('tool.yahoo_finance_news_desc'), parameters)

    def create_tool(self) -> YahooFinanceNewsTool:
        return YahooFinanceNewsTool()
    
class MyCustomApiTool(MyTool):
    def __init__(self, tool_id=None, base_url=None, headers=None, query_params=None):
        parameters = {
            'base_url': {'mandatory': False},
            'headers': {'mandatory': False},
            'query_params': {'mandatory': False}
        }
        super().__init__(tool_id, 'CustomApiTool', t('tool.custom_api_desc'), parameters, base_url=base_url, headers=headers, query_params=query_params)

    @staticmethod
    def _parse_headers(value):
        if not value:
            return None
        if isinstance(value, dict):
            parsed = value
        else:
            try:
                parsed = ast.literal_eval(value)
            except (SyntaxError, ValueError) as exc:
                raise ValueError("headers must be a dictionary literal") from exc
        if not isinstance(parsed, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in parsed.items()
        ):
            raise ValueError("headers must be a dictionary of string keys and values")
        return parsed

    def create_tool(self) -> CustomApiTool:
        return CustomApiTool(
            base_url=self.parameters.get('base_url') if self.parameters.get('base_url') else None,
            headers=self._parse_headers(self.parameters.get('headers')),
            query_params=self.parameters.get('query_params') if self.parameters.get('query_params') else None
        )

class MyCustomFileWriteTool(MyTool):
    def __init__(self, tool_id=None, base_folder=None, filename=None):
        parameters = {
            'base_folder': {'mandatory': True},
            'filename': {'mandatory': False}
        }
        super().__init__(tool_id, 'CustomFileWriteTool', t('tool.custom_file_write_desc'), parameters,base_folder=base_folder, filename=filename)

    def create_tool(self) -> CustomFileWriteTool:
        return CustomFileWriteTool(
            base_folder=self.parameters.get('base_folder') if self.parameters.get('base_folder') else "workspace",
            filename=self.parameters.get('filename') if self.parameters.get('filename') else None
        )


class MyDuckDuckGoSearchTool(MyTool):
    def __init__(self, tool_id=None):
        parameters = {}
        super().__init__(tool_id, 'DuckDuckGoSearchTool', t('tool.duckduckgo_search_desc'), parameters)

    def create_tool(self) -> DuckDuckGoSearchTool:
        return DuckDuckGoSearchTool()


class MyCodeInterpreterTool(MyTool):
    def __init__(self, tool_id=None):
        parameters = {}
        super().__init__(tool_id, 'CodeInterpreterTool', t('tool.code_interpreter_desc'), parameters)

    def create_tool(self) -> CodeInterpreterTool:
        return CodeInterpreterTool()
    

class MyCustomCodeInterpreterTool(MyTool):
    def __init__(self, tool_id=None,workspace_dir=None):
        parameters = {
            'workspace_dir': {'mandatory': False}
        }
        super().__init__(tool_id, 'CustomCodeInterpreterTool', t('tool.custom_code_interpreter_desc'), parameters, workspace_dir=workspace_dir)

    def create_tool(self) -> CustomCodeInterpreterTool:
        return CustomCodeInterpreterTool(workspace_dir=self.parameters.get('workspace_dir') if self.parameters.get('workspace_dir') else "workspace")

class MyCSVSearchToolEnhanced(MyTool):
    def __init__(self, tool_id=None, csv=None):
        parameters = {
            'csv': {'mandatory': False}
        }
        super().__init__(tool_id, 'CSVSearchToolEnhanced', t('tool.csv_search_enhanced_desc'), parameters, csv=csv)

    def create_tool(self) -> CSVSearchToolEnhanced:
        return CSVSearchToolEnhanced(csv=self.parameters.get('csv') if self.parameters.get('csv') else None)
    
class MyScrapeWebsiteToolEnhanced(MyTool):
    def __init__(self, tool_id=None, website_url=None, cookies=None, show_urls=None, css_selector=None):
        parameters = {
            'website_url': {'mandatory': False},
            'cookies': {'mandatory': False},
            'show_urls': {'mandatory': False},
            'css_selector': {'mandatory': False}
        }
        super().__init__(tool_id, 'ScrapeWebsiteToolEnhanced', t('tool.scrape_website_enhanced_desc'), parameters, website_url=website_url, cookies=cookies, show_urls=show_urls, css_selector=css_selector)

    def create_tool(self) -> ScrapeWebsiteToolEnhanced:
        return ScrapeWebsiteToolEnhanced(
            website_url=self.parameters.get('website_url') if self.parameters.get('website_url') else None,
            cookies=self.parameters.get('cookies') if self.parameters.get('cookies') else None,
            show_urls=self.parameters.get('show_urls') if self.parameters.get('show_urls') else False,
            css_selector=self.parameters.get('css_selector') if self.parameters.get('css_selector') else None
        )

class MyScrapflyScrapeWebsiteTool(MyTool):
    def __init__(self, tool_id=None, api_key=None):
        parameters = {
            'api_key': {'mandatory': False}
        }
        super().__init__(tool_id, 'ScrapflyScrapeWebsiteTool', t('tool.scrapfly_scrape_desc'), parameters, api_key=api_key)

    def create_tool(self) -> ScrapflyScrapeWebsiteTool:
        api_key = self.parameters.get('api_key') or os.getenv('SCRAPFLY_API_KEY')
        if not api_key:
            raise ValueError("Scrapfly API key not provided and not set in .env file (SCRAPFLY_API_KEY)")
        return ScrapflyScrapeWebsiteTool(
            api_key=api_key
        )

# Register all tools here.
# The keys are STABLE internal tool identifiers: they are persisted in the
# database (see db_utils.save_tool / load_tools) and in crew JSON exports,
# so they must never be translated or renamed. UI labels are resolved
# separately via TOOL_I18N_KEYS / MyTool.display_name.
TOOL_CLASSES = {
    'DuckDuckGoSearchTool': MyDuckDuckGoSearchTool,
    'SerperDevTool': MySerperDevTool,
    'WebsiteSearchTool': MyWebsiteSearchTool,
    'ScrapeWebsiteTool': MyScrapeWebsiteTool,
    'ScrapeWebsiteToolEnhanced': MyScrapeWebsiteToolEnhanced,
    'ScrapflyScrapeWebsiteTool': MyScrapflyScrapeWebsiteTool,
    
    'SeleniumScrapingTool': MySeleniumScrapingTool,
    'ScrapeElementFromWebsiteTool': MyScrapeElementFromWebsiteTool,
    'CustomApiTool': MyCustomApiTool,
    'CodeInterpreterTool': MyCodeInterpreterTool,
    'CustomCodeInterpreterTool': MyCustomCodeInterpreterTool,
    'FileReadTool': MyFileReadTool,
    'CustomFileWriteTool': MyCustomFileWriteTool,
    'DirectorySearchTool': MyDirectorySearchTool,
    'DirectoryReadTool': MyDirectoryReadTool,

    'YoutubeVideoSearchTool': MyYoutubeVideoSearchTool,
    'YoutubeChannelSearchTool' :MyYoutubeChannelSearchTool,
    'GithubSearchTool': MyGithubSearchTool,
    'CodeDocsSearchTool': MyCodeDocsSearchTool,
    'YahooFinanceNewsTool': MyYahooFinanceNewsTool,

    'TXTSearchTool': MyTXTSearchTool,
    'CSVSearchTool': MyCSVSearchTool,
    'CSVSearchToolEnhanced': MyCSVSearchToolEnhanced,
    'DOCXSearchTool': MyDocxSearchTool, 
    'EXASearchTool': MyEXASearchTool,
    'JSONSearchTool': MyJSONSearchTool,
    'MDXSearchTool': MyMDXSearchTool,
    'PDFSearchTool': MyPDFSearchTool
}

# Maps stable tool identifiers (TOOL_CLASSES keys) to i18n keys used for
# the translated UI label (`tool.<key>`) and description (`tool.<key>_desc`).
TOOL_I18N_KEYS = {
    'DuckDuckGoSearchTool': 'duckduckgo_search',
    'SerperDevTool': 'serper_dev',
    'WebsiteSearchTool': 'website_search',
    'ScrapeWebsiteTool': 'scrape_website',
    'ScrapeWebsiteToolEnhanced': 'scrape_website_enhanced',
    'ScrapflyScrapeWebsiteTool': 'scrapfly_scrape',
    'SeleniumScrapingTool': 'selenium_scraping',
    'ScrapeElementFromWebsiteTool': 'scrape_element_from_website',
    'CustomApiTool': 'custom_api',
    'CodeInterpreterTool': 'code_interpreter',
    'CustomCodeInterpreterTool': 'custom_code_interpreter',
    'FileReadTool': 'file_read',
    'CustomFileWriteTool': 'custom_file_write',
    'DirectorySearchTool': 'directory_search',
    'DirectoryReadTool': 'directory_read',
    'YoutubeVideoSearchTool': 'youtube_video_search',
    'YoutubeChannelSearchTool': 'youtube_channel_search',
    'GithubSearchTool': 'github_search',
    'CodeDocsSearchTool': 'code_docs_search',
    'YahooFinanceNewsTool': 'yahoo_finance_news',
    'TXTSearchTool': 'txt_search',
    'CSVSearchTool': 'csv_search',
    'CSVSearchToolEnhanced': 'csv_search_enhanced',
    'DOCXSearchTool': 'docx_search',
    'EXASearchTool': 'exa_search',
    'JSONSearchTool': 'json_search',
    'MDXSearchTool': 'mdx_search',
    'PDFSearchTool': 'pdf_search',
}

# Historic name variants that may still be stored in user databases or
# crew JSON exports created with older versions of CrewAI Studio.
# Before the i18n support the persisted name was always the stable
# identifier, but between the i18n introduction and this fix the
# *translated* label (or even a raw `tool.<key>` string when the
# translation was missing) was persisted instead.
_LEGACY_NAME_OVERRIDES = {
    # my_tools.py used a `tool.scrapfly_scrape_website` key that never
    # existed in the translation files (they have `scrapfly_scrape`),
    # so the raw key string ended up persisted as the tool name.
    'tool.scrapfly_scrape_website': 'ScrapflyScrapeWebsiteTool',
}


def _build_legacy_name_map():
    """Build a mapping of every known historic tool name to its stable ID.

    Covers, for each tool:
      * the raw `tool.<i18n_key>` string (persisted when a translation
        was missing),
      * the translated label in every available language (persisted by
        versions where MyTool.name was translated).
    """
    mapping = dict(_LEGACY_NAME_OVERRIDES)
    for stable_id, i18n_key in TOOL_I18N_KEYS.items():
        mapping[f'tool.{i18n_key}'] = stable_id
        for label in get_tool_label_variants(i18n_key):
            # Never let a translated label shadow a stable identifier.
            if label and label not in TOOL_CLASSES:
                mapping[label] = stable_id
    return mapping


_LEGACY_TOOL_NAMES = None


def resolve_tool_id(name):
    """Resolve a persisted tool name to a stable TOOL_CLASSES key.

    Returns the stable identifier, or None when the name is unknown
    (callers should skip such tools gracefully instead of crashing).
    """
    if name in TOOL_CLASSES:
        return name
    global _LEGACY_TOOL_NAMES
    if _LEGACY_TOOL_NAMES is None:
        _LEGACY_TOOL_NAMES = _build_legacy_name_map()
    return _LEGACY_TOOL_NAMES.get(name)