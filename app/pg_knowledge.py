import streamlit as st
from streamlit import session_state as ss
from my_knowledge_source import MyKnowledgeSource
import db_utils
import os
import shutil
from pathlib import Path

class PageKnowledge:
    def __init__(self):
        self.name = "Knowledge"

    def create_knowledge_source(self):
        knowledge_source = MyKnowledgeSource()
        if 'knowledge_sources' not in ss:
            ss.knowledge_sources = []
        ss.knowledge_sources.append(knowledge_source)
        knowledge_source.edit = True
        db_utils.save_knowledge_source(knowledge_source)
        return knowledge_source

    def clear_knowledge(self):
        # This will clear knowledge stores in CrewAI
        # Get CrewAI home directory
        home_dir = Path.home()
        crewai_dir = home_dir / ".crewai"
        
        # Remove knowledge folder
        knowledge_dir = crewai_dir / "knowledge"
        if knowledge_dir.exists():
            shutil.rmtree(knowledge_dir)
            st.success("Knowledge stores cleared successfully!")
        else:
            st.info("No knowledge stores found to clear.")

    def draw(self):
        st.subheader(self.name)
        
        # Instruction
        st.markdown("""
        Knowledge sources are used to provide external information to agents.
        You can create different types of knowledge sources and assign them to agents or crews.
        """)
        
        # Create knowledge directory if it doesn't exist
        os.makedirs("knowledge", exist_ok=True)
        
        # Clear knowledge button
        st.button("Clear All Knowledge Stores", on_click=self.clear_knowledge, 
                  help="This will clear all knowledge stores in CrewAI, removing cached embeddings")
        
        # Display existing knowledge sources
        editing = False
        if 'knowledge_sources' not in ss:
            ss.knowledge_sources = db_utils.load_knowledge_sources()
            
        for knowledge_source in ss.knowledge_sources:
            knowledge_source.draw()
            if knowledge_source.edit:
                editing = True
                
        if len(ss.knowledge_sources) == 0:
            st.write("No knowledge sources defined yet.")
            
        st.button('Create Knowledge Source', on_click=self.create_knowledge_source, disabled=editing)