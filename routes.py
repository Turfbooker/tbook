import os
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, PlayerProfile, OwnerProfile, Turf, Booking, Review
from forms import PlayerProfileForm, OwnerProfileForm, TurfForm, BookingForm, ReviewForm, SearchForm
import stripe

# Set the Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Get domain for Stripe redirects
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != '' else request.host_url

# Home route
@app.route("/")
@app.route("/home")
def home():
    turfs = Turf.query.order_by(Turf.created_at.desc()).limit(6).all()
    return render_template('home.html', title='Home', turfs=turfs)

# Player routes
@app.route("/player/dashboard")
@login_required
def player_dashboard():
    if current_user.role != 'player':
        flash('Access denied. You must be logged in as a player.', 'danger')
        return redirect(url_for('home'))
    
    # Get recent and upcoming bookings
    upcoming_bookings = Booking.query.filter_by(
        player_id=current_user.player_profile.id
    ).filter(
        Booking.booking_date >= datetime.now().date()
    ).order_by(
        Booking.booking_date, Booking.start_time
    ).limit(5).all()
    
    # Get turfs for recommendations
    recommended_turfs = Turf.query.order_by(Turf.created_at.desc()).limit(4).all()
    
    # Search form
    search_form = SearchForm()
    
    return render_template(
        'player/dashboard.html', 
        title='Player Dashboard',
        upcoming_bookings=upcoming_bookings,
        recommended_turfs=recommended_turfs,
        search_form=search_form
    )

@app.route("/player/profile", methods=['GET', 'POST'])
@login_required
def player_profile():
    if current_user.role != 'player':
        flash('Access denied. You must be logged in as a player.', 'danger')
        return redirect(url_for('home'))
    
    form = PlayerProfileForm()
    if form.validate_on_submit():
        profile = current_user.player_profile
        profile.full_name = form.full_name.data
        profile.phone = form.phone.data
        profile.address = form.address.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('player_profile'))
    elif request.method == 'GET':
        profile = current_user.player_profile
        form.full_name.data = profile.full_name
        form.phone.data = profile.phone
        form.address.data = profile.address
    
    return render_template('player/profile.html', title='Player Profile', form=form)

@app.route("/player/booking_history")
@login_required
def booking_history():
    if current_user.role != 'player':
        flash('Access denied. You must be logged in as a player.', 'danger')
        return redirect(url_for('home'))
    
    # Get all bookings
    bookings = Booking.query.filter_by(
        player_id=current_user.player_profile.id
    ).order_by(
        Booking.booking_date.desc(), Booking.start_time.desc()
    ).all()
    
    return render_template('player/booking_history.html', title='Booking History', bookings=bookings)

@app.route("/turf/<int:turf_id>", methods=['GET', 'POST'])
def turf_details(turf_id):
    turf = Turf.query.get_or_404(turf_id)
    booking_form = BookingForm()
    booking_form.turf_id.data = turf_id
    
    if booking_form.validate_on_submit() and current_user.is_authenticated and current_user.role == 'player':
        # Calculate duration and price
        start_datetime = datetime.combine(booking_form.booking_date.data, booking_form.start_time.data)
        end_datetime = datetime.combine(booking_form.booking_date.data, booking_form.end_time.data)
        duration = (end_datetime - start_datetime).total_seconds() / 3600  # hours
        total_price = duration * turf.price_per_hour
        
        # Create booking
        booking = Booking(
            player_id=current_user.player_profile.id,
            turf_id=turf.id,
            booking_date=booking_form.booking_date.data,
            start_time=booking_form.start_time.data,
            end_time=booking_form.end_time.data,
            total_price=total_price,
            status='pending',
            payment_status='unpaid'
        )
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking created! Proceed to payment.', 'success')
        return redirect(url_for('checkout', booking_id=booking.id))
    
    # Get existing bookings for the selected date to show availability
    if request.args.get('date'):
        selected_date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
        booking_form.booking_date.data = selected_date
    else:
        selected_date = datetime.now().date()
    
    existing_bookings = Booking.query.filter_by(
        turf_id=turf.id, 
        booking_date=selected_date
    ).filter(
        Booking.status.in_(['pending', 'confirmed'])
    ).all()
    
    # Get reviews
    reviews = Review.query.join(Booking).filter(Booking.turf_id == turf.id).all()
    
    return render_template(
        'player/turf_details.html', 
        title=turf.name,
        turf=turf,
        booking_form=booking_form,
        existing_bookings=existing_bookings,
        selected_date=selected_date,
        reviews=reviews
    )

