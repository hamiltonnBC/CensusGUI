document.addEventListener('DOMContentLoaded', function () {
    // Configuration
    const availableTables = [
        {id: 'DP02', name: 'Social Characteristics'},
        {id: 'DP03', name: 'Economic Characteristics'},
        {id: 'DP04', name: 'Housing Characteristics'},
        {id: 'DP05', name: 'Demographic Characteristics'}
    ];

    // State management
    const selectedYears = new Set();

    // Function to organize variables by table ID
    function organizeVariablesByTable(variables) {
        const tableVariables = {};

        variables.forEach(variable => {
            // Extract table ID from variable code (e.g., 'DP05_0001E' -> 'DP05')
            const tableId = variable.substring(0, 4);
            if (!tableVariables[tableId]) {
                tableVariables[tableId] = [];
            }
            tableVariables[tableId].push(variable);
        });

        return Object.entries(tableVariables).map(([id, vars]) => ({
            id: id,
            variables: vars
        }));
    }

    // Initialize table display
    function initializeTables() {
        const tableSelection = document.getElementById('tableSelection');
        if (!tableSelection) return;

        tableSelection.innerHTML = availableTables.map(table => `
            <div class="table-info p-3 border rounded-lg">
                <div class="font-medium">${table.id}</div>
                <p class="text-sm text-gray-600">${table.name}</p>
            </div>
        `).join('');
    }

    // Initialize year selection
    function initializeYears() {
        const yearSelection = document.getElementById('yearSelection');
        if (!yearSelection) return;

        const currentYear = new Date().getFullYear();
        const years = Array.from(
            {length: currentYear - 2009 + 1},
            (_, i) => currentYear - i
        );

        yearSelection.innerHTML = years.map(year => `
            <div class="year-option p-2 text-center border rounded cursor-pointer"
                 data-year="${year}">
                ${year}
            </div>
        `).join('');

        // Add click handlers for years
        yearSelection.querySelectorAll('.year-option').forEach(option => {
            option.addEventListener('click', function () {
                const year = this.dataset.year;
                if (selectedYears.has(year)) {
                    selectedYears.delete(year);
                    this.classList.remove('bg-blue-50', 'border-blue-500');
                } else {
                    selectedYears.add(year);
                    this.classList.add('bg-blue-50', 'border-blue-500');
                }
            });
        });
    }

    // Form submission handler
    const form = document.getElementById('dataSelectionForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (selectedYears.size === 0) {
                alert('Please select at least one year');
                return;
            }

            const variables = document.getElementById('variables').value.split(',').map(v => v.trim());
            if (!variables.length || (variables.length === 1 && !variables[0])) {
                alert('Please enter at least one variable');
                return;
            }

            const formData = {
                tables: organizeVariablesByTable(variables),
                years: Array.from(selectedYears),
                acs_type: document.getElementById('acs_type').value,
                geography: document.getElementById('geography').value,
                api_key: document.getElementById('api_key').value,
                include_metadata: document.getElementById('include_metadata').checked
            };

            // Generate URLs for confirmation
            fetch('/api/generate_url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            })
                .then(response => response.json())
                .then(result => {
                    const confirmation = document.getElementById('confirmation');
                    const apiUrlDisplay = document.getElementById('api_url_display');

                    if (result.urls) {
                        apiUrlDisplay.innerHTML = result.urls.map(url => `
                        <div class="mb-2">
                            <strong>${url.table} (${url.year})</strong>: 
                            <span class="text-sm break-all">${url.url}</span>
                        </div>
                    `).join('');
                        form.style.display = 'none';
                        confirmation.style.display = 'flex';
                    } else {
                        console.error('Error:', result.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    }

    // Initialize the form
    initializeTables();
    initializeYears();

    // Confirmation handlers
    const confirmYes = document.getElementById('confirm_yes');
    const confirmNo = document.getElementById('confirm_no');
    const confirmation = document.getElementById('confirmation');

    if (confirmYes) {
        confirmYes.addEventListener('click', function () {
            const variables = document.getElementById('variables').value.split(',').map(v => v.trim());
            const formData = {
                tables: organizeVariablesByTable(variables),
                years: Array.from(selectedYears),
                acs_type: document.getElementById('acs_type').value,
                geography: document.getElementById('geography').value,
                api_key: document.getElementById('api_key').value,
                include_metadata: document.getElementById('include_metadata').checked
            };

            fetch('/process_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            })
                .then(response => response.text())
                .then(html => {
                    document.open();
                    document.write(html);
                    document.close();
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    }

    if (confirmNo) {
        confirmNo.addEventListener('click', function () {
            form.style.display = 'block';
            confirmation.style.display = 'none';
        });
    }
});


    document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('toggleAIAssistant');
    const container = document.getElementById('aiAssistantContainer');
    const hideText = document.getElementById('hideAssistantText');
    const showText = document.getElementById('showAssistantText');
    const questionInput = document.getElementById('aiQuestion');
    const submitButton = document.getElementById('submitAIQuestion');
    const chatHistory = document.getElementById('chatHistory');

    // Toggle AI Assistant visibility
    toggleButton.addEventListener('click', () => {
    container.classList.toggle('hidden');
    hideText.classList.toggle('hidden');
    showText.classList.toggle('hidden');
});

    // Enable/disable submit button based on input
    questionInput.addEventListener('input', () => {
    submitButton.disabled = questionInput.value.trim().length === 0;
});

    // Handle question submission
    submitButton.addEventListener('click', async () => {
    const question = questionInput.value.trim();
    if (!question) return;

    // Add user question to chat
    addMessageToChat('user', question);

    try {
    submitButton.disabled = true;
    questionInput.disabled = true;

    const response = await fetch('/api/ask-ai', {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json',
},
    body: JSON.stringify({question})
});

    const data = await response.json();

    // Add AI response to chat
    addMessageToChat('ai', data.response);

} catch (error) {
    addMessageToChat('error', 'Sorry, there was an error processing your question. Please try again.');
} finally {
    submitButton.disabled = false;
    questionInput.disabled = false;
    questionInput.value = '';
}
});

    function addMessageToChat(type, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'p-3 rounded-lg ' +
    (type === 'user' ? 'bg-blue-50 ml-8' :
    type === 'ai' ? 'bg-white border ml-0 mr-8' : 'bg-red-50 mx-8');

    messageDiv.innerHTML = `
            <p class="text-sm ${type === 'error' ? 'text-red-600' : 'text-gray-700'}">
                ${type === 'user' ? '<span class="font-medium">You:</span> ' :
    type === 'ai' ? '<span class="font-medium">AI:</span> ' : ''}
                ${message}
            </p>
        `;

    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}
});
