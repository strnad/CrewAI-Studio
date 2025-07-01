import streamlit as st
from streamlit import session_state as ss
from db_utils import delete_result, load_results
from datetime import datetime
from utils import rnd_id, format_result, generate_printable_view, get_tasks_outputs_str

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
            # Format inputs for display in expander title
            input_summary = ""
            input_items = list(result.inputs.items())
            
            # Handle different numbers of input fields
            if len(input_items) == 0:
                input_summary = ""
            elif len(input_items) == 1:
                # For just one input, show more of its value
                key, value = input_items[0]
                input_summary = f" | {key}: {value[:30]}" + ("..." if len(value) > 30 else "")
            else:
                # For multiple inputs, show brief summaries
                max_chars = max(40 // len(input_items), 10)  # Adjust based on number of inputs
                input_parts = []
                
                for key, value in input_items:
                    if len(value) <= max_chars:
                        input_parts.append(f"{key}: {value}")
                    else:
                        input_parts.append(f"{key}: {value[:max_chars]}...")
                
                input_summary = " | " + " | ".join(input_parts)
            
            # Create the expander with enhanced title
            timestamp = datetime.fromisoformat(result.created_at).strftime('%Y-%m-%d %H:%M:%S')
            expander_title = f"{result.crew_name} - {timestamp}{input_summary}"
            
            with st.expander(expander_title, expanded=False):
                st.markdown("#### Inputs")
                for key, value in result.inputs.items():
                    st.text_area(key, value, disabled=True, key=rnd_id())

                st.markdown("#### Result")
                formatted_result = format_result(result.result)

                try:
                    tasks_output = result.result.get('tasks_output', None)
                    if tasks_output:
                        tasks_output_str: list[str] = list(map(lambda t: t.get("raw", ""), tasks_output))
                        tasks_descriptions = [t.get("description") for t in tasks_output]
                        tasks_result = get_tasks_outputs_str(tasks_output_str, tasks_descriptions)
                        formatted_tasks_result = format_result(tasks_result)
                    else:
                        formatted_tasks_result = ""
                except Exception:
                    formatted_tasks_result = ""

                # Show both rendered and raw versions using tabs
                tab1, tab2, tab3 = st.tabs(["Rendered", "Raw", "Rendered Complete"])
                with tab1:
                    st.markdown(formatted_result)
                with tab2:
                    st.code(formatted_result)
                with tab3:
                    st.markdown(formatted_tasks_result)

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

                    if formatted_tasks_result != "":
                        # Create a button to open the printable view in a new tab
                        html_tasks_content = generate_printable_view(
                            result.crew_name,
                            result.result,
                            result.inputs,
                            formatted_tasks_result,
                            result.created_at
                        )

                        if st.button("Open Complete Printable View", key=f"print_full_{result.id}"):
                            js = f"""
                            <script>
                                var printWindow = window.open('', '_blank');
                                printWindow.document.write({html_tasks_content!r});
                                printWindow.document.close();
                            </script>
                            """
                            st.components.v1.html(js, height=0)

