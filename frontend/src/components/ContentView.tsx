import React from 'react';

interface ContentViewProps {
  fileName: string;
  rowCount: number;
  data: any[];
}

export const ContentView: React.FC<ContentViewProps> = ({
  fileName,
  rowCount,
  data,
}) => {
  return (
    <div className="bg-black min-h-0 h-full p-4 flex-1 flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div>
          <span className="text-gray-400 mr-4">{fileName}</span>
          <span className="text-gray-500">{rowCount} rows</span>
        </div>
        <div className="relative flex-1 max-w-md ml-4">
          <input
            type="text"
            placeholder="Search value"
            className="w-full bg-black-lighter text-white px-4 py-2 rounded-lg border border-black-lighter focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-sm text-gray-400 border-b border-black-lighter">
              <th className="text-left font-semibold p-3">Id</th>
              <th className="text-left font-semibold p-3">Start_date</th>
              <th className="text-left font-semibold p-3">End_date</th>
              <th className="text-left font-semibold p-3">Value</th>
            </tr>
          </thead>
          <tbody className="text-gray-300">
            {data.map((row, index) => (
              <tr key={index} className="border-b border-black-lighter">
                <td className="p-3">{row.id}</td>
                <td className="p-3">{row.start_date}</td>
                <td className="p-3">{row.end_date}</td>
                <td className="p-3">{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
