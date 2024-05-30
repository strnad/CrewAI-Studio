import streamlit as st
from streamlit import session_state as ss
from my_agent import MyAgent
import db_utils

class PageAgents:
    def __init__(self):
        self.name = "Agents"

    def create_agent(self):
        agent = MyAgent()
        if 'agents' not in ss:
            ss.agents = []
        ss.agents.append(agent)
        agent.edit = True
        db_utils.save_agent(agent)  # Save agent to database
        return agent

    def draw(self):
        with st.container():
            st.subheader(self.name)
            editing = False
            if 'agents' not in ss:
                ss.agents = db_utils.load_agents()  # Load agents from database
            for agent in ss.agents:
                agent.draw()
                if agent.edit:
                    editing = True
            if len(ss.agents) == 0:
                st.write("No agents defined yet.")
            st.button('Create agent', on_click=self.create_agent, disabled=editing)
