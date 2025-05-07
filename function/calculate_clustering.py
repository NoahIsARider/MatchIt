# calculate_clustering.py
# Module for clustering form submissions based on numeric field values

import json
import os
import random
from typing import Dict, List, Union, Tuple, Optional

# Data file paths
SUBMISSIONS_FILE = os.path.join('data', 'submissions.json')
FORMS_FILE = os.path.join('data', 'forms.json')


def load_data(file_path: str) -> List[Dict]:
    """
    Load data from a JSON file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of dictionaries containing the data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return []


def is_numeric(value: str) -> bool:
    """
    Check if a value can be converted to a number
    
    Args:
        value: The value to check
        
    Returns:
        True if the value can be converted to a number, False otherwise
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def get_form_field_type(form_id: str, field_name: str) -> Optional[str]:
    """
    Get the type of a field in a form
    
    Args:
        form_id: ID of the form
        field_name: Name of the field
        
    Returns:
        Type of the field or None if not found
    """
    forms = load_data(FORMS_FILE)
    for form in forms:
        if form['id'] == form_id:
            for field in form['fields']:
                if field['name'] == field_name:
                    return field['type']
    return None


def extract_numeric_values(form_id: str, field_name: str) -> Tuple[List[Dict], List[float], int]:
    """
    Extract numeric values for a specific field from form submissions
    
    Args:
        form_id: ID of the form
        field_name: Name of the field to extract values from
        
    Returns:
        Tuple containing (list of submissions with numeric values,
                         list of numeric values,
                         count of non-numeric values skipped)
    """
    submissions = load_data(SUBMISSIONS_FILE)
    
    # Filter submissions for the specified form
    form_submissions = [s for s in submissions if s['form_id'] == form_id]
    
    if not form_submissions:
        return [], [], 0
    
    # Check if the field is numeric type
    field_type = get_form_field_type(form_id, field_name)
    if field_type not in ['number', 'radio', 'select', 'checkbox']:
        return [], [], 0
    
    valid_submissions = []
    numeric_values = []
    non_numeric_count = 0
    
    for submission in form_submissions:
        if field_name in submission['data']:
            value = submission['data'][field_name]
            
            # Handle different types of values
            if isinstance(value, list):  # For checkbox fields
                # For clustering, we'll use the first numeric value in the list
                numeric_found = False
                for item in value:
                    if is_numeric(item):
                        numeric_values.append(float(item))
                        valid_submissions.append(submission)
                        numeric_found = True
                        break
                if not numeric_found:
                    non_numeric_count += 1
            elif is_numeric(value):
                numeric_values.append(float(value))
                valid_submissions.append(submission)
            else:
                non_numeric_count += 1
    
    return valid_submissions, numeric_values, non_numeric_count


def calculate_distance(point1: float, point2: float) -> float:
    """
    Calculate the Euclidean distance between two points
    
    Args:
        point1: First point
        point2: Second point
        
    Returns:
        Euclidean distance between the points
    """
    return abs(point1 - point2)


def assign_to_clusters(data_points: List[float], centroids: List[float]) -> List[int]:
    """
    Assign each data point to the nearest centroid
    
    Args:
        data_points: List of data points
        centroids: List of centroid values
        
    Returns:
        List of cluster assignments (indices of centroids)
    """
    assignments = []
    for point in data_points:
        # Find the nearest centroid
        min_distance = float('inf')
        nearest_centroid = 0
        
        for i, centroid in enumerate(centroids):
            distance = calculate_distance(point, centroid)
            if distance < min_distance:
                min_distance = distance
                nearest_centroid = i
        
        assignments.append(nearest_centroid)
    
    return assignments


def update_centroids(data_points: List[float], assignments: List[int], k: int) -> List[float]:
    """
    Update centroid values based on the mean of assigned points
    
    Args:
        data_points: List of data points
        assignments: List of cluster assignments
        k: Number of clusters
        
    Returns:
        List of updated centroid values
    """
    new_centroids = [0.0] * k
    counts = [0] * k
    
    # Sum up all points in each cluster
    for i, assignment in enumerate(assignments):
        new_centroids[assignment] += data_points[i]
        counts[assignment] += 1
    
    # Calculate the mean for each cluster
    for i in range(k):
        if counts[i] > 0:
            new_centroids[i] /= counts[i]
        else:
            # If a cluster is empty, keep the old centroid or assign a random point
            if data_points:
                new_centroids[i] = random.choice(data_points)
    
    return new_centroids


def kmeans_clustering(data_points: List[float], k: int, max_iterations: int = 100) -> Tuple[List[int], List[float]]:
    """
    Perform K-means clustering on the data points
    
    Args:
        data_points: List of data points
        k: Number of clusters
        max_iterations: Maximum number of iterations
        
    Returns:
        Tuple containing (list of cluster assignments, list of centroid values)
    """
    if not data_points or k <= 0 or k > len(data_points):
        return [], []
    
    # Initialize centroids randomly
    centroids = random.sample(data_points, k)
    
    for _ in range(max_iterations):
        # Assign points to clusters
        assignments = assign_to_clusters(data_points, centroids)
        
        # Update centroids
        new_centroids = update_centroids(data_points, assignments, k)
        
        # Check for convergence
        if all(abs(new - old) < 0.001 for new, old in zip(new_centroids, centroids)):
            break
        
        centroids = new_centroids
    
    return assign_to_clusters(data_points, centroids), centroids


def cluster_submissions(form_id: str, field_name: str, num_clusters: int = None, members_per_cluster: int = None) -> Dict:
    """
    Cluster form submissions based on a numeric field value
    
    Args:
        form_id: ID of the form
        field_name: Name of the field to cluster by
        num_clusters: Number of clusters to create (if None, will use members_per_cluster)
        members_per_cluster: Target number of members per cluster (if None, will use num_clusters)
        
    Returns:
        Dictionary containing clustering results
    """
    submissions, numeric_values, non_numeric_count = extract_numeric_values(form_id, field_name)
    
    if not submissions or not numeric_values:
        return {
            'success': False,
            'message': 'No numeric values found for clustering',
            'non_numeric_count': non_numeric_count
        }
    
    # Determine the number of clusters
    if num_clusters is None and members_per_cluster is None:
        # Default to 3 clusters if neither is specified
        num_clusters = 3
    elif num_clusters is None:
        # Calculate number of clusters based on members_per_cluster
        num_clusters = max(1, len(numeric_values) // members_per_cluster)
    
    # Ensure we don't have more clusters than data points
    num_clusters = min(num_clusters, len(numeric_values))
    
    # Perform K-means clustering
    assignments, centroids = kmeans_clustering(numeric_values, num_clusters)
    
    # Group submissions by cluster
    clusters = [[] for _ in range(num_clusters)]
    for i, assignment in enumerate(assignments):
        clusters[assignment].append({
            'submission_id': submissions[i]['id'],
            'submitted_by': submissions[i]['submitted_by'],
            'submitted_at': submissions[i]['submitted_at'],
            'value': numeric_values[i]
        })
    
    # Sort clusters by centroid value
    sorted_clusters = sorted(zip(centroids, clusters))
    
    # Format the results
    result_clusters = []
    for i, (centroid, cluster) in enumerate(sorted_clusters):
        result_clusters.append({
            'cluster_id': i + 1,
            'centroid': centroid,
            'size': len(cluster),
            'submissions': cluster
        })
    
    return {
        'success': True,
        'field_name': field_name,
        'num_clusters': num_clusters,
        'total_submissions': len(numeric_values),
        'non_numeric_count': non_numeric_count,
        'clusters': result_clusters
    }