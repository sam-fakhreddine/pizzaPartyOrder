from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify
import os

auth_bp = Blueprint('auth', __name__)

# Route to display login page
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
            session['logged_in'] = True
            return redirect(url_for('manager.manage'))
        return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')

# Route to log out
@auth_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('auth.login'))
