from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, TimeField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User
from datetime import datetime, time

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Login as', choices=[('player', 'Player'), ('owner', 'Turf Owner')], validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Register as', choices=[('player', 'Player'), ('owner', 'Turf Owner')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class PlayerProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Update Profile')

class OwnerProfileForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Update Profile')

class TurfForm(FlaskForm):
    name = StringField('Turf Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    price_per_hour = FloatField('Price Per Hour (₹)', validators=[DataRequired()])
    size = StringField('Size (e.g., 5-a-side)', validators=[DataRequired(), Length(max=50)])
    surface_type = SelectField('Surface Type', choices=[
        ('grass', 'Natural Grass'), 
        ('artificial', 'Artificial Grass'),
        ('synthetic', 'Synthetic Turf'),
        ('indoor', 'Indoor')
    ], validators=[DataRequired()])
    amenities = TextAreaField('Amenities (comma separated)', validators=[DataRequired()])
    opening_time = TimeField('Opening Time', validators=[DataRequired()], format='%H:%M')
    closing_time = TimeField('Closing Time', validators=[DataRequired()], format='%H:%M')
    submit = SubmitField('Save Turf')
    
    def validate_closing_time(self, closing_time):
        if self.opening_time.data >= closing_time.data:
            raise ValidationError('Closing time must be after opening time.')

class BookingForm(FlaskForm):
    turf_id = HiddenField('Turf ID', validators=[DataRequired()])
    booking_date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', validators=[DataRequired()], format='%H:%M')
    submit = SubmitField('Book Now')
    
    def validate_booking_date(self, booking_date):
        if booking_date.data < datetime.now().date():
            raise ValidationError('Booking date cannot be in the past.')
    
    def validate_end_time(self, end_time):
        if self.start_time.data >= end_time.data:
            raise ValidationError('End time must be after start time.')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], 
                         validators=[DataRequired()], coerce=int)
    comment = TextAreaField('Comment', validators=[Length(max=500)])
    submit = SubmitField('Submit Review')

class SearchForm(FlaskForm):
    location = StringField('Location')
    date = DateField('Date', format='%Y-%m-%d')
    min_price = FloatField('Min Price')
    max_price = FloatField('Max Price')
    surface_type = SelectField('Surface Type', choices=[
        ('', 'Any'), 
        ('grass', 'Natural Grass'), 
        ('artificial', 'Artificial Grass'),
        ('synthetic', 'Synthetic Turf'),
        ('indoor', 'Indoor')
    ])
    submit = SubmitField('Search')
