import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  color?: 'blue' | 'green' | 'yellow' | 'red';
}

function StatCard({ title, value, description, color = 'blue' }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-800',
    green: 'bg-green-50 border-green-200 text-green-800',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    red: 'bg-red-50 border-red-200 text-red-800',
  };

  return (
    <div className={cn(
      'border rounded-lg p-4',
      colorClasses[color]
    )}>
      <p className="text-sm font-medium">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      {description && <p className="text-xs mt-1 opacity-75">{description}</p>}
    </div>
  );
}

interface StatsBarProps {
  totalTasks: number;
  pendingTasks: number;
  completedTasks: number;
  className?: string;
}

export default function StatsBar({
  totalTasks,
  pendingTasks,
  completedTasks,
  className
}: StatsBarProps) {
  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-3 gap-4 mb-6", className)}>
      <StatCard
        title="Total Tasks"
        value={totalTasks}
        description="All tasks in your list"
        color="blue"
      />
      <StatCard
        title="Pending"
        value={pendingTasks}
        description="Tasks to complete"
        color="yellow"
      />
      <StatCard
        title="Completed"
        value={completedTasks}
        description="Finished tasks"
        color="green"
      />
    </div>
  );
}