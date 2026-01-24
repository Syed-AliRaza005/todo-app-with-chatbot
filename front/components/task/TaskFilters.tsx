import { useState } from 'react';
import { TaskFilterOptions } from '@/types/task';

interface TaskFiltersProps {
  onFilterChange: (filters: TaskFilterOptions) => void;
}

export default function TaskFilters({ onFilterChange }: TaskFiltersProps) {
  const [status, setStatus] = useState<'all' | 'Pending' | 'Completed'>('all');
  const [search, setSearch] = useState('');

  const handleStatusChange = (newStatus: 'all' | 'Pending' | 'Completed') => {
    setStatus(newStatus);
    onFilterChange({ status: newStatus, search });
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newSearch = e.target.value;
    setSearch(newSearch);
    onFilterChange({ status, search: newSearch });
  };

  return (
    <div className="flex flex-col sm:flex-row gap-4 mb-6">
      <div className="flex space-x-2">
        <button
          onClick={() => handleStatusChange('all')}
          className={`px-3 py-1.5 rounded-md text-sm font-medium ${
            status === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          All
        </button>
        <button
          onClick={() => handleStatusChange('Pending')}
          className={`px-3 py-1.5 rounded-md text-sm font-medium ${
            status === 'Pending'
              ? 'bg-yellow-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Pending
        </button>
        <button
          onClick={() => handleStatusChange('Completed')}
          className={`px-3 py-1.5 rounded-md text-sm font-medium ${
            status === 'Completed'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Completed
        </button>
      </div>
      <div className="flex-1">
        <input
          type="text"
          placeholder="Search tasks..."
          value={search}
          onChange={handleSearchChange}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
}