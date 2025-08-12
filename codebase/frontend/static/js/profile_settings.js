document.addEventListener('DOMContentLoaded', function() {
    // Function to show delete account confirmation modal
    window.showDeleteConfirmation = function() {
        const modal = document.getElementById('delete_modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    };

    // Handle form submissions with validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                // Disable button to prevent double submission
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Saving...';
            }
        });
    });

    // API Key handling
    const apiKeyInput = document.querySelector('input[name="api_key"]');
    if (apiKeyInput) {
        apiKeyInput.addEventListener('input', function() {
            // Remove quotes if user pastes them
            this.value = this.value.replace(/['"]/g, '');
        });
    }

    // Settings changed warning
    let settingsChanged = false;
    const settingsForm = document.querySelector('form[action*="update_settings"]');

    if (settingsForm) {
        const initialState = new FormData(settingsForm);

        settingsForm.addEventListener('change', () => {
            const currentState = new FormData(settingsForm);
            settingsChanged = false;

            for (let [key, value] of currentState.entries()) {
                if (value !== initialState.get(key)) {
                    settingsChanged = true;
                    break;
                }
            }
        });
    }

    // Warn about unsaved changes when leaving page
    window.addEventListener('beforeunload', (e) => {
        if (settingsChanged) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
});