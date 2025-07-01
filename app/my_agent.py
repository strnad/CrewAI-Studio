from crewai import Agent
import streamlit as st
from utils import rnd_id, fix_columns_width
from streamlit import session_state as ss
from db_utils import save_agent, delete_agent
from llms import llm_providers_and_models, create_llm
from datetime import datetime

class MyAgent:
    def __init__(self, id=None, role=None, backstory=None, goal=None, temperature=None, allow_delegation=False, verbose=False, cache= None, llm_provider_model=None, max_iter=None, created_at=None, tools=None, knowledge_source_ids=None):
        self.id = id or "A_" + rnd_id()
        self.role = role or "Senior Researcher"
        self.backstory = backstory or "Driven by curiosity, you're at the forefront of innovation, eager to explore and share knowledge that could change the world."
        self.goal = goal or "Uncover groundbreaking technologies in AI"
        self.temperature = temperature or 0.1
        self.allow_delegation = allow_delegation if allow_delegation is not None else False
        self.verbose = verbose if verbose is not None else True
        self.llm_provider_model = llm_providers_and_models()[0] if llm_provider_model is None else llm_provider_model
        self.created_at = created_at or datetime.now().isoformat()
        self.tools = tools or []
        self.max_iter = max_iter or 25
        self.cache = cache if cache is not None else True
        self.knowledge_source_ids = knowledge_source_ids or []
        self.edit_key = f'edit_{self.id}'
        if self.edit_key not in ss:
            ss[self.edit_key] = False

    @property
    def edit(self):
        return ss[self.edit_key]

    @edit.setter
    def edit(self, value):
        ss[self.edit_key] = value

    def get_crewai_agent(self) -> Agent:
        llm = create_llm(self.llm_provider_model, temperature=self.temperature)
        tools = [tool.create_tool() for tool in self.tools]
        
        # Add knowledge sources if they exist
        knowledge_sources = []
        if 'knowledge_sources' in ss and self.knowledge_source_ids:
            valid_knowledge_source_ids = []
            
            for ks_id in self.knowledge_source_ids:
                ks = next((k for k in ss.knowledge_sources if k.id == ks_id), None)
                if ks:
                    try:
                        knowledge_sources.append(ks.get_crewai_knowledge_source())
                        valid_knowledge_source_ids.append(ks_id)
                    except Exception as e:
                        print(f"Error loading knowledge source {ks.id}: {str(e)}")
        if knowledge_sources:
            print(f"Loaded {len(knowledge_sources)} knowledge sources for agent {self.id}")
            print(knowledge_sources)
        return Agent(
            role=self.role,
            backstory=self.backstory,
            goal=self.goal,
            allow_delegation=self.allow_delegation,
            verbose=self.verbose,
            max_iter=self.max_iter,
            cache=self.cache,
            tools=tools,
            llm=llm,
            knowledge_sources=knowledge_sources if knowledge_sources else None
        )

    def delete(self):
        ss.agents = [agent for agent in ss.agents if agent.id != self.id]
        delete_agent(self.id)

    def get_tool_display_name(self, tool):
        first_param_name = tool.get_parameter_names()[0] if tool.get_parameter_names() else None
        first_param_value = tool.parameters.get(first_param_name, '') if first_param_name else ''
        return f"{tool.name} ({first_param_value if first_param_value else tool.tool_id})"

    def is_valid(self, show_warning=False):
        for tool in self.tools:
            if not tool.is_valid(show_warning=show_warning):
                if show_warning:
                    st.warning(f"Tool {tool.name} is not valid")
                return False
        return True

    def validate_llm_provider_model(self):
        available_models = llm_providers_and_models()
        if self.llm_provider_model not in available_models:
            self.llm_provider_model = available_models[0]

    def draw(self, key=None):
        self.validate_llm_provider_model()
        expander_title = f"{self.role[:60]} -{self.llm_provider_model.split(':')[1]}" if self.is_valid() else f"❗ {self.role[:20]} -{self.llm_provider_model.split(':')[1]}"
        form_key = f'form_{self.id}_{key}' if key else f'form_{self.id}'        
        if self.edit:
            with st.expander(f"Agent: {self.role}", expanded=True):
                with st.form(key=form_key):
                    self.role = st.text_input("Role", value=self.role)
                    self.backstory = st.text_area("Backstory", value=self.backstory)
                    self.goal = st.text_area("Goal", value=self.goal)
                    self.allow_delegation = st.checkbox("Allow delegation", value=self.allow_delegation)
                    self.verbose = st.checkbox("Verbose", value=self.verbose)
                    self.cache = st.checkbox("Cache", value=self.cache)
                    self.llm_provider_model = st.selectbox("LLM Provider and Model", options=llm_providers_and_models(), index=llm_providers_and_models().index(self.llm_provider_model))
                    self.temperature = st.slider("Temperature", value=self.temperature, min_value=0.0, max_value=1.0)
                    self.max_iter = st.number_input("Max Iterations", value=self.max_iter, min_value=1, max_value=100)                    
                    enabled_tools = [tool for tool in ss.tools]
                    tools_key = f"{self.id}_tools_{key}" if key else f"{self.id}_tools"
                    selected_tools = st.multiselect(
                        "Select Tools",
                        [self.get_tool_display_name(tool) for tool in enabled_tools],
                        default=[self.get_tool_display_name(tool) for tool in self.tools],
                        key=tools_key
                    )                    
                    if 'knowledge_sources' in ss and len(ss.knowledge_sources) > 0:
                        knowledge_source_options = [ks.id for ks in ss.knowledge_sources]
                        knowledge_source_labels = {ks.id: ks.name for ks in ss.knowledge_sources}
                        
                        # Filter out any knowledge source IDs that no longer exist
                        valid_knowledge_sources = [ks_id for ks_id in self.knowledge_source_ids 
                                                if ks_id in knowledge_source_options]
                        
                        # If we filtered out any IDs, update the agent's knowledge sources
                        if len(valid_knowledge_sources) != len(self.knowledge_source_ids):
                            self.knowledge_source_ids = valid_knowledge_sources
                            save_agent(self)
                        
                        # Generate a unique key for the knowledge sources multiselect
                        ks_key = f"knowledge_sources_{self.id}_{key}" if key else f"knowledge_sources_{self.id}"
                        
                        # Now use the filtered list for the multiselect with the unique key
                        selected_knowledge_sources = st.multiselect(
                            "Knowledge Sources",
                            options=knowledge_source_options,
                            default=valid_knowledge_sources,
                            format_func=lambda x: knowledge_source_labels.get(x, "Unknown"),
                            key=ks_key
                        )
                        self.knowledge_source_ids = selected_knowledge_sources                
                    submitted = st.form_submit_button("Save")
                    if submitted:
                        self.tools = [tool for tool in enabled_tools if self.get_tool_display_name(tool) in selected_tools]
                        self.set_editable(False)
        else:
            fix_columns_width()
            with st.expander(expander_title, expanded=False):
                st.markdown(f"**Role:** {self.role}")
                st.markdown(f"**Backstory:** {self.backstory}")
                st.markdown(f"**Goal:** {self.goal}")
                st.markdown(f"**Allow delegation:** {self.allow_delegation}")
                st.markdown(f"**Verbose:** {self.verbose}")
                st.markdown(f"**Cache:** {self.cache}")
                st.markdown(f"**LLM Provider and Model:** {self.llm_provider_model}")
                st.markdown(f"**Temperature:** {self.temperature}")
                st.markdown(f"**Max Iterations:** {self.max_iter}")
                st.markdown(f"**Tools:** {[self.get_tool_display_name(tool) for tool in self.tools]}")                
                # Display knowledge sources
                if self.knowledge_source_ids and 'knowledge_sources' in ss:
                    knowledge_sources = [ks for ks in ss.knowledge_sources if ks.id in self.knowledge_source_ids]
                    if knowledge_sources:
                        st.markdown("**Knowledge Sources:**")
                        for ks in knowledge_sources:
                            st.markdown(f"- {ks.name}")
                self.is_valid(show_warning=True)
                col1, col2 = st.columns(2)
                with col1:
                    btn_key = f"edit_btn_{rnd_id()}"
                    st.button("Edit", on_click=self.set_editable, args=(True,), key=btn_key)
                with col2:
                    del_key = f"del_btn_{rnd_id()}"
                    st.button("Delete", on_click=self.delete, key=del_key)

    def set_editable(self, edit):
        self.edit = edit
        save_agent(self)
        if not edit:
            st.rerun()