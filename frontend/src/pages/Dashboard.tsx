import { useState, useEffect } from 'react';
import { Sidebar } from '../components/Sidebar';
import { ActionHistory } from '../components/ActionHistory';
import { ContentView } from '../components/ContentView';
import { TopBar, ActiveView } from '../components/TopBar';

interface Action {
  id: string;
  action: string;
  column: string;
  datetime: string;
}

export const Dashboard: React.FC = () => {
  // Mobile view state
  const [activeView, setActiveView] = useState<ActiveView>('content');
  const [isSidebarOpen, setIsSidebarOpen] = useState(window.innerWidth > 1024);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024);

  // Listen for window resize
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const [actions, setActions] = useState<Action[]>([
    {
      id: '1',
      action: 'Transformation',
      column: 'Start_date',
      datetime: '12:33 13-03-2025',
    },
    {
      id: '2',
      action: 'Transformation',
      column: 'End_date',
      datetime: '13:28 13-03-2025',
    },
    {
      id: '3',
      action: 'Transformation',
      column: 'Value',
      datetime: '14:44 13-03-2025',
    },
  ]);

  const [uploadError, setUploadError] = useState<string|null>(null);
  const [fileData] = useState({
    name: 'file.csv',
    rowCount: 358,
    data: [
      { id: 1, start_date: '2025-01-01', end_date: '2025-12-31', value: 100 },
      { id: 2, start_date: '2025-02-01', end_date: '2025-12-31', value: 200 },
      { id: 3, start_date: '2025-03-01', end_date: '2025-12-31', value: 300 },
    ],
  });

  const handleFileSelect = async (file: File) => {
    setUploadError(null);

    // Validate file size (e.g., max 10MB)
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    if (file.size > MAX_FILE_SIZE) {
      setUploadError('File size too large. Maximum size is 10MB.');
      return;
    }

    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      console.log('Selected file:', file.name);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error instanceof Error ? error.message : 'Failed to upload file');
    }
  };

  const handleNewAction = () => {
    // Implement new action logic
    console.log('New action clicked');
  };

  const handleRevert = (actionId: string) => {
    // Implement revert logic
    console.log('Revert clicked for action:', actionId);
  };

  return (
    <div className="flex flex-col h-screen bg-black-lighter overflow-hidden">
      <TopBar 
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        activeView={activeView}
        setActiveView={setActiveView}
        isMobile={isMobile}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar 
          onFileSelect={handleFileSelect}
          uploadError={uploadError}
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
        />

        {/* Main content area */}
        <div className="flex flex-1 flex-col lg:flex-row min-w-0">
          {/* Action History - hidden on mobile when content view is active */}
          <div className={`
            ${isMobile ? (activeView === 'actions' ? 'flex' : 'hidden') : 'flex'}
            lg:flex flex-col flex-1
          `}>
            <ActionHistory
              actions={actions}
              onNewAction={handleNewAction}
              onRevert={handleRevert}
            />
          </div>

          {/* Content View - hidden on mobile when actions view is active */}
          <div className={`
            ${isMobile ? (activeView === 'content' ? 'flex' : 'hidden') : 'flex'}
            flex-1 min-w-0
          `}>
            <ContentView
              fileName={fileData.name}
              rowCount={fileData.rowCount}
              data={fileData.data}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

