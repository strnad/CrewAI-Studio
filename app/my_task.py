from crewai import Task
import streamlit as st
from utils import rnd_id, fix_columns_width
from streamlit import session_state as ss
from db_utils import save_task, delete_task
from datetime import datetime

class MyTask:
    def __init__(self, id=None, description="Task Description", expected_output="Expected output", agent=None, created_at=None):
        self.id = id or rnd_id()
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
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

    def get_crewai_task(self):
        try:
            return Task(description=self.description, expected_output=self.expected_output, agent=self.agent.get_crewai_agent())
        except Exception as e:
            st.error(f"Error: task {self.description} could not be created. {str(e)}")
            return None

    def delete(self):
        ss.tasks = [task for task in ss.tasks if task.id != self.id]
        delete_task(self.id)

    def is_valid(self, show_warning=False):
        if not self.agent:
            if show_warning:
                st.warning(f"Task {self.description} has no agent")
            return False
        if not self.agent.is_valid(show_warning):
            return False
        return True


    def draw(self):
        agent_options = [agent.role for agent in ss.agents]
        expander_title = f"Task: {self.description}" if self.is_valid() else f"❗ Task: {self.description}"

        if self.edit:
            with st.expander(expander_title, expanded=True):
                with st.form(key=f'form_{self.id}'):
                    self.description = st.text_input("Description", value=self.description)
                    self.expected_output = st.text_area("Expected output", value=self.expected_output)
                    self.agent = st.selectbox("Agent", options=ss.agents, format_func=lambda x: x.role, index=0 if self.agent is None else agent_options.index(self.agent.role))
                    submitted = st.form_submit_button("Save")
                    if submitted:
                        self.set_editable(False)
        else:
            fix_columns_width()
            with st.expander(expander_title):
                st.markdown(f"**Description:** {self.description}")
                st.markdown(f"**Expected output:** {self.expected_output}")
                st.markdown(f"**Agent:** {self.agent.role if self.agent else 'None'}")
                col1, col2 = st.columns(2)
                with col1:
                    st.button("Edit", on_click=self.set_editable, args=(True,), key=rnd_id())
                with col2:
                    st.button("Delete", on_click=self.delete, key=rnd_id())
                self.is_valid(show_warning=True)

    def set_editable(self, edit):
        self.edit = edit
        save_task(self)
        if not edit:
            st.rerun()
