import React, { useState } from 'react';
import { Action } from '../types/action';

interface ActionHistoryProps {}

export const ActionHistory: React.FC<ActionHistoryProps> = () => {
  
   const [actions] = useState<Action[]>([
      // {
      //   id: '1',
      //   action: 'Transformation',
      //   column: 'Start_date',
      //   datetime: '12:33 13-03-2025',
      // },
      // {
      //   id: '2',
      //   action: 'Transformation',
      //   column: 'End_date',
      //   datetime: '13:28 13-03-2025',
      // },
      // {
      //   id: '3',
      //   action: 'Transformation',
      //   column: 'Value',
      //   datetime: '14:44 13-03-2025',
      // },
    ]);

  const handleNewAction = () => {
    // Implement new action logic
    console.log('New action clicked');
  };

  const handleRevert = () => {
    // Implement revert action logic
    console.log('Revert action clicked');
  }

  return (
    <div className="bg-black-light border-r border-black-lighter min-h-0 h-full p-4 overflow-y-auto flex-1 flex flex-col">
      <button
        onClick={handleNewAction}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors mb-6 flex items-center justify-center"
      >
        <span className="mr-2">+</span> New action
      </button>

      <div className="space-y-4">
        <table className="w-full">
          <thead>
            <tr className="text-sm text-gray-400">
              <th className="text-left font-semibold pb-2">Action</th>
              <th className="text-left font-semibold pb-2">Column</th>
              <th className="text-left font-semibold pb-2">Datetime</th>
              <th className="text-left font-semibold pb-2"></th>
            </tr>
          </thead>
          <tbody className="text-gray-300">
            {actions.map((action) => (
              <tr key={action.id} className="border-t border-black-lighter">
                <td className="py-3">{action.action}</td>
                <td className="py-3">{action.column}</td>
                <td className="py-3">{action.datetime}</td>
                <td className="py-3">
                  <button
                    onClick={() => handleRevert()}
                    className="text-indigo-500 hover:text-indigo-400"
                  >
                    Revert
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