@app.route("/search")
def search_turfs():
    # Get search parameters
    location = request.args.get('location', '')
    date_str = request.args.get('date', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    surface_type = request.args.get('surface_type', '')
    
    # Build the query
    query = Turf.query
    
    if location:
        query = query.filter(Turf.location.ilike(f'%{location}%'))
    
    if surface_type:
        query = query.filter(Turf.surface_type == surface_type)
    
    if min_price:
        query = query.filter(Turf.price_per_hour >= float(min_price))
    
    if max_price:
        query = query.filter(Turf.price_per_hour <= float(max_price))
    
    # Execute the query
    turfs = query.all()
    
    # Initialize search form with current values
    search_form = SearchForm()
    if location:
        search_form.location.data = location
    if date_str:
        search_form.date.data = datetime.strptime(date_str, '%Y-%m-%d').date()
    if min_price:
        search_form.min_price.data = float(min_price)
    if max_price:
        search_form.max_price.data = float(max_price)
    if surface_type:
        search_form.surface_type.data = surface_type
    
    return render_template(
        'player/dashboard.html', 
        title='Search Results',
        turfs=turfs,
        search_form=search_form,
        is_search_results=True
    )

# Turf Owner routes
@app.route("/owner/dashboard")
@login_required
def owner_dashboard():
    if current_user.role != 'owner':
        flash('Access denied. You must be logged in as a turf owner.', 'danger')
        return redirect(url_for('home'))
    
    # Get owner's turfs
    turfs = Turf.query.filter_by(owner_id=current_user.owner_profile.id).all()
    
    # Get recent bookings across all turfs
    recent_bookings = Booking.query.join(Turf).filter(
        Turf.owner_id == current_user.owner_profile.id
    ).order_by(
        Booking.booking_date.desc(), Booking.start_time.desc()
    ).limit(10).all()
    
    # Calculate total earnings
    total_earnings = db.session.query(db.func.sum(Booking.total_price)).join(Turf).filter(
        Turf.owner_id == current_user.owner_profile.id,
        Booking.payment_status == 'paid'
    ).scalar() or 0
    
    # Calculate upcoming bookings
    upcoming_bookings_count = Booking.query.join(Turf).filter(
        Turf.owner_id == current_user.owner_profile.id,
        Booking.booking_date >= datetime.now().date(),
        Booking.status.in_(['pending', 'confirmed'])
    ).count()
    
    return render_template(
        'owner/dashboard.html', 
        title='Owner Dashboard',
        turfs=turfs,
        recent_bookings=recent_bookings,
        total_earnings=total_earnings,
        upcoming_bookings_count=upcoming_bookings_count
    )

@app.route("/owner/profile", methods=['GET', 'POST'])
@login_required
def owner_profile():
    if current_user.role != 'owner':
        flash('Access denied. You must be logged in as a turf owner.', 'danger')
        return redirect(url_for('home'))
    
    form = OwnerProfileForm()
    if form.validate_on_submit():
        profile = current_user.owner_profile
        profile.business_name = form.business_name.data
        profile.phone = form.phone.data
        profile.address = form.address.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('owner_profile'))
    elif request.method == 'GET':
        profile = current_user.owner_profile
        form.business_name.data = profile.business_name
        form.phone.data = profile.phone
        form.address.data = profile.address
    
    return render_template('owner/profile.html', title='Owner Profile', form=form)

@app.route("/owner/turf_management")
@login_required
def turf_management():
    if current_user.role != 'owner':
        flash('Access denied. You must be logged in as a turf owner.', 'danger')
        return redirect(url_for('home'))
    
    turfs = Turf.query.filter_by(owner_id=current_user.owner_profile.id).all()
    return render_template('owner/turf_management.html', title='Turf Management', turfs=turfs)

@app.route("/owner/add_turf", methods=['GET', 'POST'])
@login_required
def add_turf():
    if current_user.role != 'owner':
        flash('Access denied. You must be logged in as a turf owner.', 'danger')
        return redirect(url_for('home'))
    
    form = TurfForm()
    if form.validate_on_submit():
        turf = Turf(
            owner_id=current_user.owner_profile.id,
            name=form.name.data,
            description=form.description.data,
            location=form.location.data,
            price_per_hour=form.price_per_hour.data,
            size=form.size.data,
            surface_type=form.surface_type.data,
            amenities=form.amenities.data,
            opening_time=form.opening_time.data,
            closing_time=form.closing_time.data
        )
        db.session.add(turf)
        db.session.commit()
        
        flash('Your turf has been added!', 'success')
        return redirect(url_for('turf_management'))
    
    return render_template('owner/add_turf.html', title='Add Turf', form=form)

@app.route("/owner/edit_turf/<int:turf_id>", methods=['GET', 'POST'])
@login_required
def edit_turf(turf_id):
    if current_user.role != 'owner':
        flash('Access denied. You must be logged in as a turf owner.', 'danger')
        return redirect(url_for('home'))
    
    turf = Turf.query.get_or_404(turf_id)
    
    # Check if the turf belongs to the current owner
    if turf.owner_id != current_user.owner_profile.id:
        flash('You do not have permission to edit this turf.', 'danger')
        return redirect(url_for('turf_management'))
    
    form = TurfForm()
    if form.validate_on_submit():
        turf.name = form.name.data
        turf.description = form.description.data
        turf.location = form.location.data
        turf.price_per_hour = form.price_per_hour.data
        turf.size = form.size.data
        turf.surface_type = form.surface_type.data
        turf.amenities = form.amenities.data
        turf.opening_time = form.opening_time.data
        turf.closing_time = form.closing_time.data
        
        db.session.commit()
        flash('Your turf has been updated!', 'success')
        return redirect(url_for('turf_management'))
    elif request.method == 'GET':
        form.name.data = turf.name
        form.description.data = turf.description
        form.location.data = turf.location
        form.price_per_hour.data = turf.price_per_hour
        form.size.data = turf.size
        form.surface_type.data = turf.surface_type
        form.amenities.data = turf.amenities
        form.opening_time.data = turf.opening_time
        form.closing_time.data = turf.closing_time
    
    return render_template('owner/add_turf.html', title='Edit Turf', form=form, turf=turf)

