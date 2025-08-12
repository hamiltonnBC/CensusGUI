document.addEventListener('DOMContentLoaded', function() {
    // Global utility functions and event handlers go here

    // Handle flash messages dismissal
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        const closeButton = alert.querySelector('.close-button');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                alert.style.display = 'none';
            });
        }
    });

    // other global functionality here
});