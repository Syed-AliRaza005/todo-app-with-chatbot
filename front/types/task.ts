// Task-related TypeScript types

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'Pending' | 'Completed';
  created_at: string;
  completed_at?: string;
  user_id: string;
  updated_at?: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: 'Pending' | 'Completed';
}

export interface TaskFilterOptions {
  status?: 'all' | 'Pending' | 'Completed';
  search?: string;
}