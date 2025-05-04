import React from 'react';
import { IoMenu } from "react-icons/io5";
import { AiOutlineUser } from "react-icons/ai";
import { IoIosLogOut } from "react-icons/io";
import { useAuth } from '../context/AuthContext';
import ClickAwayListener from 'react-click-away-listener';

export type ActiveView = 'actions' | 'content';

interface TopBarProps {
  onToggleSidebar: () => void;
  activeView: ActiveView;
  setActiveView: (view: ActiveView) => void;
  isMobile: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({ 
  onToggleSidebar, 
  activeView, 
  setActiveView,
  isMobile
}) => {
  const { user, logout } = useAuth();
  const [openUserPopup, setOpenUserPopup] = React.useState(false);

  return (
    <div className="bg-black-light border-b border-black-lighter px-4 block h-[60px] z-31">
        <div className="flex items-center justify-between h-full">
            {/* Left section */}
            <div className="flex items-center gap-4">
                <button
                    onClick={onToggleSidebar}
                    className="text-gray-300 hover:text-white p-2 -m-2"
                >
                    <IoMenu size={24} />
                </button>
                
                {/* View switcher for mobile */}
                {isMobile && (
                    <div className="flex items-center bg-black-lighter rounded-lg p-1">
                        <button
                            onClick={() => setActiveView('actions')}
                            className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                            activeView === 'actions'
                                ? 'bg-indigo-600 text-white'
                                : 'text-gray-400 hover:text-white'
                            }`}
                        >
                            Actions
                        </button>
                        <button
                            onClick={() => setActiveView('content')}
                            className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                            activeView === 'content'
                                ? 'bg-indigo-600 text-white'
                                : 'text-gray-400 hover:text-white'
                            }`}
                        >
                            Content
                        </button>
                    </div>
                )}
            </div>

            {/* Right section */}
            <div className="flex items-center gap-4">
                <ClickAwayListener onClickAway={() => openUserPopup && setOpenUserPopup(false)}>
                    <div className="flex items-center gap-2 text-gray-300">
                        <AiOutlineUser onClick={() => {setOpenUserPopup(!openUserPopup)}} size={20} />
                        <div className={`absolute flex flex-col gap-4 items-end top-[60px] right-4 p-4 bg-black-light border border-black-lighter rounded-lg shadow-lg mt-2 ${openUserPopup ? 'block' : 'hidden'}`}>
                            <span className="text-sm">{user?.email}</span>
                            <span className="text-sm flex gap-2 text-red" onClick={logout}>Logout <IoIosLogOut size={20} /></span>
                        </div>
                    </div>
                </ClickAwayListener>
            </div>
        </div>
    </div>
  );
};
