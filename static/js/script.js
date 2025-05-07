// script.js
// Main JavaScript file for the MatchIt Form System

document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Tooltips initialization (if using Bootstrap tooltips)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle checkbox groups to collect values as arrays
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const checkboxGroups = {};
            
            // Find all checkboxes and group them by name
            form.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
                const name = checkbox.getAttribute('name');
                if (!checkboxGroups[name]) {
                    checkboxGroups[name] = [];
                }
                checkboxGroups[name].push(checkbox.value);
            });
            
            // For each group, create a hidden input with the JSON value
            for (const [name, values] of Object.entries(checkboxGroups)) {
                if (values.length > 0) {
                    // Remove existing checkboxes with this name to avoid duplicates
                    form.querySelectorAll(`input[name="${name}"]:checked`).forEach(el => {
                        el.disabled = true;
                    });
                    
                    // Add a hidden field with all values
                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = `${name}_values`;
                    hiddenInput.value = JSON.stringify(values);
                    form.appendChild(hiddenInput);
                }
            }
        });
    });

    // Dynamic field options for select, radio, and checkbox fields
    const fieldTypeSelects = document.querySelectorAll('.field-type');
    fieldTypeSelects.forEach(select => {
        select.addEventListener('change', function() {
            const fieldCard = this.closest('.field-card');
            const optionsContainer = fieldCard.querySelector('.options-container');
            
            if (['select', 'radio', 'checkbox'].includes(this.value)) {
                optionsContainer.classList.remove('d-none');
            } else {
                optionsContainer.classList.add('d-none');
            }
        });
    });
});