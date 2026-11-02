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
from i18n import t, get_available_languages, get_current_language, set_language, setup_language_selector
import os

def pages():
    return {
        t('page.crews'): PageCrews(),
        t('page.tools'): PageTools(),
        t('page.agents'): PageAgents(),
        t('page.tasks'): PageTasks(),
        t('page.knowledge'): PageKnowledge(),
        t('page.kickoff'): PageCrewRun(),
        t('page.results'): PageResults(),
        t('page.import_export'): PageExportCrew()
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

        if 'page' not in ss:
            ss.page = t('page.crews')

        page_keys = list(pages().keys())
        selected_page = st.radio(t('language.select'), page_keys, index=page_keys.index(ss.page) if ss.page in page_keys else 0, label_visibility="collapsed")
        if selected_page != ss.page:
            ss.page = selected_page
            st.rerun()

        setup_language_selector()

def main():
    st.set_page_config(page_title=t('page.title'), page_icon="img/favicon.ico", layout="wide")
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
