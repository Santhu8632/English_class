from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Program, Enquiry, Admin
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Create tables and default admin
with app.app_context():
    db.create_all()
    
    # Create default admin if not exists
    if not Admin.query.filter_by(username='admin').first():
        default_admin = Admin(
            username='admin',
            password=generate_password_hash('admin123')
        )
        db.session.add(default_admin)
        db.session.commit()
    
    # Create programs if not exists
    programs_data = [
        {"name": "College/University Spoken English", "description": "Comprehensive spoken English program for college and university students."},
        {"name": "Interview Softskills", "description": "Master the softskills needed to ace any job interview."},
        {"name": "Corporate Training", "description": "Professional English training for corporate environments."},
        {"name": "American Accent", "description": "Learn to speak with an authentic American accent."},
        {"name": "Personality Development", "description": "Develop a confident and impressive personality."},
        {"name": "Presentation Skills", "description": "Learn to deliver powerful and engaging presentations."}
    ]
    
    for program_data in programs_data:
        if not Program.query.filter_by(name=program_data['name']).first():
            program = Program(name=program_data['name'], description=program_data['description'])
            db.session.add(program)
    
    db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/programs')
def programs():
    programs = Program.query.all()
    return render_template('programs.html', programs=programs)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        contact_no = request.form['contact_no']
        program_id = request.form['program_id']
        
        enquiry = Enquiry(
            name=name,
            email=email,
            address=address,
            contact_no=contact_no,
            program_id=program_id
        )
        
        db.session.add(enquiry)
        db.session.commit()
        
        flash('Your enquiry has been submitted successfully! We will contact you soon.', 'success')
        return redirect(url_for('success'))
    
    programs = Program.query.all()
    return render_template('contact.html', programs=programs)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    enquiries = Enquiry.query.all()
    return render_template('admin_dashboard.html', enquiries=enquiries)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
