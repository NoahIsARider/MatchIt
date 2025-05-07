// average_calculator.js
// JavaScript for calculating field averages in form submissions

document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const fieldSelect = document.getElementById('field-select');
    const calculateBtn = document.getElementById('calculate-average-btn');
    const resultsContainer = document.getElementById('average-results');
    const averageValueElement = document.getElementById('average-value');
    const averageStatsElement = document.getElementById('average-stats');
    
    // If elements don't exist, we're not on the form submissions page
    if (!fieldSelect || !calculateBtn) return;
    
    // Enable/disable calculate button based on field selection
    fieldSelect.addEventListener('change', function() {
        calculateBtn.disabled = !this.value;
    });
    
    // Handle calculate button click
    calculateBtn.addEventListener('click', function() {
        const fieldName = fieldSelect.value;
        if (!fieldName) return;
        
        // Get form ID from the URL
        const urlParts = window.location.pathname.split('/');
        const formId = urlParts[urlParts.indexOf('form') + 1];
        
        // Show loading state
        calculateBtn.disabled = true;
        calculateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Calculating...';
        
        // Make AJAX request to calculate average
        fetch(`/api/calculate_average/${formId}/${fieldName}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Display results
                if (data.average !== null) {
                    // Format the average to 2 decimal places
                    const formattedAverage = parseFloat(data.average).toFixed(2);
                    
                    averageValueElement.innerHTML = `<strong>Average value for ${fieldName}:</strong> ${formattedAverage}`;
                    averageStatsElement.innerHTML = `Based on ${data.numeric_count} numeric values. ${data.non_numeric_count} non-numeric values were skipped.`;
                    
                    resultsContainer.classList.remove('d-none');
                } else {
                    averageValueElement.innerHTML = `<strong>No numeric values found for ${fieldName}</strong>`;
                    averageStatsElement.innerHTML = `${data.non_numeric_count} non-numeric values were skipped.`;
                    
                    resultsContainer.classList.remove('d-none');
                }
            })
            .catch(error => {
                console.error('Error calculating average:', error);
                averageValueElement.innerHTML = '<strong>Error calculating average</strong>';
                averageStatsElement.innerHTML = 'Please try again later.';
                resultsContainer.classList.remove('d-none');
            })
            .finally(() => {
                // Reset button state
                calculateBtn.disabled = false;
                calculateBtn.innerHTML = 'Calculate Average';
            });
    });
});