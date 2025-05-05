import axios from 'axios';

const API_URL = 'http://localhost:80';

// Create axios instance with default config
const axiosInstance = axios.create({
    baseURL: API_URL,
    withCredentials: true,
});

axiosInstance.interceptors.request.use(
    async (config) => {
        // Skip adding CSRF token for GET requests and token endpoint
        if (
            config.method?.toLowerCase() === 'get' ||
            config.url === '/csrf-token'
        ) {
            return config;
        }

        try {
            // Try to get existing token from cookies
            let csrfToken = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrf_access_token='))
                ?.split('=')[1];
            
            // If no token exists or about to expire, get a new one
            if (!csrfToken) {
                await axios.get(`${API_URL}/csrf-token`, { withCredentials: true });

                csrfToken = document.cookie
                    .split('; ')
                    .find(row => row.startsWith('csrf_access_token='))
                    ?.split('=')[1];
            }

            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }

            console.log('Setting CSRF token:', csrfToken);
            config.headers['X-CSRF-Token'] = csrfToken;
            return config;
        } catch (error) {
            console.error('Failed to set CSRF token:', error);
            return Promise.reject(error);
        }
    },
    (error) => {
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        console.log('Error response:', error.response);

        // If error is CSRF related and we haven't retried yet
        if (
            error.response?.status === 401 &&
            error.response?.data?.detail?.includes('CSRF') &&
            !originalRequest._retry
        ) {
            originalRequest._retry = true;

            try {
                console.log('Retrying request with new CSRF token...');
                await axios.get(`${API_URL}/csrf-token`, { withCredentials: true });
                
                return axiosInstance(originalRequest);
            } catch (error) {
                return Promise.reject(error);
            }
        } else if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
            console.error('Unauthorized access:', error.response.data);
            window.location.href = '/login';
        }

        return Promise.reject(error);
    }
);

export default axiosInstance;
