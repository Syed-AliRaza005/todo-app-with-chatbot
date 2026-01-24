'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import AuthGuard from '@/components/auth/AuthGuard';
import Header from '@/components/layout/Header';
import TaskList from '@/components/task/TaskList';
import TaskForm from '@/components/task/TaskForm';
import EmptyState from '@/components/layout/EmptyState';
import TaskFilters from '@/components/task/TaskFilters';
import StatisticsDisplay from '@/components/task/StatisticsDisplay';
import { taskApi, Task, CreateTaskRequest, UpdateTaskRequest } from '@/lib/api';
import { Task as TaskType } from '@/types/task';
import { TaskFilterOptions } from '@/types/task';

export default function DashboardPage() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<TaskType[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<TaskType[]>([]);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<TaskFilterOptions>({ status: 'all', search: '' });

  // Fetch tasks
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setIsLoading(true);
        const fetchedTasks = await taskApi.getAllTasks();
        setTasks(fetchedTasks);
      } catch (err) {
        console.error('Error fetching tasks:', err);
        setError('Failed to load tasks. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchTasks();
    }
  }, [user]);

  // Apply filters
  useEffect(() => {
    let result = [...tasks];

    // Apply status filter
    if (filters.status && filters.status !== 'all') {
      if (filters.status === 'Completed') {
        result = result.filter(task => task.status === 'Completed');
      } else if (filters.status === 'Pending') {
        result = result.filter(task => task.status === 'Pending');
      }
    }

    // Apply search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      result = result.filter(task =>
        task.title.toLowerCase().includes(searchLower) ||
        (task.description && task.description.toLowerCase().includes(searchLower))
      );
    }

    setFilteredTasks(result);
  }, [tasks, filters]);

  // Handle task creation
  const handleCreateTask = async (taskData: CreateTaskRequest | UpdateTaskRequest) => {
    try {
      const newTask = await taskApi.createTask(taskData as CreateTaskRequest);
      setTasks([newTask, ...tasks]);
      setShowTaskForm(false);
    } catch (err) {
      console.error('Error creating task:', err);
      // In a real app, you might show an error toast here
    }
  };

  // Handle task update
  const handleUpdateTask = async (taskData: CreateTaskRequest | UpdateTaskRequest) => {
    if (!editingTask) return;

    try {
      const updatedTask = await taskApi.updateTask(editingTask.id, taskData as UpdateTaskRequest);
      setTasks(tasks.map(task =>
        task.id === editingTask.id ? updatedTask : task
      ));
      setEditingTask(null);
      setShowTaskForm(false);
    } catch (err) {
      console.error('Error updating task:', err);
      // In a real app, you might show an error toast here
    }
  };

  // Handle task toggle
  const handleToggleTask = async (id: string) => {
    try {
      const updatedTask = await taskApi.toggleTaskCompletion(id);
      setTasks(tasks.map(task =>
        task.id === id ? updatedTask : task
      ));
    } catch (err) {
      console.error('Error toggling task:', err);
      // In a real app, you might show an error toast here
    }
  };

  // Handle task deletion
  const handleDeleteTask = async (id: string) => {
    try {
      await taskApi.deleteTask(id);
      setTasks(tasks.filter(task => task.id !== id));
    } catch (err) {
      console.error('Error deleting task:', err);
      // In a real app, you might show an error toast here
    }
  };

  // Handle filter changes
  const handleFilterChange = (newFilters: TaskFilterOptions) => {
    setFilters(newFilters);
  };

  // Handle task edit
  const handleEditTask = (task: TaskType) => {
    setEditingTask(task);
    setShowTaskForm(true);
  };

  if (isLoading) {
    return (
      <AuthGuard>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          </main>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
            <button
              onClick={() => {
                setEditingTask(null);
                setShowTaskForm(true);
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Add Task
            </button>
          </div>

          <StatisticsDisplay tasks={tasks} />

          <TaskFilters onFilterChange={handleFilterChange} />

          {error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
              <span className="block sm:inline">{error}</span>
            </div>
          ) : filteredTasks.length === 0 ? (
            <EmptyState
              title={tasks.length === 0 ? "No tasks yet" : `No tasks match your ${filters.status === 'all' || !filters.status ? 'filters' : filters.status.toLowerCase()} filter`}
              description={tasks.length === 0
                ? "Get started by creating your first task. Click the button above to add a new task."
                : "Try changing your filters to see more tasks."}
              action={tasks.length === 0 ? (
                <button
                  onClick={() => {
                    setEditingTask(null);
                    setShowTaskForm(true);
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Create your first task
                </button>
              ) : null}
            />
          ) : (
            <TaskList
              tasks={filteredTasks}
              onToggleTask={handleToggleTask}
              onDeleteTask={handleDeleteTask}
              onEditTask={handleEditTask}
            />
          )}

          {showTaskForm && (
            <TaskForm
              isOpen={showTaskForm}
              onClose={() => {
                setShowTaskForm(false);
                setEditingTask(null);
              }}
              onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
              initialData={editingTask || undefined}
              isEditing={!!editingTask}
            />
          )}
        </main>
      </div>
    </AuthGuard>
  );
}