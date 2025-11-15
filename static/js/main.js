// API configuration
const API_BASE_URL = '/api';

// Store auth token
function setAuthToken(token) {
    localStorage.setItem('auth_token', token);
}

function getAuthToken() {
    return localStorage.getItem('auth_token');
}

function removeAuthToken() {
    localStorage.removeItem('auth_token');
}

// API helper function
async function apiRequest(endpoint, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json'
    };

    const token = getAuthToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method,
        headers
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        let result;
        try {
            result = await response.json();
        } catch (e) {
            // If JSON parsing fails, throw error with status
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        if (!response.ok) {
            throw new Error(result.error || result.msg || 'Request failed');
        }

        return result;
    } catch (error) {
        throw error;
    }
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getAuthToken();
}

// Redirect if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login';
    }
}

// Logout function
function logout() {
    removeAuthToken();
    window.location.href = '/';
}

// Attach logout to logout button if exists
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
});
