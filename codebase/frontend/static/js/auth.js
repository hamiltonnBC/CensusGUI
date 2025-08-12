/**
 * Authentication-related JavaScript functionality
 */
console.log('Auth.js loaded successfully');
// Handle rate limiting and display feedback
function handleRateLimit(response) {
    if (response.status === 429) {
        throw new Error('Too many attempts. Please try again later.');
    }
    return response;
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    const errorDiv = document.getElementById('error-message');
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    try {
        // Disable submit button to prevent double submission
        submitButton.disabled = true;

        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            })
        });

        // Handle rate limiting
        handleRateLimit(response);

        const data = await response.json();

        if (data.success) {
            window.location.href = '/';
        } else {
            errorDiv.textContent = data.error || 'Login failed. Please try again.';
            errorDiv.classList.remove('hidden');
        }
    } catch (error) {
        errorDiv.textContent = error.message || 'An error occurred. Please try again.';
        errorDiv.classList.remove('hidden');
    } finally {
        // Re-enable submit button
        submitButton.disabled = false;
    }
}

// Password strength checker
function checkPasswordStrength(password) {
    const checks = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    const strength = Object.values(checks).filter(Boolean).length;
    return { strength, checks };
}

// Update password strength indicator
function updatePasswordStrength(password) {
    const indicator = document.getElementById('password-strength');
    const { strength, checks } = checkPasswordStrength(password);

    const messages = {
        0: 'Very Weak',
        1: 'Weak',
        2: 'Fair',
        3: 'Good',
        4: 'Strong',
        5: 'Very Strong'
    };

    const colors = {
        0: 'bg-red-500',
        1: 'bg-red-400',
        2: 'bg-yellow-500',
        3: 'bg-yellow-400',
        4: 'bg-green-500',
        5: 'bg-green-400'
    };

    indicator.textContent = messages[strength];
    indicator.className = `text-sm ${colors[strength]} text-white px-2 py-1 rounded`;

    return checks;
}

// Initialize authentication related features
function initAuth() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const passwordInput = document.getElementById('password');
    const passwordConfirm = document.getElementById('password-confirm');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (registerForm) {
        const requirements = document.getElementById('password-requirements');

        passwordInput?.addEventListener('input', (e) => {
            const checks = updatePasswordStrength(e.target.value);

            // Update requirement checks
            Object.entries(checks).forEach(([requirement, passed]) => {
                const elem = requirements?.querySelector(`[data-requirement="${requirement}"]`);
                if (elem) {
                    elem.classList.toggle('text-green-500', passed);
                    elem.classList.toggle('text-red-500', !passed);
                }
            });
        });

        passwordConfirm?.addEventListener('input', (e) => {
            const match = e.target.value === passwordInput.value;
            const matchIndicator = document.getElementById('password-match');
            if (matchIndicator) {
                matchIndicator.textContent = match ? 'Passwords match' : 'Passwords do not match';
                matchIndicator.className = `text-sm ${match ? 'text-green-500' : 'text-red-500'}`;
            }
        });

        registerForm.addEventListener('submit', handleRegister);
    }
}

// Handle registration form submission
async function handleRegister(event) {
    event.preventDefault();
    const errorDiv = document.getElementById('error-message');
    const successDiv = document.getElementById('success-message');
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    try {
        submitButton.disabled = true;

        // Validate passwords match
        const password = document.getElementById('password').value;
        const passwordConfirm = document.getElementById('password-confirm').value;

        if (password !== passwordConfirm) {
            throw new Error('Passwords do not match');
        }

        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: document.getElementById('username').value,
                email: document.getElementById('email').value,
                password: password
            })
        });

        handleRateLimit(response);

        const data = await response.json();

        if (data.success) {
            errorDiv.classList.add('hidden');
            successDiv.textContent = data.message || 'Registration successful! Please check your email to activate your account.';
            successDiv.classList.remove('hidden');
            form.reset();
        } else {
            errorDiv.textContent = data.error || 'Registration failed. Please try again.';
            errorDiv.classList.remove('hidden');
            successDiv.classList.add('hidden');
        }
    } catch (error) {
        errorDiv.textContent = error.message || 'An error occurred. Please try again.';
        errorDiv.classList.remove('hidden');
        successDiv.classList.add('hidden');
    } finally {
        submitButton.disabled = false;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initAuth);