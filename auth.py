from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User, PlayerProfile, OwnerProfile
from forms import LoginForm, SignupForm

from app import app

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'player':
            return redirect(url_for('player_dashboard'))
        else:
            return redirect(url_for('owner_dashboard'))
            
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data) and user.role == form.role.data:
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            
            if user.role == 'player':
                return redirect(next_page) if next_page else redirect(url_for('player_dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('owner_dashboard'))
        else:
            flash('Login unsuccessful. Please check email, password and role.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        if current_user.role == 'player':
            return redirect(url_for('player_dashboard'))
        else:
            return redirect(url_for('owner_dashboard'))
            
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        
        # Create corresponding profile
        if user.role == 'player':
            profile = PlayerProfile(user_id=user.id)
            db.session.add(profile)
        else:
            profile = OwnerProfile(user_id=user.id)
            db.session.add(profile)
            
        db.session.commit()
        
        flash(f'Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', title='Sign Up', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))
