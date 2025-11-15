document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signupForm');
    const errorMessage = document.getElementById('error-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous errors
        errorMessage.style.display = 'none';

        // Get form data
        const formData = {
            company_name: document.getElementById('company_name').value,
            email: document.getElementById('email').value,
            industry: document.getElementById('industry').value,
            company_size: document.getElementById('company_size').value,
            first_name: document.getElementById('first_name').value,
            last_name: document.getElementById('last_name').value,
            password: document.getElementById('password').value
        };

        const confirmPassword = document.getElementById('confirm_password').value;

        // Validate passwords match
        if (formData.password !== confirmPassword) {
            errorMessage.textContent = 'Passwords do not match';
            errorMessage.style.display = 'block';
            return;
        }

        // Validate password length
        if (formData.password.length < 8) {
            errorMessage.textContent = 'Password must be at least 8 characters';
            errorMessage.style.display = 'block';
            return;
        }

        try {
            // Submit signup request
            const result = await apiRequest('/auth/signup', 'POST', formData);

            // Store auth token
            setAuthToken(result.access_token);

            // Redirect to questionnaire
            window.location.href = '/questionnaire';
        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        }
    });
});
