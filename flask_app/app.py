from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/crews', methods=['GET'])
def get_crews():
    return jsonify([])

@app.route('/api/tools', methods=['GET'])
def get_tools():
    return jsonify([])

@app.route('/api/agents', methods=['GET'])
def get_agents():
    return jsonify([])

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify([])

@app.route('/api/tools/state', methods=['GET'])
def get_tools_state():
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
