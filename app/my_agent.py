from crewai import Agent
import streamlit as st
from utils import rnd_id, fix_columns_width
from streamlit import session_state as ss
from db_utils import save_agent, delete_agent
from llms import llm_providers_and_models, create_llm
from datetime import datetime

class MyAgent:
    def __init__(self, id=None, role=None, backstory=None, goal=None, temperature=None, allow_delegation=False, verbose=False, cache= None, llm_provider_model=None, max_iter=None, created_at=None, tools=None):
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
        self.edit_key = f'edit_{self.id}'
        if self.edit_key not in ss:
            ss[self.edit_key] = False

    @property
    def edit(self):
        return ss[self.edit_key]

    @edit.setter
    def edit(self, value):
        ss[self.edit_key] = value

    def get_crewai_agent(self):
        try:
            llm = create_llm(self.llm_provider_model, temperature=self.temperature)
        except Exception as e:
            st.error(f"Error: agent llm could not be created. {str(e)}")
            return None
        try:
            tools = [tool.create_tool() for tool in self.tools]
        except Exception as e:
            st.error(f"Error: agent tools could not be created. {str(e)}")
            return None
        try:
            return Agent(
                role=self.role,
                backstory=self.backstory,
                goal=self.goal,
                allow_delegation=self.allow_delegation,
                verbose=self.verbose,
                max_iter=self.max_iter,
                cache=self.cache,
                tools=tools,
                llm=llm
            )
        except Exception as e:
            st.error(f"Error: agent {self.role} could not be created. {str(e)}")
            return None

    def delete(self):
        ss.agents = [agent for agent in ss.agents if agent.id != self.id]
        delete_agent(self.id)

    def get_tool_display_name(self, tool):
        first_param_name = tool.get_parameter_names()[0] if tool.get_parameter_names() else None
        first_param_value = tool.parameters.get(first_param_name, '') if first_param_name else ''
        return f"{tool.name} ({first_param_value if first_param_value else tool.tool_id})"

    def is_valid(self,show_warning=False):
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

    def draw(self):
        self.validate_llm_provider_model()
        expander_title = f"{self.role[:60]} -{self.llm_provider_model.split(':')[1]}" if self.is_valid() else f"❗ {self.role[:20]} -{self.llm_provider_model.split(':')[1]}"
        if self.edit:
            with st.expander(f"Agent: {self.role}", expanded=True):
                with st.form(key=f'form_{self.id}'):
                    self.role = st.text_input("Role", value=self.role)
                    self.backstory = st.text_area("Backstory", value=self.backstory)
                    self.goal = st.text_area("Goal", value=self.goal)
                    self.allow_delegation = st.checkbox("Allow delegation", value=self.allow_delegation)
                    self.verbose = st.checkbox("Verbose", value=self.verbose)
                    self.cache = st.checkbox("Cache", value=self.cache)
                    self.llm_provider_model = st.selectbox("LLM Provider and Model", options=llm_providers_and_models(), index=llm_providers_and_models().index(self.llm_provider_model))
                    self.temperature = st.slider("Temperature", value=self.temperature, min_value=0.0, max_value=1.0)
                    self.max_iter = st.number_input("Max Iterations", value=self.max_iter, min_value=1, max_value=50)
                    enabled_tools = [tool for tool in ss.tools]
                    selected_tools = st.multiselect(
                        "Select Tools",
                        [self.get_tool_display_name(tool) for tool in enabled_tools],
                        default=[self.get_tool_display_name(tool) for tool in self.tools]
                    )
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

                self.is_valid(show_warning=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.button("Edit", on_click=self.set_editable, args=(True,), key=rnd_id())
                with col2:
                    st.button("Delete", on_click=self.delete, key=rnd_id())

    def set_editable(self, edit):
        self.edit = edit
        save_agent(self)
        if not edit:
            st.rerun()
