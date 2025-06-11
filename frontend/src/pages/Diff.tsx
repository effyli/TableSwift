import React, { useState } from 'react';

type DiffRow = Record<string, string>;

export const DiffViewer: React.FC = () => {
  const [headers, setHeaders] = useState<string[]>([]);
  const [rows, setRows] = useState<DiffRow[]>([]);
  const [changedColumns, setChangedColumns] = useState<Set<string>>(new Set());

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = reader.result as string;
      parseDiff(text);
    };
    reader.readAsText(file);
  };

  function parseDiff(text: string) {
    const lines = text.split(/\r?\n/).filter(l => l.trim() !== '');
    const rawHeader = lines.find(l => !/^[+-]/.test(l))!;
    const cols = rawHeader.replace(/^..?/, '').split(',');
    setHeaders(cols);

    const out: DiffRow[] = [];
    const changedCols = new Set<string>();

    for (let i = 0; i < lines.length; i++) {
      if (lines[i].startsWith('-')) {
        const oldVals = lines[i].replace(/^-.\s*/, '').split(',');
        let j = i + 1;
        while (j < lines.length && lines[j].startsWith('?')) j++;
        if (j < lines.length && lines[j].startsWith('+')) {
          const newVals = lines[j].replace(/^\+.\s*/, '').split(',');

          const row: DiffRow = {};
          cols.forEach((c, idx) => {
            const newVal = newVals[idx];
            const oldVal = oldVals[idx];
            row[c] = newVal;
            row[`Original ${c}`] = oldVal;
            if (newVal !== oldVal) {
              changedCols.add(c);
            }
          });
          out.push(row);
          i = j;
        }
      }
    }
    setRows(out);
    setChangedColumns(changedCols);
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>CSV Diff Viewer</h2>
      <input
        type="file"
        accept=".txt,.diff"
        onChange={onFileChange}
        style={{ marginBottom: 20 }}
      />
      {rows.length > 0 && (
        <table
          style={{
            borderCollapse: 'collapse',
            width: '100%',
            fontFamily: 'sans-serif',
          }}
        >
          <thead>
            <tr>
              {/* Only show headers for changed columns */}
              {headers.filter(h => changedColumns.has(h)).map(h => (
                <th
                  key={`new-h-${h}`}
                  style={{
                    borderBottom: '2px solid #333',
                    textAlign: 'left',
                    padding: '8px',
                  }}
                >
                  Updated {h}
                </th>
              ))}
              {headers.filter(h => changedColumns.has(h)).map(h => (
                <th
                  key={`old-h-${h}`}
                  style={{
                    borderBottom: '2px solid #333',
                    textAlign: 'left',
                    padding: '8px',
                  }}
                >
                  Original {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri}>
                {/* Only show values for changed columns */}
                {headers.filter(h => changedColumns.has(h)).map(h => (
                  <td
                    key={`new-${ri}-${h}`}
                    style={{
                      padding: '6px 8px',
                      color: 'green',
                    }}
                  >
                    {row[h]}
                  </td>
                ))}
                {headers.filter(h => changedColumns.has(h)).map(h => (
                  <td
                    key={`old-${ri}-${h}`}
                    style={{
                      padding: '6px 8px',
                      color: 'crimson',
                    }}
                  >
                    {row[`Original ${h}`]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
