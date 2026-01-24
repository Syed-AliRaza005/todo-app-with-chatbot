import { Task as TaskType } from '@/types/task';
import TaskItem from '@/components/task/TaskItem';

interface TaskListProps {
  tasks: TaskType[];
  onToggleTask: (id: string) => void;
  onDeleteTask: (id: string) => void;
  onEditTask: (task: TaskType) => void;
}

export default function TaskList({ tasks, onToggleTask, onDeleteTask, onEditTask }: TaskListProps) {
  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggle={() => onToggleTask(task.id)}
            onDelete={() => onDeleteTask(task.id)}
            onEdit={() => onEditTask(task)}
          />
        ))}
      </ul>
    </div>
  );
}