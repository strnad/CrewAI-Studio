import random
import string
from streamlit import markdown
import markdown as md
from datetime import datetime
import re
from crewai import TaskOutput


def rnd_id(length=8):
    characters = string.ascii_letters + string.digits
    random_text = ''.join(random.choice(characters) for _ in range(length))
    return random_text

def escape_quotes(s):
    return s.replace('"', '\\"').replace("'", "\\'")

def fix_columns_width():
    markdown("""
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
            </style>
            """, unsafe_allow_html=True)


def generate_printable_view(crew_name, result, inputs, formatted_result, created_at=None):
    """
    Generates a simple HTML view for printing.
    """
    if created_at is None:
        created_at = datetime.now().isoformat()
    created_at_str = datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M:%S')
    
    fixed_md = normalize_list_indentation(formatted_result)

    # Convert Markdown -> HTML
    markdown_html = md.markdown(
        fixed_md,
        extensions=['markdown.extensions.extra']  # optional: extra for tables, code, sane_lists
    )

    html_content = f"""
    <html>
        <head>
            <title>CrewAI-Studio result - {crew_name}</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    padding: 20px;
                    max-width: 800px;
                    margin: auto;
                }}
                h1 {{
                    color: #f05252;
                }}
                .section {{
                    margin: 20px 0;
                }}
                .input-item {{
                    margin: 5px 0;
                }}
                h2, h3, h4, h5, h6 {{
                    color: #333;
                    margin-top: 1em;
                }}
                code {{
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Courier New', monospace;
                }}
                pre code {{
                    background-color: #f5f5f5;
                    display: block;
                    padding: 10px;
                    white-space: pre-wrap;
                    font-family: 'Consolas', 'Courier New', monospace;
                }}
                @media print {{
                    #printButton {{
                        display: none;
                    }}
                    .page-break {{
                        page-break-before: always;
                    }}
                    body {{
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }}
                }}
            </style>
        </head>
        <body>
            <button id="printButton" onclick="window.print();" style="margin-bottom: 20px;">
                Print
            </button>

            <h1>CrewAI-Studio result</h1>
            <div class="section">
                <h2>Crew Information</h2>
                <p><strong>Crew Name:</strong> {crew_name}</p>
                <p><strong>Created:</strong> {created_at_str}</p>
            </div>
            <div class="section">
                <h2>Inputs</h2>
                {''.join(f'<div class="input-item"><strong>{k}:</strong><br><pre>{v}</pre></div>' for k, v in inputs.items())}
            </div>
            <div class="page-break"></div>
            <div class="section">
                {markdown_html}
            </div>
        </body>
    </html>
    """
    return html_content

def format_result(result):
    """
    Returns the result in a string format, extracting relevant data from nested structures if needed.
    """
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

def normalize_list_indentation(md_text: str) -> str:
    """
    Converts lines starting with multiples of 2 spaces (AI-generated) into
    multiples of 4 spaces so Python-Markdown sees nested lists correctly.
    Preserves both '-' and '*' bullets.
    """
    import re
    normalized_lines = []
    for line in md_text.splitlines():
        # match lines with leading spaces, then '*' or '-' bullet
        m = re.match(r'^(?P<spaces> +)(?P<bullet>[-*])\s+(.*)$', line)
        if m:
            spaces = len(m.group('spaces'))
            level = spaces // 2  # AI indent levels (2 spaces each)
            new_indent = ' ' * (level * 4)
            bullet = m.group('bullet')
            content = m.group(3)
            normalized_lines.append(f"{new_indent}{bullet} {content}")
        else:
            normalized_lines.append(line)
    return "\n".join(normalized_lines)


def get_tasks_outputs_str(tasks_output: list[TaskOutput | str], tasks: list = None):
    """Return a formatted string of task outputs, optionally including task descriptions."""
    strRes = ""
    for idx, task_output in enumerate(tasks_output):
        val = task_output.raw if isinstance(task_output, TaskOutput) else task_output
        desc = ""
        if tasks and idx < len(tasks):
            task = tasks[idx]
            desc = getattr(task, "description", str(task))
        title = f"#  {desc}" if desc else "#  TASK"
        strRes += f"\n\n{title}\n{val}\n\n==========\n"
    return strRes
