import { Task as TaskType } from '@/types/task';
import { formatDate } from '@/lib/utils';
import Button from '@/components/ui/Button';

interface TaskItemProps {
  task: TaskType;
  onToggle: () => void;
  onDelete: () => void;
  onEdit: () => void;
}

export default function TaskItem({ task, onToggle, onDelete, onEdit }: TaskItemProps) {
  return (
    <li className="px-4 py-4 sm:px-6 hover:bg-gray-50 transition-colors duration-150">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={task.status === 'Completed'}
            onChange={onToggle}
            className="h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer"
          />
          <div className="ml-3 min-w-0 flex-1">
            <p
              className={`text-sm font-medium ${
                task.status === 'Completed' ? 'text-gray-500 line-through' : 'text-gray-900'
              }`}
            >
              {task.title}
            </p>
            {task.description && (
              <p className="text-sm text-gray-500 mt-1">{task.description}</p>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            task.status === 'Completed'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {task.status === 'Completed' ? 'Completed' : 'Pending'}
          </span>
          <span className="text-xs text-gray-500 hidden sm:inline">
            {formatDate(task.created_at)}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={onEdit}
            className="text-blue-600 hover:text-blue-900 hover:bg-blue-50 p-1"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13.586 3.586a1 1 0 111.414 1.414l-.707.707a1 1 0 01-1.414 0l-.707-.707a1 1 0 010-1.414zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onDelete}
            className="text-red-600 hover:text-red-900 hover:bg-red-50 p-1"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </Button>
        </div>
      </div>
      {task.status === 'Completed' && task.completed_at && (
        <div className="ml-8 mt-1">
          <p className="text-xs text-green-600">
            Completed on {formatDate(task.completed_at)}
          </p>
        </div>
      )}
    </li>
  );
}