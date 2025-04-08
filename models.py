from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'player' or 'owner'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    player_profile = db.relationship('PlayerProfile', backref='user', uselist=False, lazy=True)
    owner_profile = db.relationship('OwnerProfile', backref='user', uselist=False, lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class PlayerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    
    # Relationships
    bookings = db.relationship('Booking', backref='player', lazy=True)
    
    def __repr__(self):
        return f"PlayerProfile('{self.full_name}')"

class OwnerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    
    # Relationships
    turfs = db.relationship('Turf', backref='owner', lazy=True)
    
    def __repr__(self):
        return f"OwnerProfile('{self.business_name}')"

class Turf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner_profile.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(50))  # e.g., "5-a-side", "7-a-side"
    surface_type = db.Column(db.String(50))  # e.g., "Grass", "Artificial"
    amenities = db.Column(db.Text)  # comma-separated list of amenities
    opening_time = db.Column(db.Time, nullable=False)
    closing_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='turf', lazy=True)
    
    def __repr__(self):
        return f"Turf('{self.name}', '{self.location}', '{self.price_per_hour}')"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player_profile.id'), nullable=False)
    turf_id = db.Column(db.Integer, db.ForeignKey('turf.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid
    payment_id = db.Column(db.String(100))  # To store Stripe payment ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Booking('{self.booking_date}', '{self.start_time}-{self.end_time}', '{self.status}')"

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref='review', uselist=False)
    
    def __repr__(self):
        return f"Review('{self.rating}', '{self.booking_id}')"
