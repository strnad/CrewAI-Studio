from datetime import datetime
from utils import rnd_id, fix_columns_width
from streamlit import session_state as ss
import streamlit as st
import os
import db_utils
from pathlib import Path  # Using Path for cross-platform path handling

class MyKnowledgeSource:
    def __init__(self, id=None, name=None, source_type=None, source_path=None, 
                content=None, metadata=None, chunk_size=None, chunk_overlap=None, 
                created_at=None):
        self.id = id or "KS_" + rnd_id()
        self.name = name or "Knowledge Source 1"
        self.source_type = source_type or "string"  # string, text_file, pdf, csv, excel, json, docling
        self.source_path = source_path or ""  # For file-based sources
        self.content = content or ""  # For string-based sources
        self.metadata = metadata or {}
        self.chunk_size = chunk_size or 4000
        self.chunk_overlap = chunk_overlap or 200
        self.created_at = created_at or datetime.now().isoformat()
        self.edit_key = f'edit_{self.id}'
        if self.edit_key not in ss:
            ss[self.edit_key] = False

    @property
    def edit(self):
        return ss[self.edit_key]

    @edit.setter
    def edit(self, value):
        ss[self.edit_key] = value

    def find_file(self, file_path):
        """
        Tries to find the file at various possible locations.
        Returns the correct path if found, or None if not found.
        """
        if not file_path:
            return None
        else: #simply check if the file exists in the folder knowledge
            if Path("knowledge", file_path).exists():
                return file_path
            else:
                return None

    def get_crewai_knowledge_source(self):
        # Import knowledge source classes based on type
        if self.source_type == "string":
            from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
            return StringKnowledgeSource(
                content=self.content,
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        elif self.source_type == "docling":
            from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
            return CrewDoclingSource(
                file_paths=[self.source_path],
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        else:
            # For file-based sources, find the actual file path
            actual_path = self.find_file(self.source_path)
            if not actual_path:
                raise FileNotFoundError(f"File not found: {self.source_path}")
                
            # Import the appropriate class based on source type
            if self.source_type == "text_file":
                from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
                return TextFileKnowledgeSource(
                    file_paths=[actual_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            elif self.source_type == "pdf":
                from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource               
                return PDFKnowledgeSource(
                    file_paths=[actual_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            elif self.source_type == "csv":
                from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
                return CSVKnowledgeSource(
                    file_paths=[actual_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            elif self.source_type == "excel":
                from crewai.knowledge.source.excel_knowledge_source import ExcelKnowledgeSource
                return ExcelKnowledgeSource(
                    file_paths=[actual_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            elif self.source_type == "json":
                from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
                return JSONKnowledgeSource(
                    file_paths=[actual_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            else:
                raise ValueError(f"Unsupported knowledge source type: {self.source_type}")

    def is_valid(self, show_warning=False):
        # Validate the knowledge source based on its type
        if self.source_type == "string" and not self.content:
            if show_warning:
                st.warning(f"Knowledge source {self.name} has no content")
            return False
        
        if self.source_type != "string" and self.source_type != "docling" and not self.source_path:
            if show_warning:
                st.warning(f"Knowledge source {self.name} has no source path")
            return False
            
        # For file-based sources, check if the file exists (except for docling URLs)
        if self.source_type != "string" and self.source_type != "docling":
            actual_path = self.find_file(self.source_path)
            if not actual_path:
                if show_warning:
                    st.warning(f"File not found: {self.source_path}")
                return False

            
        return True

    def delete(self):
        ss.knowledge_sources = [ks for ks in ss.knowledge_sources if ks.id != self.id]
        db_utils.delete_knowledge_source(self.id)

    def draw(self, key=None):
        source_types = {
            "string": "Text String",
            "text_file": "Text File (.txt)",
            "pdf": "PDF Document",
            "csv": "CSV File",
            "excel": "Excel File",
            "json": "JSON File",
            "docling": "DocLing (URL or file)"
        }
        
        # Create an ID for the upload field that includes both the knowledge source ID and type
        # This ensures the field is recreated when the type changes
        upload_field_id = f"uploader_{self.id}_{self.source_type}"
        
        if self.edit:
            # Use a container instead of an expander for the main form
            with st.container():
                st.subheader(f"Knowledge Source: {self.name}")
                
                # Name and type are outside the form to trigger immediate updates
                self.name = st.text_input("Name", value=self.name, key=f"name_{self.id}")
                
                prev_type = self.source_type
                self.source_type = st.selectbox(
                    "Source Type", 
                    options=list(source_types.keys()),
                    format_func=lambda x: source_types[x],
                    index=list(source_types.keys()).index(self.source_type),
                    key=f"type_{self.id}"
                )
                
                # If type changed, save immediately to trigger rerender
                if prev_type != self.source_type:
                    db_utils.save_knowledge_source(self)
                    st.rerun()
                
                # Create the form for the rest of the fields
                with st.form(key=f'form_{self.id}' if key is None else key):
                    if self.source_type == "string":
                        self.content = st.text_area("Content", value=self.content, height=200)
                    else:
                        self.source_path = st.text_input(
                            "Source Path", 
                            value=self.source_path,
                            help="Enter file path relative to the 'knowledge' directory or a URL for docling"
                        )
                        
                        # File uploader for local files
                        if self.source_type != "docling":
                            # Define file types for the uploader based on source type
                            upload_types = {
                                "text_file": "txt", 
                                "pdf": "pdf", 
                                "csv": "csv", 
                                "excel": ["xlsx", "xls"], 
                                "json": "json"
                            }
                            
                            file_type = upload_types.get(self.source_type)
                            if file_type:
                                uploaded_file = st.file_uploader(
                                    f"Upload {source_types[self.source_type]}", 
                                    type=file_type,
                                    key=upload_field_id
                                )
                                
                                if uploaded_file is not None:
                                    # Create knowledge directory if it doesn't exist
                                    os.makedirs("knowledge", exist_ok=True)
                                    
                                    # Save the uploaded file to the knowledge directory
                                    file_name = uploaded_file.name                                   
                                    file_path = os.path.join("knowledge", file_name)
                                    
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())
                                    
                                    # Set the source path to just the filename with knowledge prefix
                                    self.source_path = file_name
                    
                    # Advanced settings
                    st.subheader("Advanced Settings")
                    
                    # Chunk configuration
                    col1, col2 = st.columns(2)
                    with col1:
                        self.chunk_size = st.number_input(
                            "Chunk Size", 
                            value=self.chunk_size,
                            min_value=100,
                            max_value=8000,
                            help="Maximum size of each chunk (default: 4000)"
                        )
                    with col2:
                        self.chunk_overlap = st.number_input(
                            "Chunk Overlap", 
                            value=self.chunk_overlap,
                            min_value=0,
                            max_value=1000,
                            help="Overlap between chunks (default: 200)"
                        )
                    
                    # Metadata section
                    st.subheader("Metadata (optional)")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        metadata_key = st.text_input("Key", key=f"metadata_key_{self.id}")
                        metadata_value = st.text_input("Value", key=f"metadata_value_{self.id}")
                    with col2:
                        add_metadata = st.form_submit_button("Add Metadata")
                        if add_metadata and metadata_key:
                            self.metadata[metadata_key] = metadata_value
                            st.rerun()
                    
                    # Display current metadata
                    if self.metadata:
                        st.write("Current Metadata:")
                        for key, value in dict(self.metadata).items():
                            col1, col2, col3 = st.columns([3, 3, 1])
                            with col1:
                                st.text(key)
                            with col2:
                                st.text(value)
                            with col3:
                                remove_key = st.form_submit_button(f"Remove {key[:6]}...")
                                if remove_key:
                                    self.metadata.pop(key)
                                    st.rerun()
                    
                    # Save button for the entire form
                    submitted = st.form_submit_button("Save Knowledge Source")
                    if submitted:
                        db_utils.save_knowledge_source(self)
                        self.set_editable(False)
        else:
            fix_columns_width()
            source_name = f"{self.name}" if self.is_valid() else f"❗ {self.name}"
            with st.expander(source_name, expanded=False):
                st.markdown(f"**Name:** {self.name}")
                st.markdown(f"**Type:** {source_types[self.source_type]}")
                
                if self.source_type == "string":
                    preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
                    st.markdown(f"**Content Preview:** {preview}")
                else:
                    st.markdown(f"**Source Path:** {self.source_path}")
                
                st.markdown(f"**Chunk Size:** {self.chunk_size}")
                st.markdown(f"**Chunk Overlap:** {self.chunk_overlap}")
                
                if self.metadata:
                    st.markdown("**Metadata:**")
                    for key, value in self.metadata.items():
                        st.markdown(f"- {key}: {value}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.button("Edit", on_click=self.set_editable, args=(True,), key=rnd_id())
                with col2:
                    st.button("Delete", on_click=self.delete, key=rnd_id())
                
                self.is_valid(show_warning=True)

    def set_editable(self, edit):
        self.edit = edit
        db_utils.save_knowledge_source(self)
        if not edit:
            st.rerun()