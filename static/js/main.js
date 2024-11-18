// Form validation and submission handling
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const submitButton = form?.querySelector('button[type="submit"]');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            if (submitButton) {
                // Show loading state
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating Plan...
                `;
            }
        });
    }
});

// Form field validation
function validateForm() {
    const requiredFields = document.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('border-red-500');
        } else {
            field.classList.remove('border-red-500');
        }
    });

    return isValid;
}

// Budget formatter
function formatBudget(input) {
    let value = input.value.replace(/[^\d]/g, '');
    if (value) {
        value = parseInt(value).toLocaleString('en-US');
        input.value = value;
    }
}

// Date validation
function validateDate(input) {
    const selectedDate = new Date(input.value);
    const today = new Date();
    
    if (selectedDate < today) {
        input.setCustomValidity('Please select a future date');
    } else {
        input.setCustomValidity('');
    }
}

// Dynamic participant count validation
function validateParticipants(input) {
    const count = parseInt(input.value);
    if (count < 1) {
        input.setCustomValidity('Must have at least 1 participant');
    } else if (count > 10000) {
        input.setCustomValidity('Maximum 10,000 participants allowed');
    } else {
        input.setCustomValidity('');
    }
}

// Print functionality
function printResults() {
    window.print();
}

// Smooth scroll to results
function scrollToResults() {
    const resultsSection = document.querySelector('#results');
    if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Error handling
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mt-4';
    errorDiv.role = 'alert';
    errorDiv.innerHTML = `
        <strong class="font-bold">Error!</strong>
        <span class="block sm:inline">${message}</span>
        <span class="absolute top-0 bottom-0 right-0 px-4 py-3">
            <svg class="fill-current h-6 w-6 text-red-500" role="button" onclick="this.parentElement.parentElement.remove()"
                xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                <title>Close</title>
                <path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
            </svg>
        </span>
    `;
    document.querySelector('form').prepend(errorDiv);
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', e => {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute z-10 p-2 bg-gray-900 text-white text-sm rounded shadow-lg';
            tooltip.textContent = e.target.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            const rect = e.target.getBoundingClientRect();
            tooltip.style.top = `${rect.bottom + 5}px`;
            tooltip.style.left = `${rect.left}px`;
        });
        
        trigger.addEventListener('mouseleave', () => {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    
    // Add event listeners for form validation
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput) {
        dateInput.addEventListener('change', () => validateDate(dateInput));
    }
    
    const participantsInput = document.querySelector('input[name="expected_participants"]');
    if (participantsInput) {
        participantsInput.addEventListener('input', () => validateParticipants(participantsInput));
    }
    
    const budgetInput = document.querySelector('input[name="budget"]');
    if (budgetInput) {
        budgetInput.addEventListener('input', () => formatBudget(budgetInput));
    }
});