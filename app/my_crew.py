from crewai import Crew, Process
import streamlit as st
from utils import rnd_id, fix_columns_width
from streamlit import session_state as ss
from datetime import datetime
from llms import llm_providers_and_models, create_llm
import db_utils

class MyCrew:
    def __init__(self, id=None, name="Crew name", agents=None, tasks=None, process=Process.sequential, verbose=2, manager_llm=None, created_at=None, memory=False):
        self.id = id or rnd_id()
        self.name = name
        self.agents = agents if agents is not None else []
        self.tasks = tasks if tasks is not None else []
        self.process = process
        self.verbose = verbose
        self.manager_llm = manager_llm
        self.memory = memory
        self.created_at = created_at or datetime.now().isoformat()
        self.edit_key = f'edit_{self.id}'
        if self.edit_key not in ss:
            ss[self.edit_key] = False
        self.tasks_order_key = f'tasks_order_{self.id}'
        if self.tasks_order_key not in ss:
            ss[self.tasks_order_key] = [task.id for task in self.tasks]

    @property
    def edit(self):
        return ss[self.edit_key]

    @edit.setter
    def edit(self, value):
        ss[self.edit_key] = value

    def get_crewai_crew(self, *args, **kwargs):
        crewai_agents = [agent.get_crewai_agent() for agent in self.agents]
        crewai_tasks = [task.get_crewai_task() for task in self.tasks]
        
        if self.manager_llm:
            return Crew(agents=crewai_agents, tasks=crewai_tasks, process=self.process, verbose=self.verbose, manager_llm=create_llm(self.manager_llm), memory=self.memory, *args, **kwargs)
        return Crew(agents=crewai_agents, tasks=crewai_tasks, process=self.process, verbose=self.verbose, memory=self.memory, *args, **kwargs)

    def delete(self):
        ss.crews = [crew for crew in ss.crews if crew.id != self.id]
        db_utils.delete_crew(self.id)
        #st.rerun()

    def update_name(self):
        self.name = ss[f'name_{self.id}']
        db_utils.save_crew(self)

    def update_process(self):
        self.process = ss[f'process_{self.id}']
        db_utils.save_crew(self)

    def update_tasks(self):
        selected_tasks_ids = ss[f'tasks_{self.id}']
        self.tasks = [task for task in ss.tasks if task.id in selected_tasks_ids]
        self.tasks = sorted(self.tasks, key=lambda task: selected_tasks_ids.index(task.id))
        ss[self.tasks_order_key] = selected_tasks_ids
        db_utils.save_crew(self)

    def update_verbose(self):
        self.verbose = ss[f'verbose_{self.id}']
        db_utils.save_crew(self)

    def update_agents(self):
        selected_agents = ss[f'agents_{self.id}']
        self.agents = [agent for agent in ss.agents if agent.role in selected_agents]
        db_utils.save_crew(self)

    def update_manager_llm(self):
        self.manager_llm = ss[f'manager_llm_{self.id}']
        db_utils.save_crew(self)

    def update_memory(self):
        self.memory = ss[f'memory_{self.id}']
        db_utils.save_crew(self)

    def is_valid(self, show_warning=False):
        if len(self.agents) == 0:
            if show_warning:
                st.warning(f"Crew {self.name} has no agents")
            return False
        if len(self.tasks) == 0:
            if show_warning:
                st.warning(f"Crew {self.name} has no agents")
            return False
        if any([not agent.is_valid(show_warning=show_warning) for agent in self.agents]):
            return False
        if any([not task.is_valid(show_warning=show_warning) for task in self.tasks]):
            return False
        return True
        #return (len(self.agents) > 0 and len(self.tasks) > 0) and all([agent.is_valid() for agent in self.agents]) and all([task.is_valid() for task in self.tasks])

    def draw(self):
        name_key = f"name_{self.id}"
        process_key = f"process_{self.id}"
        verbose_key = f"verbose_{self.id}"
        agents_key = f"agents_{self.id}"
        tasks_key = f"tasks_{self.id}"
        manager_llm_key = f"manager_llm_{self.id}"
        memory_key = f"memory_{self.id}"

        expander_title = f"Crew: {self.name}" if self.is_valid() else f"❗ Crew: {self.name}"

        if self.edit:
            with st.container(border=True):
                st.text_input("Name (just id, it doesn't affect anything)", value=self.name, key=name_key, on_change=self.update_name)
                st.selectbox("Process", options=[Process.sequential, Process.hierarchical], index=[Process.sequential, Process.hierarchical].index(self.process), key=process_key, on_change=self.update_process)
                st.slider("Verbosity", min_value=0, max_value=2, value=self.verbose, key=verbose_key, on_change=self.update_verbose)
                st.multiselect("Agents", options=[agent.role for agent in ss.agents], default=[agent.role for agent in self.agents], key=agents_key, on_change=self.update_agents)
                st.multiselect("Tasks", options=[task.id for task in ss.tasks], default=[task.id for task in self.tasks], format_func=lambda x: next(task.description for task in ss.tasks if task.id == x), key=tasks_key, on_change=self.update_tasks)
                st.selectbox("Manager LLM", options=llm_providers_and_models(), index=0 if self.manager_llm is None else llm_providers_and_models().index(self.manager_llm), key=manager_llm_key, on_change=self.update_manager_llm, disabled=(self.process != Process.hierarchical))
                st.checkbox("Memory", value=self.memory, key=memory_key, on_change=self.update_memory)
                st.button("Save", on_click=self.set_editable, args=(False,), key=rnd_id())


        else:
            fix_columns_width()
            with st.expander(expander_title):
                st.markdown(f"**Name:** {self.name}")
                st.markdown(f"**Process:** {self.process}")
                st.markdown(f"**Verbosity:** {self.verbose}")
                st.markdown(f"**Agents:** {[agent.role for agent in self.agents]}")
                st.markdown(f"**Tasks:** {[task.description for task in self.tasks]}")
                st.markdown(f"**Manager LLM:** {self.manager_llm}")
                st.markdown(f"**Memory:** {self.memory}")
                col1, col2 = st.columns(2)
                with col1:
                    st.button("Edit", on_click=self.set_editable, key=rnd_id(), args=(True,))
                with col2:
                    st.button("Delete", on_click=self.delete, key=rnd_id())
                self.is_valid(show_warning=True)

    def set_editable(self, edit):
        self.edit = edit
        db_utils.save_crew(self)
        # if not edit:
        #     st.rerun()

