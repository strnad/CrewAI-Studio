import streamlit as st
from streamlit import session_state as ss
from db_utils import delete_result, load_results
from datetime import datetime
from utils import rnd_id

class PageResults:
    def __init__(self):
        self.name = "Results"

    def format_result(self, result):
        """Format the result for display."""
        if isinstance(result, dict):
            if 'result' in result:
                if isinstance(result['result'], dict):
                    if 'final_output' in result['result']:
                        return result['result']['final_output']
                    elif 'raw' in result['result']:
                        return result['result']['raw']
                    else:
                        return str(result['result'])
                elif hasattr(result['result'], 'raw'):
                    return result['result'].raw
            return str(result)
        return str(result)

    def draw(self):
        st.subheader(self.name)

        # Load results if not already in session state
        if 'results' not in ss:
            ss.results = load_results()

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            crew_filter = st.multiselect(
                "Filter by Crew",
                options=list(set(r.crew_name for r in ss.results)),
                default=[],
                key="crew_filter"
            )
        with col2:
            date_filter = st.date_input(
                "Filter by Date",
                value=None,
                key="date_filter"
            )

        # Apply filters
        filtered_results = ss.results
        if crew_filter:
            filtered_results = [r for r in filtered_results if r.crew_name in crew_filter]
        if date_filter:
            filter_date = datetime.combine(date_filter, datetime.min.time())
            filtered_results = [r for r in filtered_results if datetime.fromisoformat(r.created_at).date() == date_filter]

        # Display results
        for result in filtered_results:
            with st.expander(f"{result.crew_name} - {datetime.fromisoformat(result.created_at).strftime('%Y-%m-%d %H:%M:%S')}", expanded=False):
                st.markdown("#### Inputs")
                for key, value in result.inputs.items():
                    st.text_input(key, value, disabled=True)
                
                st.markdown("#### Result")
                formatted_result = self.format_result(result.result)
                
                # Use tabs to show both rendered and raw versions
                tab1, tab2 = st.tabs(["Rendered", "Raw"])
                with tab1:
                    st.markdown(formatted_result)
                with tab2:
                    st.code(formatted_result)

                if st.button("Delete", key=f"delete_{result.id}"):
                    delete_result(result.id)
                    ss.results.remove(result)
                    st.rerun()