import { Task } from '@/types/task';
import StatsBar from '@/components/layout/StatsBar';

interface StatisticsDisplayProps {
  tasks: Task[];
}

export default function StatisticsDisplay({ tasks }: StatisticsDisplayProps) {
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(task => task.status === 'Completed').length;
  const pendingTasks = tasks.filter(task => task.status === 'Pending').length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="mb-8">
      <StatsBar
        totalTasks={totalTasks}
        pendingTasks={pendingTasks}
        completedTasks={completedTasks}
      />

      <div className="bg-white shadow rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Completion Rate</h3>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-green-600 h-4 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${completionRate}%` }}
          ></div>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          {completionRate}% completed ({completedTasks} of {totalTasks} tasks)
        </div>
      </div>
    </div>
  );
}