document.addEventListener('DOMContentLoaded', function() {
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    const requirements = {
        length: /.{8,}/,
        uppercase: /[A-Z]/,
        lowercase: /[a-z]/,
        number: /[0-9]/,
        special: /[!@#$%^&*(),.?":{}|<>]/
    };

    // Function to update requirement status
    function updateRequirement(name, valid) {
        const element = document.querySelector(`[data-requirement="${name}"]`);
        if (element) {
            element.className = valid ? 'text-green-500' : 'text-red-500';
        }
    }

    // Check password requirements
    newPassword.addEventListener('input', function() {
        const password = this.value;
        Object.keys(requirements).forEach(req => {
            updateRequirement(req, requirements[req].test(password));
        });

        // Check password match if confirm password has value
        if (confirmPassword.value) {
            checkPasswordMatch();
        }
    });

    // Check if passwords match
    function checkPasswordMatch() {
        const matchMessage = document.getElementById('password_match');
        const doMatch = newPassword.value === confirmPassword.value;

        matchMessage.textContent = confirmPassword.value ?
            (doMatch ? 'Passwords match' : 'Passwords do not match') : '';
        matchMessage.className = `mt-1 text-sm ${doMatch ? 'text-green-600' : 'text-red-600'}`;
    }

    confirmPassword.addEventListener('input', checkPasswordMatch);

    // Form submission validation
    document.querySelector('form').addEventListener('submit', function(e) {
        if (newPassword.value !== confirmPassword.value) {
            e.preventDefault();
            alert('Passwords do not match');
            return false;
        }

        // Check all password requirements
        for (let [requirement, regex] of Object.entries(requirements)) {
            if (!regex.test(newPassword.value)) {
                e.preventDefault();
                alert(`Password must contain ${requirement}`);
                return false;
            }
        }
    });
});