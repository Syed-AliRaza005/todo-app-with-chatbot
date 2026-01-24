import { cn } from '@/lib/utils';

interface EmptyStateProps {
  title: string;
  description: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export default function EmptyState({
  title,
  description,
  action,
  icon,
  className
}: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-12 px-4", className)}>
      {icon && <div className="mb-4">{icon}</div>}
      <h3 className="text-lg font-medium text-gray-900 mb-1">{title}</h3>
      <p className="text-gray-500 text-center mb-6 max-w-md">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
}