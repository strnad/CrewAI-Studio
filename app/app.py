import streamlit as st
from streamlit import session_state as ss
import db_utils
from pg_agents import PageAgents
from pg_tasks import PageTasks
from pg_crews import PageCrews
from pg_tools import PageTools
from pg_crew_run import PageCrewRun
from pg_export_crew import PageExportCrew
from pg_results import PageResults
from pg_knowledge import PageKnowledge
from dotenv import load_dotenv
from llms import load_secrets_fron_env
from i18n import t, get_language_options, set_language, get_current_language
import os

def pages():
    return {
        t('navigation.crews'): PageCrews(),
        t('navigation.tools'): PageTools(),
        t('navigation.agents'): PageAgents(),
        t('navigation.tasks'): PageTasks(),
        t('navigation.knowledge'): PageKnowledge(),
        t('navigation.kickoff'): PageCrewRun(),
        t('navigation.results'): PageResults(),
        t('navigation.import_export'): PageExportCrew()
    }

def load_data():
    ss.agents = db_utils.load_agents()
    ss.tasks = db_utils.load_tasks()
    ss.crews = db_utils.load_crews()
    ss.tools = db_utils.load_tools()
    ss.enabled_tools = db_utils.load_tools_state()
    ss.knowledge_sources = db_utils.load_knowledge_sources()


def draw_sidebar():
    with st.sidebar:
        st.image("img/crewai_logo.png")

        # Language selector
        lang_options = get_language_options()
        current_lang = get_current_language()

        # Create reverse mapping for display
        lang_display = {code: name for code, name in lang_options.items()}
        selected_lang_name = st.selectbox(
            "🌐 Language",
            options=list(lang_display.values()),
            index=list(lang_display.keys()).index(current_lang),
            key="language_selector"
        )

        # Get language code from selected name
        selected_lang = [code for code, name in lang_display.items() if name == selected_lang_name][0]

        # Update language if changed
        if selected_lang != current_lang:
            set_language(selected_lang)
            st.rerun()

        # Initialize default page with translation
        if 'page' not in ss:
            ss.page = t('navigation.crews')

        # Page navigation
        page_list = list(pages().keys())

        # Ensure current page is valid (handle language changes)
        if ss.page not in page_list:
            ss.page = page_list[0]

        selected_page = st.radio(
            t('navigation.page'),
            page_list,
            index=page_list.index(ss.page),
            label_visibility="collapsed"
        )

        if selected_page != ss.page:
            ss.page = selected_page
            st.rerun()
            
def main():
    # Note: page_title stays in English as it appears in browser tab
    st.set_page_config(page_title="CrewAI Studio", page_icon="img/favicon.ico", layout="wide")
    load_dotenv()
    load_secrets_fron_env()
    if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
        try:
            import agentops
            agentops.init(api_key=os.getenv('AGENTOPS_API_KEY'),auto_start_session=False)    
        except ModuleNotFoundError as e:
            ss.agentops_failed = True
            print(f"Error initializing AgentOps: {str(e)}")            
        
    db_utils.initialize_db()
    load_data()
    draw_sidebar()
    PageCrewRun.maintain_session_state() #this will persist the session state for the crew run page so crew run can be run in a separate thread
    pages()[ss.page].draw()
    
if __name__ == '__main__':
    main()
