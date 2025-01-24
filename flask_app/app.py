from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

crews = []
tools = []
agents = []
tasks = []
tools_state = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/crews', methods=['GET', 'POST'])
def get_crews():
    if request.method == 'GET':
        return jsonify(crews)
    elif request.method == 'POST':
        new_crew = request.get_json()
        crews.append(new_crew)
        return jsonify({'message': 'Crew added'}), 201

@app.route('/api/tools', methods=['GET', 'POST'])
def get_tools():
    if request.method == 'GET':
        return jsonify(tools)
    elif request.method == 'POST':
        new_tool = request.get_json()
        tools.append(new_tool)
        return jsonify({'message': 'Tool added'}), 201

@app.route('/api/agents', methods=['GET', 'POST'])
def get_agents():
    if request.method == 'GET':
        return jsonify(agents)
    elif request.method == 'POST':
        new_agent = request.get_json()
        agents.append(new_agent)
        return jsonify({'message': 'Agent added'}), 201

@app.route('/api/tasks', methods=['GET', 'POST'])
def get_tasks():
    if request.method == 'GET':
        return jsonify(tasks)
    elif request.method == 'POST':
        new_task = request.get_json()
        tasks.append(new_task)
        return jsonify({'message': 'Task added'}), 201

@app.route('/api/tools/state', methods=['GET'])
def get_tools_state():
    return jsonify(tools_state)

@app.route('/api/crews/<int:crew_id>/run', methods=['POST'])
def run_crew(crew_id):
    return jsonify({'message': f'Crew {crew_id} started'})

@app.route('/api/crews/<int:crew_id>/export', methods=['GET'])
def export_crew(crew_id):
    # Placeholder for exporting crew data
    return jsonify({'message': f'Crew {crew_id} exported'})

@app.route('/api/crews/import', methods=['POST'])
def import_crew():
    # Placeholder for importing crew data
    return jsonify({'message': 'Crew imported'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
