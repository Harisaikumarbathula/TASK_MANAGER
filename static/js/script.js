class TodoApp {
    constructor() {
        this.currentFilter = 'all';
        this.editingTaskId = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTasks();
    }

    bindEvents() {
        // Add task form
        document.getElementById('taskForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTask();
        });

        // Filter buttons
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setFilter(e.target.dataset.filter);
            });
        });

        // Edit modal save button
        document.getElementById('saveChanges').addEventListener('click', () => {
            this.saveTaskEdit();
        });
    }

    async loadTasks() {
        try {
            this.showLoading(true);
            const response = await fetch(`/api/tasks?filter=${this.currentFilter}`);
            const tasks = await response.json();
            this.renderTasks(tasks);
        } catch (error) {
            console.error('Error loading tasks:', error);
            this.showError('Failed to load tasks');
        } finally {
            this.showLoading(false);
        }
    }

    async addTask() {
        const title = document.getElementById('taskTitle').value.trim();
        const description = document.getElementById('taskDescription').value.trim();

        if (!title) {
            this.showError('Task title is required');
            return;
        }

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title, description }),
            });

            if (response.ok) {
                document.getElementById('taskForm').reset();
                this.loadTasks();
                this.showSuccess('Task added successfully!');
            } else {
                throw new Error('Failed to add task');
            }
        } catch (error) {
            console.error('Error adding task:', error);
            this.showError('Failed to add task');
        }
    }

    async toggleTask(taskId, completed) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ completed }),
            });

            if (response.ok) {
                this.loadTasks();
                this.showSuccess(completed ? 'Task completed!' : 'Task marked as pending');
            } else {
                throw new Error('Failed to update task');
            }
        } catch (error) {
            console.error('Error updating task:', error);
            this.showError('Failed to update task');
        }
    }

    async deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }

        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                this.loadTasks();
                this.showSuccess('Task deleted successfully!');
            } else {
                throw new Error('Failed to delete task');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            this.showError('Failed to delete task');
        }
    }

    openEditModal(task) {
        this.editingTaskId = task.id;
        document.getElementById('editTitle').value = task.title;
        document.getElementById('editDescription').value = task.description || '';
        
        const modal = new bootstrap.Modal(document.getElementById('editModal'));
        modal.show();
    }

    async saveTaskEdit() {
        const title = document.getElementById('editTitle').value.trim();
        const description = document.getElementById('editDescription').value.trim();

        if (!title) {
            this.showError('Task title is required');
            return;
        }

        try {
            const response = await fetch(`/api/tasks/${this.editingTaskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title, description }),
            });

            if (response.ok) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
                modal.hide();
                this.loadTasks();
                this.showSuccess('Task updated successfully!');
            } else {
                throw new Error('Failed to update task');
            }
        } catch (error) {
            console.error('Error updating task:', error);
            this.showError('Failed to update task');
        }
    }

    setFilter(filter) {
        this.currentFilter = filter;
        
        // Update active button
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        
        this.loadTasks();
    }

    renderTasks(tasks) {
        const tasksList = document.getElementById('tasksList');
        const emptyState = document.getElementById('emptyState');

        if (tasks.length === 0) {
            tasksList.innerHTML = '';
            emptyState.classList.remove('d-none');
            return;
        }

        emptyState.classList.add('d-none');
        tasksList.innerHTML = tasks.map(task => this.createTaskHTML(task)).join('');
    }

    createTaskHTML(task) {
        const createdAt = new Date(task.created_at).toLocaleDateString();
        const completedClass = task.completed ? 'completed' : '';
        const statusBadge = task.completed ? 
            '<div class="status-badge"></div>' : 
            '<div class="status-badge pending"></div>';

        return `
            <div class="task-card ${completedClass}" style="position: relative;">
                ${statusBadge}
                <div class="card-body">
                    <div class="d-flex align-items-start">
                        <input type="checkbox" class="task-checkbox" 
                               ${task.completed ? 'checked' : ''} 
                               onchange="app.toggleTask(${task.id}, this.checked)">
                        <div class="flex-grow-1">
                            <h6 class="task-title">${this.escapeHtml(task.title)}</h6>
                            ${task.description ? `<p class="task-description">${this.escapeHtml(task.description)}</p>` : ''}
                            <small class="task-meta">
                                <i class="fas fa-calendar-alt"></i>
                                Created: ${createdAt}
                            </small>
                        </div>
                    </div>
                    <div class="task-actions mt-3">
                        <button class="btn btn-sm btn-warning" onclick="app.openEditModal(${JSON.stringify(task).replace(/"/g, '&quot;')})">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="app.deleteTask(${task.id})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                        <button class="btn btn-sm ${task.completed ? 'btn-secondary' : 'btn-success'}" 
                                onclick="app.toggleTask(${task.id}, ${!task.completed})">
                            <i class="fas ${task.completed ? 'fa-undo' : 'fa-check'}"></i>
                            ${task.completed ? 'Undo' : 'Complete'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        const tasksList = document.getElementById('tasksList');
        
        if (show) {
            spinner.classList.remove('d-none');
            tasksList.innerHTML = '';
        } else {
            spinner.classList.add('d-none');
        }
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'danger');
    }

    showToast(message, type) {
        // Create toast element
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toastId = `toast-${Date.now()}`;
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove toast after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app
const app = new TodoApp();
