// clustering_calculator.js
// JavaScript for clustering form submissions based on field values

document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const fieldSelect = document.getElementById('field-select');
    const clusteringBtn = document.getElementById('calculate-clustering-btn');
    const clusteringModal = document.getElementById('clustering-modal');
    const clusteringForm = document.getElementById('clustering-form');
    const clusteringResults = document.getElementById('clustering-results');
    const clusteringContainer = document.getElementById('clustering-container');
    
    // If elements don't exist, we're not on the form submissions page
    if (!fieldSelect || !clusteringBtn) return;
    
    // Enable/disable clustering button based on field selection
    fieldSelect.addEventListener('change', function() {
        clusteringBtn.disabled = !this.value;
    });
    
    // Handle clustering button click - show modal
    clusteringBtn.addEventListener('click', function() {
        const fieldName = fieldSelect.value;
        if (!fieldName) return;
        
        // Set the field name in the modal
        if (document.getElementById('clustering-field-name')) {
            document.getElementById('clustering-field-name').textContent = fieldName;
        }
        
        // Show the modal
        const bootstrapModal = new bootstrap.Modal(clusteringModal);
        bootstrapModal.show();
    });
    
    // Handle clustering form submission
    clusteringForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fieldName = fieldSelect.value;
        if (!fieldName) return;
        
        // Get clustering parameters
        const clusteringType = document.querySelector('input[name="clustering-type"]:checked').value;
        let numClusters = null;
        let membersPerCluster = null;
        
        if (clusteringType === 'num-clusters') {
            numClusters = parseInt(document.getElementById('num-clusters').value);
        } else {
            membersPerCluster = parseInt(document.getElementById('members-per-cluster').value);
        }
        
        // Get form ID from the URL
        const urlParts = window.location.pathname.split('/');
        const formId = urlParts[urlParts.indexOf('form') + 1];
        
        // Show loading state
        document.getElementById('clustering-submit-btn').disabled = true;
        document.getElementById('clustering-submit-btn').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Clustering...';
        
        // Make AJAX request to perform clustering
        fetch(`/api/calculate_clustering/${formId}/${fieldName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                num_clusters: numClusters,
                members_per_cluster: membersPerCluster
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide the modal
            bootstrap.Modal.getInstance(clusteringModal).hide();
            
            // Display results
            if (data.success) {
                // Clear previous results
                clusteringResults.innerHTML = '';
                
                // Create header
                const header = document.createElement('div');
                header.className = 'alert alert-info';
                header.innerHTML = `
                    <h6 class="alert-heading">Clustering Results for ${data.field_name}:</h6>
                    <p>Total submissions: ${data.total_submissions} (${data.non_numeric_count} non-numeric values were skipped)</p>
                    <p>Number of clusters: ${data.num_clusters}</p>
                `;
                clusteringResults.appendChild(header);
                
                // Create clusters
                data.clusters.forEach(cluster => {
                    const clusterCard = document.createElement('div');
                    clusterCard.className = 'card mb-3';
                    
                    // Create card header
                    const cardHeader = document.createElement('div');
                    cardHeader.className = 'card-header bg-primary text-white';
                    cardHeader.innerHTML = `
                        <h6 class="mb-0">Cluster ${cluster.cluster_id} (${cluster.size} submissions)</h6>
                        <small>Centroid value: ${parseFloat(cluster.centroid).toFixed(2)}</small>
                    `;
                    clusterCard.appendChild(cardHeader);
                    
                    // Create card body with submissions table
                    const cardBody = document.createElement('div');
                    cardBody.className = 'card-body';
                    
                    if (cluster.submissions.length > 0) {
                        const table = document.createElement('table');
                        table.className = 'table table-sm table-striped';
                        
                        // Create table header
                        const thead = document.createElement('thead');
                        thead.innerHTML = `
                            <tr>
                                <th>Submitted By</th>
                                <th>Submission Date</th>
                                <th>Value</th>
                                <th>Actions</th>
                            </tr>
                        `;
                        table.appendChild(thead);
                        
                        // Create table body
                        const tbody = document.createElement('tbody');
                        cluster.submissions.forEach(submission => {
                            const tr = document.createElement('tr');
                            const submissionDate = new Date(submission.submitted_at).toLocaleDateString();
                            tr.innerHTML = `
                                <td>${submission.submitted_by}</td>
                                <td>${submissionDate}</td>
                                <td>${submission.value}</td>
                                <td>
                                    <a href="/user/submission/${submission.submission_id}" class="btn btn-sm btn-primary">
                                        <i class="bi bi-eye"></i> View
                                    </a>
                                </td>
                            `;
                            tbody.appendChild(tr);
                        });
                        table.appendChild(tbody);
                        cardBody.appendChild(table);
                    } else {
                        cardBody.innerHTML = '<p class="mb-0">No submissions in this cluster.</p>';
                    }
                    
                    clusterCard.appendChild(cardBody);
                    clusteringResults.appendChild(clusterCard);
                });
                
                // Show the results container
                clusteringContainer.classList.remove('d-none');
            } else {
                // Show error message
                clusteringResults.innerHTML = `
                    <div class="alert alert-danger">
                        <h6 class="alert-heading">Error:</h6>
                        <p>${data.message || 'An error occurred while clustering.'}</p>
                    </div>
                `;
                clusteringContainer.classList.remove('d-none');
            }
        })
        .catch(error => {
            console.error('Error performing clustering:', error);
            bootstrap.Modal.getInstance(clusteringModal).hide();
            
            // Show error message
            clusteringResults.innerHTML = `
                <div class="alert alert-danger">
                    <h6 class="alert-heading">Error:</h6>
                    <p>An error occurred while performing clustering. Please try again later.</p>
                </div>
            `;
            clusteringContainer.classList.remove('d-none');
        })
        .finally(() => {
            // Reset button state
            document.getElementById('clustering-submit-btn').disabled = false;
            document.getElementById('clustering-submit-btn').innerHTML = 'Perform Clustering';
        });
    });
    
    // Handle clustering type change
    document.querySelectorAll('input[name="clustering-type"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const numClustersGroup = document.getElementById('num-clusters-group');
            const membersPerClusterGroup = document.getElementById('members-per-cluster-group');
            
            if (this.value === 'num-clusters') {
                numClustersGroup.classList.remove('d-none');
                membersPerClusterGroup.classList.add('d-none');
            } else {
                numClustersGroup.classList.add('d-none');
                membersPerClusterGroup.classList.remove('d-none');
            }
        });
    });
});