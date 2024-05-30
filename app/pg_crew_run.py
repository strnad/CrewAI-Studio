import re
import streamlit as st
from streamlit import session_state as ss

class PageCrewRun:
    def __init__(self):
        self.name = "Let crews work!"
    
    @staticmethod
    def extract_placeholders(text):
        """Extract placeholders from a string."""
        return re.findall(r'\{(.*?)\}', text)

    def get_placeholders_from_crew(self, crew):
        """Get a set of all unique placeholders used in a crew's tasks."""
        placeholders = set()
        for task in crew.tasks:
            placeholders.update(self.extract_placeholders(task.description))
            placeholders.update(self.extract_placeholders(task.expected_output))
        for agent in crew.agents:
            placeholders.update(self.extract_placeholders(agent.role))
            placeholders.update(self.extract_placeholders(agent.backstory))
            placeholders.update(self.extract_placeholders(agent.goal))
        return placeholders

    def run_crew(self, crew, inputs):
        try:
            crewai_crew = crew.get_crewai_crew(full_output=True)
            with st.spinner(f"Running crew {crew.name}..."):
                result = crewai_crew.kickoff(inputs=inputs)
            st.balloons()
            with st.expander("Final output", expanded=True):                
                st.write(result['final_output'])
            with st.expander("Full output", expanded=False):
                st.write(result)
        except Exception as e:
            st.error(f"Error running crew {crew.name}: {str(e)}")

    def get_mycrew_by_name(self, crewname):
        for crew in ss.crews:
            if crew.name == crewname:
                return crew
        return None 

    def draw_placeholders(self, crew):
        placeholders = self.get_placeholders_from_crew(crew)
        if placeholders:
            with st.container(border=True):
                st.write('Placeholders to fill in:')
                for placeholder in placeholders:
                    st.text_input(label=placeholder,autocomplete="on", key=f'placeholder_{placeholder}', value=ss.get(f'placeholder_{placeholder}', ''))

    def draw_crews(self):
        with st.container():            
            if 'crews' not in ss:
                ss.crews = []
            else:
                st.selectbox(label="Select crew to run", label_visibility="visible", options=[crew.name for crew in ss.crews], index=0, key='selected_crew_name')
    
            if len(ss.crews) == 0:
                st.write("No crews defined yet.")
            else:
                selected_crew_name = ss.selected_crew_name
                selected_crew = self.get_mycrew_by_name(selected_crew_name)
                if selected_crew:
                    self.draw_placeholders(selected_crew)
                    if not selected_crew.is_valid(show_warning=True):
                        st.error("Selected crew is not valid. Please fix the issues.")
                    if st.button('Run crew!', disabled=selected_crew.is_valid() == False):
                        inputs = {key.split('_')[1]: value for key, value in ss.items() if key.startswith('placeholder_')}
                        self.run_crew(selected_crew, inputs)

    def draw(self):
        st.subheader(self.name)
        self.draw_crews()

