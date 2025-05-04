import React from 'react';

interface Action {
  id: string;
  action: string;
  column: string;
  datetime: string;
}

interface ActionHistoryProps {
  actions: Action[];
  onNewAction: () => void;
  onRevert: (actionId: string) => void;
}

export const ActionHistory: React.FC<ActionHistoryProps> = ({
  actions,
  onNewAction,
  onRevert,
}) => {
  return (
    <div className="bg-black-light border-r border-black-lighter h-screen p-4 flex-grow">
      <button
        onClick={onNewAction}
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
                    onClick={() => onRevert(action.id)}
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