@app.route("/owner/booking_requests")
@login_required
def booking_requests():
    if current_user.role != 'owner':
        flash('Access denied. You must be logged in as a turf owner.', 'danger')
        return redirect(url_for('home'))
    
    # Get all bookings for the owner's turfs
    bookings = Booking.query.join(Turf).filter(
        Turf.owner_id == current_user.owner_profile.id
    ).order_by(
        Booking.booking_date, Booking.start_time
    ).all()
    
    return render_template('owner/booking_requests.html', title='Booking Requests', bookings=bookings)

@app.route("/owner/booking/<int:booking_id>/update_status/<status>", methods=['POST'])
@login_required
def update_booking_status(booking_id, status):
    if current_user.role != 'owner':
        flash('Access denied. You must be logged in as a turf owner.', 'danger')
        return redirect(url_for('home'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to one of the owner's turfs
    if booking.turf.owner_id != current_user.owner_profile.id:
        flash('You do not have permission to update this booking.', 'danger')
        return redirect(url_for('booking_requests'))
    
    if status in ['confirmed', 'cancelled']:
        booking.status = status
        db.session.commit()
        flash(f'Booking status updated to {status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
    
    return redirect(url_for('booking_requests'))

# Payment routes
@app.route("/checkout/<int:booking_id>")
@login_required
def checkout(booking_id):
    if current_user.role != 'player':
        flash('Access denied. You must be logged in as a player.', 'danger')
        return redirect(url_for('home'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current player
    if booking.player_id != current_user.player_profile.id:
        flash('You do not have permission to access this booking.', 'danger')
        return redirect(url_for('player_dashboard'))
    
    return render_template('payment/checkout.html', title='Checkout', booking=booking)

@app.route('/create-checkout-session/<int:booking_id>', methods=['POST'])
@login_required
def create_checkout_session(booking_id):
    if current_user.role != 'player':
        flash('Access denied. You must be logged in as a player.', 'danger')
        return redirect(url_for('home'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current player
    if booking.player_id != current_user.player_profile.id:
        flash('You do not have permission to access this booking.', 'danger')
        return redirect(url_for('player_dashboard'))
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': f'Booking for {booking.turf.name}',
                        'description': f'Date: {booking.booking_date}, Time: {booking.start_time} - {booking.end_time}',
                    },
                    'unit_amount': int(booking.total_price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url + f'payment/success/{booking_id}',
            cancel_url=request.host_url + f'payment/cancel/{booking_id}',
        )
        
        # Update booking with payment ID
        booking.payment_id = checkout_session.id
        db.session.commit()
        
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('checkout', booking_id=booking_id))

@app.route('/payment/success/<int:booking_id>')
@login_required
def payment_success(booking_id):
    if current_user.role != 'player':
        flash('Access denied. You must be logged in as a player.', 'danger')
        return redirect(url_for('home'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current player
    if booking.player_id != current_user.player_profile.id:
        flash('You do not have permission to access this booking.', 'danger')
        return redirect(url_for('player_dashboard'))
    
    # Update booking status
    booking.payment_status = 'paid'
    booking.status = 'confirmed'
    db.session.commit()
    
    return render_template('payment/success.html', title='Payment Success', booking=booking)

@app.route('/payment/cancel/<int:booking_id>')
@login_required
def payment_cancel(booking_id):
    if current_user.role != 'player':
        flash('Access denied. You must be logged in as a player.', 'danger')
        return redirect(url_for('home'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current player
    if booking.player_id != current_user.player_profile.id:
        flash('You do not have permission to access this booking.', 'danger')
        return redirect(url_for('player_dashboard'))
    
    return render_template('payment/cancel.html', title='Payment Cancelled', booking=booking)

# Review routes
@app.route("/review/<int:booking_id>", methods=['GET', 'POST'])
@login_required
def add_review(booking_id):
    if current_user.role != 'player':
        flash('Access denied. You must be logged in as a player.', 'danger')
        return redirect(url_for('home'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current player
    if booking.player_id != current_user.player_profile.id:
        flash('You do not have permission to review this booking.', 'danger')
        return redirect(url_for('player_dashboard'))
    
    # Check if the booking is completed
    if booking.status != 'completed':
        flash('You can only review completed bookings.', 'danger')
        return redirect(url_for('booking_history'))
    
    # Check if a review already exists
    existing_review = Review.query.filter_by(booking_id=booking_id).first()
    if existing_review:
        flash('You have already reviewed this booking.', 'info')
        return redirect(url_for('booking_history'))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            booking_id=booking_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('booking_history'))
    
    return render_template('player/add_review.html', title='Add Review', form=form, booking=booking)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
