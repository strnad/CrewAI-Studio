import streamlit as st
from streamlit import session_state as ss
from my_agent import MyAgent
import db_utils

class PageAgents:
    def __init__(self):
        self.name = "Agents"

    def create_agent(self, crew=None):
        agent = MyAgent()
        if 'agents' not in ss:
            ss.agents = [MyAgent]
        ss.agents.append(agent)
        agent.edit = True
        db_utils.save_agent(agent)  # Save agent to database

        if crew:
            crew.agents.append(agent)
            db_utils.save_crew(crew)

        return agent

    def draw(self):
        with st.container():
            st.subheader(self.name)
            editing = False
            if 'agents' not in ss:
                ss.agents = db_utils.load_agents()  # Load agents from database
            if 'crews' not in ss:
                ss.crews = db_utils.load_crews()  # Load crews from database

            # Dictionary to track agent assignment
            agent_assignment = {agent.id: [] for agent in ss.agents}

            # Assign agents to crews
            for crew in ss.crews:
                for agent in crew.agents:
                    agent_assignment[agent.id].append(crew.name)

            # Display agents grouped by crew in tabs
            tabs = ["All Agents"] + ["Unassigned Agents"] + [crew.name for crew in ss.crews]
            tab_objects = st.tabs(tabs)

            # Display all agents
            with tab_objects[0]:
                st.markdown("#### All Agents")
                for agent in ss.agents:
                    agent.draw()
                    if agent.edit:
                        editing = True
                st.button('Create agent', on_click=self.create_agent, disabled=editing, key="create_agent_all")

            # Display unassigned agents
            with tab_objects[1]:
                st.markdown("#### Unassigned Agents")
                unassigned_agents = [agent for agent in ss.agents if not agent_assignment[agent.id]]
                for agent in unassigned_agents:
                    unique_key = f"{agent.id}_unassigned"
                    agent.draw(key=unique_key)
                    if agent.edit:
                        editing = True
                st.button('Create agent', on_click=self.create_agent, disabled=editing, key="create_agent_unassigned")

            # Display agents grouped by crew
            for i, crew in enumerate(ss.crews, 2):
                with tab_objects[i]:
                    st.markdown(f"#### {crew.name}")
                    assigned_agents = [agent for agent in crew.agents]
                    for agent in assigned_agents:
                        unique_key = f"{agent.id}_{crew.name}"
                        agent.draw(key=unique_key)
                        if agent.edit:
                            editing = True
                    st.button('Create agent', on_click=self.create_agent, disabled=editing, kwargs={'crew': crew}, key=f"create_agent_{crew.name}")

            if len(ss.agents) == 0:
                st.write("No agents defined yet.")
                st.button('Create agent', on_click=self.create_agent, disabled=editing)

