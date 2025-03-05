// State management
let state = {
    crews: [],
    tools: [],
    agents: [],
    tasks: [],
    toolsState: []
};

// API Functions
const api = {
    async get(endpoint) {
        try {
            const response = await fetch(`/api/${endpoint}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching ${endpoint}:`, error);
            return null;
        }
    },

    async loadAllData() {
        state.crews = await this.get('crews');
        state.tools = await this.get('tools');
        state.agents = await this.get('agents');
        state.tasks = await this.get('tasks');
        state.toolsState = await this.get('tools/state');
        renderAllData();
    }
};

// Navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-links li');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const page = link.dataset.page;
            // Update active states
            document.querySelector('.nav-links li.active').classList.remove('active');
            link.classList.add('active');
            // Hide all pages and show selected
            document.querySelector('.page.active').classList.remove('active');
            document.getElementById(`${page}-page`).classList.add('active');
        });
    });
}

// Rendering Functions
function renderCrews() {
    const crewList = document.querySelector('.crew-list');
    crewList.innerHTML = state.crews.map(crew => `
        <div class="crew-item" data-id="${crew.id}">
            <h3>${crew.name}</h3>
            <p>${crew.description || 'No description'}</p>
            <div class="crew-actions">
                <button onclick="editCrew('${crew.id}')">
                    <i class="material-icons">edit</i>
                </button>
                <button onclick="deleteCrew('${crew.id}')">
                    <i class="material-icons">delete</i>
                </button>
            </div>
        </div>
    `).join('');
}

function renderTools() {
    const toolList = document.querySelector('.tool-list');
    toolList.innerHTML = state.tools.map(tool => `
        <div class="tool-item" data-id="${tool.id}">
            <h3>${tool.name}</h3>
            <p>${tool.description || 'No description'}</p>
            <div class="tool-actions">
                <button onclick="editTool('${tool.id}')">
                    <i class="material-icons">edit</i>
                </button>
                <button onclick="deleteTool('${tool.id}')">
                    <i class="material-icons">delete</i>
                </button>
            </div>
        </div>
    `).join('');
}

function renderAgents() {
    const agentList = document.querySelector('.agent-list');
    agentList.innerHTML = state.agents.map(agent => `
        <div class="agent-item" data-id="${agent.id}">
            <h3>${agent.name}</h3>
            <p>${agent.description || 'No description'}</p>
            <div class="agent-actions">
                <button onclick="editAgent('${agent.id}')">
                    <i class="material-icons">edit</i>
                </button>
                <button onclick="deleteAgent('${agent.id}')">
                    <i class="material-icons">delete</i>
                </button>
            </div>
        </div>
    `).join('');
}

function renderTasks() {
    const taskList = document.querySelector('.task-list');
    taskList.innerHTML = state.tasks.map(task => `
        <div class="task-item" data-id="${task.id}">
            <h3>${task.name}</h3>
            <p>${task.description || 'No description'}</p>
            <div class="task-actions">
                <button onclick="editTask('${task.id}')">
                    <i class="material-icons">edit</i>
                </button>
                <button onclick="deleteTask('${task.id}')">
                    <i class="material-icons">delete</i>
                </button>
            </div>
        </div>
    `).join('');
}

function renderAllData() {
    renderCrews();
    renderTools();
    renderAgents();
    renderTasks();
    updateCrewSelects();
}

function updateCrewSelects() {
    const crewSelects = document.querySelectorAll('#crew-select, #export-crew-select');
    const options = state.crews.map(crew => 
        `<option value="${crew.id}">${crew.name}</option>`
    ).join('');
    
    crewSelects.forEach(select => {
        select.innerHTML = `<option value="">Select a crew...</option>${options}`;
    });
}

// Event Handlers
document.getElementById('add-crew').addEventListener('click', () => {
    // Implementation for adding new crew
    console.log('Add crew clicked');
});

document.getElementById('add-tool').addEventListener('click', () => {
    // Implementation for adding new tool
    console.log('Add tool clicked');
});

document.getElementById('add-agent').addEventListener('click', () => {
    // Implementation for adding new agent
    console.log('Add agent clicked');
});

document.getElementById('add-task').addEventListener('click', () => {
    // Implementation for adding new task
    console.log('Add task clicked');
});

document.getElementById('start-crew').addEventListener('click', async () => {
    const crewId = document.getElementById('crew-select').value;
    if (!crewId) {
        alert('Please select a crew first');
        return;
    }
    
    const outputDiv = document.querySelector('.execution-output');
    outputDiv.innerHTML = 'Starting crew execution...';
    
    try {
        const response = await fetch(`/api/crews/${crewId}/run`, {
            method: 'POST'
        });
        const result = await response.json();
        outputDiv.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
    } catch (error) {
        outputDiv.innerHTML = `Error: ${error.message}`;
    }
});

document.getElementById('export-crew').addEventListener('click', async () => {
    const crewId = document.getElementById('export-crew-select').value;
    if (!crewId) {
        alert('Please select a crew to export');
        return;
    }
    
    try {
        const response = await fetch(`/api/crews/${crewId}/export`);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `crew-${crewId}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert(`Error exporting crew: ${error.message}`);
    }
});

document.getElementById('import-crew').addEventListener('click', async () => {
    const fileInput = document.getElementById('import-file');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file to import');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/crews/import', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        alert('Crew imported successfully');
        api.loadAllData(); // Refresh data
    } catch (error) {
        alert(`Error importing crew: ${error.message}`);
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    api.loadAllData();
});
