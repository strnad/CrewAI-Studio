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
from i18n import t, setup_language_selector
import os

# Словарь: внутренний ID -> класс страницы
def get_pages():
    return {
        "crews": PageCrews(),
        "tools": PageTools(),
        "agents": PageAgents(),
        "tasks": PageTasks(),
        "knowledge": PageKnowledge(),
        "kickoff": PageCrewRun(),
        "results": PageResults(),
        "import_export": PageExportCrew()
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

        page_dict = get_pages()
        page_ids = list(page_dict.keys())

        # Инициализируем ID страницы, если его нет
        if 'page_id' not in ss or ss.page_id not in page_ids:
            ss.page_id = "crews"

        # Находим текущий индекс
        current_index = page_ids.index(ss.page_id)

        # Создаем радио-кнопку с жестким key, чтобы Streamlit не терял состояние
        selected_id = st.radio(
            t('language.select'),  # Скрытый лейбл
            options=page_ids,
            index=current_index,
            format_func=lambda x: t(f'page.{x}'), # <--- ВОТ ЗДЕСЬ ПЕРЕВОД
            label_visibility="collapsed",
            key="main_navigation_radio"
        )

        # Если выбрали другую страницу — обновляем ID и перезапускаем
        if selected_id != ss.page_id:
            ss.page_id = selected_id
            st.rerun()

        setup_language_selector()
        
        # Возвращаем класс текущей страницы для отрисовки
        return page_dict[ss.page_id]

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
    
    # draw_sidebar возвращает нужную страницу, и мы ее рисуем
    current_page_obj = draw_sidebar()
    
    PageCrewRun.maintain_session_state()
    current_page_obj.draw()
    
if __name__ == '__main__':
    main()