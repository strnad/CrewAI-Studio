import streamlit as st
from streamlit import session_state as ss
from db_utils import delete_result, load_results
from datetime import datetime
from utils import rnd_id, format_result, generate_printable_view

class PageResults:
    def __init__(self):
        self.name = "Results"

    def draw(self):
        st.subheader(self.name)

        # Load results if not present in session state
        if 'results' not in ss:
            ss.results = load_results()

        # Filters
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

        # Sort results by creation time (newest first)
        filtered_results = sorted(
            filtered_results,
            key=lambda x: datetime.fromisoformat(x.created_at),
            reverse=True
        )

        # Display results
        for result in filtered_results:
            with st.expander(f"{result.crew_name} - {datetime.fromisoformat(result.created_at).strftime('%Y-%m-%d %H:%M:%S')}", expanded=False):
                st.markdown("#### Inputs")
                for key, value in result.inputs.items():
                    st.text_input(key, value, disabled=True, key=rnd_id())

                st.markdown("#### Result")
                formatted_result = format_result(result.result)

                # Show both rendered and raw versions using tabs
                tab1, tab2 = st.tabs(["Rendered", "Raw"])
                with tab1:
                    st.markdown(formatted_result)
                with tab2:
                    st.code(formatted_result)

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Delete", key=f"delete_{result.id}"):
                        delete_result(result.id)
                        ss.results.remove(result)
                        st.rerun()
                with col2:
                    # Create a button to open the printable view in a new tab
                    html_content = generate_printable_view(
                        result.crew_name,
                        result.result,
                        result.inputs,
                        formatted_result,
                        result.created_at
                    )
                    if st.button("Open Printable View", key=f"print_{result.id}"):
                        js = f"""
                        <script>
                            var printWindow = window.open('', '_blank');
                            printWindow.document.write({html_content!r});
                            printWindow.document.close();
                        </script>
                        """
                        st.components.v1.html(js, height=0)