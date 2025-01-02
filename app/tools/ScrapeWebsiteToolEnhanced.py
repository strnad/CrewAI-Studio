from urllib.parse import urljoin
import re
from typing import Any, Optional, Type
from datetime import datetime
import requests
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class FixedScrapeWebsiteToolEnhancedSchema(BaseModel):
    """Fixed input schema - when website_url is provided in constructor."""
    pass


class ScrapeWebsiteToolEnhancedSchema(FixedScrapeWebsiteToolEnhancedSchema):
    """Dynamic input schema - what the agent sees and can set."""
    website_url: str = Field(..., description="Mandatory website URL to read the file")


class ScrapeWebsiteToolEnhanced(BaseTool):
    name: str = "Read website content"
    description: str = "A tool that can be used to read website content."
    args_schema: Type[BaseModel] = ScrapeWebsiteToolEnhancedSchema

    website_url: Optional[str] = None
    cookies: Optional[dict] = None
    show_urls: Optional[bool] = False
    css_selector: Optional[str] = None
        
    headers: Optional[dict] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(
        self,
        website_url: Optional[str] = None,
        cookies: Optional[dict] = None,
        show_urls: Optional[bool] = False,
        css_selector: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.website_url = website_url
        self.cookies = cookies
        self.show_urls = show_urls
        self.css_selector = css_selector

        if website_url is not None and "description" not in kwargs:
            self.description = (
                f"A tool that can be used to read {website_url}'s content."
            )
            self.args_schema = FixedScrapeWebsiteToolEnhancedSchema
            self._generate_description()
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""

        # Remove HTML tags while preserving line breaks
        text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        text = text.replace('<hr/>', '').replace('<hr />', '').replace('<hr>', '')
        
        # Remove all remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Convert various whitespace to spaces
        text = re.sub(r'[\t\f\r\x0b]', ' ', text)
        
        # Clean up spaces and empty lines
        text = re.sub(r' {2,}', ' ', text)
        text = text.strip()
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
        
        # Remove wicket attributes and other technical artifacts
        text = re.sub(r'wicket:[^\s>]+', '', text)
        text = re.sub(r'\s*style="[^"]*"', '', text)
        text = re.sub(r'\s*class="[^"]*"', '', text)
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # Remove empty lines while preserving intentional line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()

    def extract_text_with_structure(self, element: Tag, depth: int = 0) -> list:
        """Extract text while preserving structure."""
        results = []
        
        # Skip script and style
        if element.name in ['script', 'style']:
            return results

        # Handle direct text content
        if isinstance(element, str):
            text = self.clean_text(element)
            if text:
                results.append(("    " * depth) + text)
            return results

        # Handle link elements
        if element.name == 'a' and element.get('href'):
            href = element['href']
            if not href.startswith('javascript:'):
                text = self.clean_text(element.get_text())
                if text:
                    if self.show_urls:
                        full_url = urljoin(self.website_url, href)
                        results.append(("    " * depth) + f"<{text}: {full_url}>")
                    else:
                        results.append(("    " * depth) + text)
            return results

        # For tables, preserve structure
        if element.name == 'table':
            rows = []
            # Process headers
            header_row = element.find(['tr', 'thead'])
            headers = []
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    header_results = self.extract_text_with_structure(th, 0)
                    if header_results:
                        headers.append(" ".join(line.strip() for line in header_results))
            if headers:
                results.append(("    " * depth) + " | ".join(headers))
                results.append(("    " * depth) + ("-" * len(" | ".join(headers))))

            # Process data rows
            for tr in element.find_all('tr'):
                if tr != header_row:
                    cols = []
                    for td in tr.find_all(['td', 'th']):
                        cell_results = self.extract_text_with_structure(td, 0)
                        if cell_results:
                            cols.append(" ".join(line.strip() for line in cell_results))
                    if cols:
                        results.append(("    " * depth) + " | ".join(cols))
            return results

        # For lists, preserve bullets/numbers
        if element.name in ['ul', 'ol']:
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                prefix = f"{i}. " if element.name == 'ol' else "• "
                li_results = self.extract_text_with_structure(li, depth)
                if li_results:
                    first_line = True
                    for line in li_results:
                        if first_line:
                            results.append(("    " * depth) + prefix + line.lstrip())
                            first_line = False
                        else:
                            results.append(("    " * (depth + 1)) + line.lstrip())
            return results

        # For headings, add markdown style
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            text = self.clean_text(element.get_text())
            if text:
                level = min(int(element.name[1]), 6)
                results.append('')
                results.append(("    " * depth) + '#' * level + ' ' + text)
                results.append('')
            return results

        # Process all child elements and maintain structure
        for child in element.children:
            # Skip empty text nodes
            if isinstance(child, str) and not child.strip():
                continue
                
            child_results = self.extract_text_with_structure(child, depth)
            if not child_results:
                continue

            # Add proper spacing for block elements
            if isinstance(child, Tag) and child.name in ['div', 'p', 'section', 'article', 'header', 'footer']:
                if results and results[-1]:
                    results.append('')
                results.extend(child_results)
                if child_results[-1]:
                    results.append('')
            else:
                results.extend(child_results)

        return results

    def extract_metadata(self, soup: BeautifulSoup, url: str) -> str:
        """Extract and format page metadata."""
        metadata = [
            "### Page Metadata ###",
            f"URL: {url}",
            f"Scraping Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        # Extract title
        title = soup.find('title')
        if title and title.string and title.string.strip():
            metadata.append(f"Title: {title.string.strip()}")
            
        # Extract description
        meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
        if meta_desc and meta_desc.get('content') and meta_desc['content'].strip():
            metadata.append(f"Description: {meta_desc['content'].strip()}")
            
        # Extract language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang') and html_tag['lang'].strip():
            metadata.append(f"Language: {html_tag['lang']}")
            
        metadata.append("---")
        return "\n".join(metadata)

    def extract_pdf_metadata(self, url: str, response: requests.Response) -> str:
        """Extract and format metadata for a PDF file, including filename from response headers."""
        # Try to extract filename from Content-Disposition header
        content_disposition = response.headers.get("Content-Disposition", "")
        filename = "unknown"

        if "filename=" in content_disposition:
            # Extract filename from Content-Disposition
            filename_match = re.search(r'filename\*?="?([^;"]+)"?', content_disposition)
            if filename_match:
                filename = filename_match.group(1).strip()
        
        if filename == "unknown":
            filename = url.split("/")[-1].split("?")[0] or "unknown"

        metadata = [
            "### PDF Metadata ###",
            f"URL: {url}",
            f"Filename: {filename}",
            f"Scraping Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        return "\n".join(metadata)
    
    def pdf_url_to_text(self, url: str) -> str:
        from pdfminer.high_level import extract_text
        from io import BytesIO

        """
        Stáhne PDF soubor z URL a převede jeho obsah na text.

        Args:
            url (str): URL adresa PDF souboru.

        Returns:
            str: Text převedený z PDF.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            pdf_file = BytesIO(response.content)

            text = extract_text(pdf_file)
            return text
        except Exception as e:
            return f"Error processing PDF: {e}"
        
    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        website_url = kwargs.get("website_url", self.website_url)
        if not website_url:
            return "Error: No website URL provided"
            
        self.website_url = website_url
        css_selector = self.css_selector
        
        try:
            response = requests.get(
                website_url,
                timeout=15,
                headers=self.headers,
                cookies=self.cookies if self.cookies else {},
                allow_redirects=True
            )
            
            # Store original URL if redirected
            final_url = response.url
            was_redirected = len(response.history) > 0
            original_url = response.history[0].url if was_redirected else website_url
            
            # Create initial metadata
            metadata = [
                "### Page Metadata ###",
                f"URL: {original_url}",
                f"Status: {response.status_code}",
                f"Scraping Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            if was_redirected:
                metadata.append(f"Redirect: {original_url} -> {final_url}")
            
            # Handle binary content
            content_type = response.headers.get("Content-Type", "").lower()
            if "pdf" in content_type:
                metadata = self.extract_pdf_metadata(final_url, response)
                text = self.pdf_url_to_text(final_url)
                return metadata + "\n\n### PDF Content ###\n" + text

            if any(binary_type in content_type for binary_type in ["image", "octet-stream"]):
                filename = website_url.split("/")[-1] or "unknown"
                metadata.append("---\n")
                return "\n".join(metadata) + f"Binary file detected: {filename}"

            try:
                response.encoding = response.apparent_encoding or 'utf-8'
                parsed = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                metadata.append("---\n")
                return "\n".join(metadata) + f"\nError: Failed to parse HTML content: {str(e)}"

            metadata = self.extract_metadata(parsed, final_url)

            # Remove script and style elements
            for tag in parsed(['script', 'style']):
                tag.extract()

            # Process content based on CSS selector or whole document
            elements_to_process = []
            if css_selector:
                elements_to_process = parsed.select(css_selector)
            else:
                # Process everything in the body, or fall back to whole document
                body = parsed.find('body')
                if body:
                    elements_to_process = [body]
                else:
                    elements_to_process = [parsed]

            # Extract text from selected elements
            results = []
            for element in elements_to_process:
                results.extend(self.extract_text_with_structure(element))

            # Join results and clean up
            text = '\n'.join(line for line in results if line is not None)
            text = re.sub(r'\n{3,}', '\n\n', text)  # Normalize multiple newlines
            text = text.strip()

            return metadata + "\n" + text if text else metadata + "No meaningful content found on the page."
            
        except requests.Timeout:
            return "Error: Website request timed out"
        except requests.RequestException as e:
            return f"Error: Failed to fetch website content: {str(e)}"