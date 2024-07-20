import sqlite3
import os
import json
from my_tools import TOOL_CLASSES

DB_NAME = 'crewai.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            entity_type TEXT,
            data TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def initialize_db():
    if not os.path.exists(DB_NAME):
        create_tables()
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="entities"')
        table_exists = cursor.fetchone()
        if not table_exists:
            create_tables()
        conn.close()

def save_entity(entity_type, entity_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO entities (id, entity_type, data)
        VALUES (?, ?, ?)
    ''', (entity_id, entity_type, json.dumps(data)))
    conn.commit()
    conn.close()

def load_entities(entity_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entities WHERE entity_type = ?', (entity_type,))
    rows = cursor.fetchall()
    conn.close()
    return [(row['id'], json.loads(row['data'])) for row in rows]

def delete_entity(entity_type, entity_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM entities WHERE id = ? AND entity_type = ?
    ''', (entity_id, entity_type))
    conn.commit()
    conn.close()

def save_tools_state(enabled_tools):
    data = {
        'enabled_tools': enabled_tools
    }
    save_entity('tools_state', 'enabled_tools', data)

def load_tools_state():
    rows = load_entities('tools_state')
    if rows:
        return rows[0][1].get('enabled_tools', {})
    return {}

def save_agent(agent):
    data = {
        'created_at': agent.created_at,
        'role': agent.role,
        'backstory': agent.backstory,
        'goal': agent.goal,
        'allow_delegation': agent.allow_delegation,
        'verbose': agent.verbose,
        'cache': agent.cache,
        'llm_provider_model': agent.llm_provider_model,
        'temperature': agent.temperature,
        'max_iter': agent.max_iter,
        'tool_ids': [tool.tool_id for tool in agent.tools]  # Save tool IDs
    }
    save_entity('agent', agent.id, data)

def load_agents():
    from my_agent import MyAgent
    rows = load_entities('agent')
    tools_dict = {tool.tool_id: tool for tool in load_tools()}
    agents = []
    for row in rows:
        data = row[1]
        tool_ids = data.pop('tool_ids', [])
        agent = MyAgent(id=row[0], **data)
        agent.tools = [tools_dict[tool_id] for tool_id in tool_ids if tool_id in tools_dict]
        agents.append(agent)
    return sorted(agents, key=lambda x: x.created_at)

def delete_agent(agent_id):
    delete_entity('agent', agent_id)

def save_task(task):
    data = {
        'description': task.description,
        'expected_output': task.expected_output,
        'async_execution': task.async_execution,
        'agent_id': task.agent.id if task.agent else None,
        'context_from_async_tasks_ids': task.context_from_async_tasks_ids,
        'context_from_sync_tasks_ids': task.context_from_sync_tasks_ids,
        'created_at': task.created_at
    }
    save_entity('task', task.id, data)

def load_tasks():
    from my_task import MyTask
    rows = load_entities('task')
    agents_dict = {agent.id: agent for agent in load_agents()}
    tasks = []
    for row in rows:
        data = row[1]
        agent_id = data.pop('agent_id', None)
        task = MyTask(id=row[0], agent=agents_dict.get(agent_id), **data)
        tasks.append(task)
    return sorted(tasks, key=lambda x: x.created_at)

def delete_task(task_id):
    delete_entity('task', task_id)

def save_crew(crew):
    data = {
        'name': crew.name,
        'process': crew.process,
        'verbose': crew.verbose,
        'agent_ids': [agent.id for agent in crew.agents],
        'task_ids': [task.id for task in crew.tasks],
        'memory': crew.memory,
        'cache': crew.cache,
        'planning': crew.planning,
        'max_rpm' : crew.max_rpm,
        'manager_llm': crew.manager_llm,
        'manager_agent_id': crew.manager_agent.id if crew.manager_agent else None,
        'created_at': crew.created_at
    }
    save_entity('crew', crew.id, data)

def load_crews():
    from my_crew import MyCrew
    rows = load_entities('crew')
    agents_dict = {agent.id: agent for agent in load_agents()}
    tasks_dict = {task.id: task for task in load_tasks()}
    crews = []
    for row in rows:
        data = row[1]
        crew = MyCrew(
            id=row[0], 
            name=data['name'], 
            process=data['process'], 
            verbose=data['verbose'], 
            created_at=data['created_at'], 
            memory=data.get('memory'),
            cache=data.get('cache'),
            planning=data.get('planning'),
            max_rpm=data.get('max_rpm'), 
            manager_llm=data.get('manager_llm'),
            manager_agent=agents_dict.get(data.get('manager_agent_id'))
        )
        crew.agents = [agents_dict[agent_id] for agent_id in data['agent_ids'] if agent_id in agents_dict]
        crew.tasks = [tasks_dict[task_id] for task_id in data['task_ids'] if task_id in tasks_dict]
        crews.append(crew)
    return sorted(crews, key=lambda x: x.created_at)

def delete_crew(crew_id):
    delete_entity('crew', crew_id)

def save_tool(tool):
    data = {
        'name': tool.name,
        'description': tool.description,
        'parameters': tool.get_parameters()
    }
    save_entity('tool', tool.tool_id, data)

def load_tools():
    rows = load_entities('tool')
    tools = []
    for row in rows:
        data = row[1]
        tool_class = TOOL_CLASSES[data['name']]
        tool = tool_class(tool_id=row[0])
        tool.set_parameters(**data['parameters'])
        tools.append(tool)
    return tools

def delete_tool(tool_id):
    delete_entity('tool', tool_id)

def export_to_json(file_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entities')
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        entity = {
            'id': row['id'],
            'entity_type': row['entity_type'],
            'data': json.loads(row['data'])
        }
        data.append(entity)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def import_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    for entity in data:
        cursor.execute('''
            INSERT OR REPLACE INTO entities (id, entity_type, data)
            VALUES (?, ?, ?)
        ''', (entity['id'], entity['entity_type'], json.dumps(entity['data'])))

    conn.commit()
    conn.close()