# app.py
# Main application file for the Form Management System

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'matchit_secret_key'  # Secret key for session management

# Data file paths
USERS_FILE = os.path.join('data', 'users.json')
FORMS_FILE = os.path.join('data', 'forms.json')
SUBMISSIONS_FILE = os.path.join('data', 'submissions.json')

# Ensure data directory and files exist
def ensure_data_files():
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Create users file if it doesn't exist
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({
                'admin': {
                    'password': 'admin123',
                    'role': 'admin',
                    'name': 'Administrator'
                },
                'user': {
                    'password': 'user123',
                    'role': 'user',
                    'name': 'Test User'
                }
            }, f, indent=4)
    
    # Create forms file if it doesn't exist
    if not os.path.exists(FORMS_FILE):
        with open(FORMS_FILE, 'w') as f:
            json.dump([], f, indent=4)
    
    # Create submissions file if it doesn't exist
    if not os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, 'w') as f:
            json.dump([], f, indent=4)

# Load data from JSON file
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return None

# Save data to JSON file
def save_data(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")
        return False

# Routes
@app.route('/')
def index():
    if 'username' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_data(USERS_FILE)
        if users and username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            session['name'] = users[username]['name']
            
            if users[username]['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('name', None)
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    forms = load_data(FORMS_FILE)
    return render_template('admin_dashboard.html', forms=forms)

@app.route('/admin/form/new', methods=['GET', 'POST'])
def new_form():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        form_data = request.form.to_dict()
        form_fields = []
        
        # Extract form fields from the submitted data
        i = 0
        while f'field_name_{i}' in form_data:
            if form_data[f'field_name_{i}'].strip():
                field = {
                    'name': form_data[f'field_name_{i}'],
                    'type': form_data[f'field_type_{i}'],
                    'required': f'field_required_{i}' in form_data,
                    'options': form_data.get(f'field_options_{i}', '').split(',') if form_data.get(f'field_options_{i}') else []
                }
                form_fields.append(field)
            i += 1
        
        # Create new form
        new_form = {
            'id': str(uuid.uuid4()),
            'title': form_data['form_title'],
            'description': form_data['form_description'],
            'created_by': session['username'],
            'created_at': datetime.now().isoformat(),
            'fields': form_fields,
            'active': True
        }
        
        # Save the new form
        forms = load_data(FORMS_FILE)
        forms.append(new_form)
        save_data(FORMS_FILE, forms)
        
        flash('Form created successfully')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('form_editor.html')

@app.route('/admin/form/<form_id>/edit', methods=['GET', 'POST'])
def edit_form(form_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    forms = load_data(FORMS_FILE)
    form = next((f for f in forms if f['id'] == form_id), None)
    
    if not form:
        flash('Form not found')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        form_data = request.form.to_dict()
        form_fields = []
        
        # Extract form fields from the submitted data
        i = 0
        while f'field_name_{i}' in form_data:
            if form_data[f'field_name_{i}'].strip():
                field = {
                    'name': form_data[f'field_name_{i}'],
                    'type': form_data[f'field_type_{i}'],
                    'required': f'field_required_{i}' in form_data,
                    'options': form_data.get(f'field_options_{i}', '').split(',') if form_data.get(f'field_options_{i}') else []
                }
                form_fields.append(field)
            i += 1
        
        # Update form
        form['title'] = form_data['form_title']
        form['description'] = form_data['form_description']
        form['fields'] = form_fields
        form['updated_at'] = datetime.now().isoformat()
        
        # Save the updated form
        save_data(FORMS_FILE, forms)
        
        flash('Form updated successfully')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('form_editor.html', form=form)

@app.route('/admin/form/<form_id>/toggle', methods=['POST'])
def toggle_form(form_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    forms = load_data(FORMS_FILE)
    form = next((f for f in forms if f['id'] == form_id), None)
    
    if form:
        form['active'] = not form['active']
        save_data(FORMS_FILE, forms)
        status = 'activated' if form['active'] else 'deactivated'
        flash(f'Form {status} successfully')
    else:
        flash('Form not found')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/submissions')
def view_all_submissions():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    submissions = load_data(SUBMISSIONS_FILE)
    forms = load_data(FORMS_FILE)
    
    # Create a lookup dictionary for form titles
    form_titles = {form['id']: form['title'] for form in forms}
    
    return render_template('all_submissions.html', submissions=submissions, form_titles=form_titles)

@app.route('/admin/form/<form_id>/submissions')
def view_form_submissions(form_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    submissions = load_data(SUBMISSIONS_FILE)
    forms = load_data(FORMS_FILE)
    
    form = next((f for f in forms if f['id'] == form_id), None)
    if not form:
        flash('Form not found')
        return redirect(url_for('admin_dashboard'))
    
    # Filter submissions for this form
    form_submissions = [s for s in submissions if s['form_id'] == form_id]
    
    return render_template('form_submissions.html', submissions=form_submissions, form=form)

# User routes
@app.route('/user/dashboard')
def user_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    forms = load_data(FORMS_FILE)
    active_forms = [f for f in forms if f['active']]
    
    # Get user's submissions
    submissions = load_data(SUBMISSIONS_FILE)
    user_submissions = [s for s in submissions if s['submitted_by'] == session['username']]
    
    # Create a lookup dictionary for form titles
    form_titles = {form['id']: form['title'] for form in forms}
    
    return render_template('user_dashboard.html', 
                           forms=active_forms, 
                           submissions=user_submissions,
                           form_titles=form_titles)

@app.route('/user/form/<form_id>', methods=['GET', 'POST'])
def fill_form(form_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    forms = load_data(FORMS_FILE)
    form = next((f for f in forms if f['id'] == form_id and f['active']), None)
    
    if not form:
        flash('Form not found or inactive')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        submission_data = {}
        for field in form['fields']:
            field_name = field['name']
            if field['type'] == 'checkbox':
                submission_data[field_name] = request.form.getlist(field_name)
            else:
                submission_data[field_name] = request.form.get(field_name, '')
        
        # Create new submission
        submission = {
            'id': str(uuid.uuid4()),
            'form_id': form_id,
            'submitted_by': session['username'],
            'submitted_at': datetime.now().isoformat(),
            'data': submission_data
        }
        
        # Save the submission
        submissions = load_data(SUBMISSIONS_FILE)
        submissions.append(submission)
        save_data(SUBMISSIONS_FILE, submissions)
        
        flash('Form submitted successfully')
        return redirect(url_for('user_dashboard'))
    
    return render_template('fill_form.html', form=form)

@app.route('/user/submission/<submission_id>')
def view_submission(submission_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    submissions = load_data(SUBMISSIONS_FILE)
    submission = next((s for s in submissions if s['id'] == submission_id), None)
    
    if not submission or (session.get('role') != 'admin' and submission['submitted_by'] != session['username']):
        flash('Submission not found or access denied')
        return redirect(url_for('user_dashboard'))
    
    forms = load_data(FORMS_FILE)
    form = next((f for f in forms if f['id'] == submission['form_id']), None)
    
    if not form:
        flash('Associated form not found')
        return redirect(url_for('user_dashboard'))
    
    return render_template('view_submission.html', submission=submission, form=form)

# API routes for AJAX operations
@app.route('/api/forms', methods=['GET'])
def api_get_forms():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    forms = load_data(FORMS_FILE)
    if session.get('role') != 'admin':
        forms = [f for f in forms if f['active']]
    
    return jsonify(forms)

@app.route('/api/form/<form_id>', methods=['GET'])
def api_get_form(form_id):
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    forms = load_data(FORMS_FILE)
    form = next((f for f in forms if f['id'] == form_id), None)
    
    if not form or (session.get('role') != 'admin' and not form['active']):
        return jsonify({'error': 'Form not found or inactive'}), 404
    
    return jsonify(form)

@app.route('/api/submissions/<form_id>', methods=['GET'])
def api_get_submissions(form_id):
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    submissions = load_data(SUBMISSIONS_FILE)
    
    if session.get('role') == 'admin':
        form_submissions = [s for s in submissions if s['form_id'] == form_id]
    else:
        form_submissions = [s for s in submissions if s['form_id'] == form_id and s['submitted_by'] == session['username']]
    
    return jsonify(form_submissions)

@app.route('/api/calculate_average/<form_id>/<field_name>', methods=['GET'])
def api_calculate_average(form_id, field_name):
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    # Import the calculate_average module
    from function.calculate_average import calculate_average_for_field
    
    # Calculate the average for the specified field
    average, numeric_count, non_numeric_count = calculate_average_for_field(form_id, field_name)
    
    # Return the results as JSON
    return jsonify({
        'average': average,
        'numeric_count': numeric_count,
        'non_numeric_count': non_numeric_count
    })

@app.route('/api/calculate_maximum/<form_id>/<field_name>', methods=['GET'])
def api_calculate_maximum(form_id, field_name):
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    # Import the calculate_maximum module
    from function.calculate_maximum import calculate_maximum_for_field
    
    # Calculate the maximum for the specified field
    maximum, numeric_count, non_numeric_count = calculate_maximum_for_field(form_id, field_name)
    
    # Return the results as JSON
    return jsonify({
        'maximum': maximum,
        'numeric_count': numeric_count,
        'non_numeric_count': non_numeric_count
    })

@app.route('/api/calculate_minimum/<form_id>/<field_name>', methods=['GET'])
def api_calculate_minimum(form_id, field_name):
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    # Import the calculate_minimum module
    from function.calculate_minimum import calculate_minimum_for_field
    
    # Calculate the minimum for the specified field
    minimum, numeric_count, non_numeric_count = calculate_minimum_for_field(form_id, field_name)
    
    # Return the results as JSON
    return jsonify({
        'minimum': minimum,
        'numeric_count': numeric_count,
        'non_numeric_count': non_numeric_count
    })

if __name__ == '__main__':
    ensure_data_files()
    app.run(debug=True)