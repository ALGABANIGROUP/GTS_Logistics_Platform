import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

const TaskManager = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium',
    category: 'general',
    due_date: '',
    assigned_to: ''
  });

  const API_BASE = 'http://127.0.0.1:8001/vizion';

  useEffect(() => {
    fetchTasks();
  }, [filter]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/board`);
      setTasks(response.data.tasks || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const createTask = async () => {
    try {
      const response = await axios.post(`${API_BASE}/tasks`, newTask);
      setTasks([...tasks, response.data]);
      setShowCreateForm(false);
      setNewTask({
        title: '',
        description: '',
        priority: 'medium',
        category: 'general',
        due_date: '',
        assigned_to: ''
      });
      toast.success('Task created successfully!');
    } catch (err) {
      toast.error('Failed to create task');
      console.error('Error creating task:', err);
    }
  };

  const updateTaskStatus = async (taskId, action) => {
    try {
      let endpoint = '';
      switch (action) {
        case 'start':
          endpoint = `${API_BASE}/tasks/${taskId}/start`;
          break;
        case 'complete':
          endpoint = `${API_BASE}/tasks/${taskId}/complete`;
          break;
        default:
          return;
      }

      await axios.post(endpoint);
      fetchTasks(); // Refresh tasks
      toast.success(`Task ${action}ed successfully!`);
    } catch (err) {
      toast.error(`Failed to ${action} task`);
      console.error(`Error ${action}ing task:`, err);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'shipment': return '🚚';
      case 'invoice': return '📄';
      case 'notification': return '🔔';
      case 'report': return '📊';
      case 'maintenance': return '🔧';
      default: return '📋';
    }
  };

  const filteredTasks = tasks.filter(task => {
    switch (filter) {
      case 'pending': return task.status === 'pending';
      case 'today': return new Date(task.due_date).toDateString() === new Date().toDateString();
      case 'my': return task.assigned_to === 'current_user'; // TODO: Get current user
      case 'auto': return task.type === 'auto';
      case 'done': return task.status === 'completed';
      default: return true;
    }
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600 text-xl">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Task Manager</h1>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200"
          >
            + New Task
          </button>
        </div>

        {/* Filters */}
        <div className="flex space-x-2 mb-6 overflow-x-auto">
          {[
            { key: 'all', label: 'All Tasks', count: tasks.length },
            { key: 'pending', label: 'Pending', count: tasks.filter(t => t.status === 'pending').length },
            { key: 'today', label: 'Today', count: tasks.filter(t => new Date(t.due_date).toDateString() === new Date().toDateString()).length },
            { key: 'my', label: 'My Tasks', count: tasks.filter(t => t.assigned_to === 'current_user').length },
            { key: 'auto', label: 'Auto Rules', count: tasks.filter(t => t.type === 'auto').length },
            { key: 'done', label: 'Done', count: tasks.filter(t => t.status === 'completed').length }
          ].map(({ key, label, count }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition duration-200 ${
                filter === key
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {label} {count > 0 && `(${count})`}
            </button>
          ))}
        </div>

        {/* Tasks List */}
        <div className="space-y-4">
          {filteredTasks.map(task => (
            <div key={task.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg">{getPriorityColor(task.priority)}</span>
                    <span className="text-lg">{getCategoryIcon(task.category)}</span>
                    <h3 className="text-xl font-semibold text-gray-900">{task.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      task.status === 'completed' ? 'bg-green-100 text-green-800' :
                      task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {task.status.replace('_', ' ')}
                    </span>
                  </div>

                  <p className="text-gray-600 mb-3">{task.description}</p>

                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                    <span>Assigned: {task.assigned_to || 'Unassigned'}</span>
                    <span>Type: {task.type}</span>
                  </div>
                </div>

                <div className="flex space-x-2 ml-4">
                  {task.status === 'pending' && (
                    <button
                      onClick={() => updateTaskStatus(task.id, 'start')}
                      className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition duration-200"
                    >
                      Start
                    </button>
                  )}

                  {task.status === 'in_progress' && (
                    <button
                      onClick={() => updateTaskStatus(task.id, 'complete')}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition duration-200"
                    >
                      Complete
                    </button>
                  )}

                  <button className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition duration-200">
                    Comment
                  </button>
                </div>
              </div>
            </div>
          ))}

          {filteredTasks.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">📋</div>
              <h3 className="text-xl font-medium text-gray-900 mb-2">No tasks found</h3>
              <p className="text-gray-500">Create your first task or check different filters.</p>
            </div>
          )}
        </div>

        {/* Create Task Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h2 className="text-2xl font-bold mb-4">Create New Task</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                  <input
                    type="text"
                    value={newTask.title}
                    onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Task title"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={newTask.description}
                    onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                    placeholder="Task description"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                    <select
                      value={newTask.priority}
                      onChange={(e) => setNewTask({...newTask, priority: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                    <select
                      value={newTask.category}
                      onChange={(e) => setNewTask({...newTask, category: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="general">General</option>
                      <option value="shipment">Shipment</option>
                      <option value="invoice">Invoice</option>
                      <option value="notification">Notification</option>
                      <option value="report">Report</option>
                      <option value="maintenance">Maintenance</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                  <input
                    type="datetime-local"
                    value={newTask.due_date}
                    onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={createTask}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200"
                >
                  Create Task
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskManager;