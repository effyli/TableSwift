import { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { userService } from '../services/user.service';

export const Dashboard: React.FC = () => {
  const { loading, user, logout } = useAuth();

  useEffect(() => {
    if (loading) {
      return;
    }

    console.log('User:', user);
  }, [loading]);

  const handleLogout = () => {
    logout();
  };

  async function fetchUsers() {
    try {
      const users = await userService.getAllUsers();
      console.log('Users:', users);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black to-black-lighter py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-400">Welcome, {user?.email}</span>
            <button
              onClick={fetchUsers}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Fetch all users
            </button>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
        
        <div className="mt-8 bg-black-light border border-black-lighter rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Protected Content</h2>
          <p className="text-gray-400">
            This is a protected route. You can only see this if you're logged in.
          </p>
        </div>
      </div>
    </div>
  );
};

