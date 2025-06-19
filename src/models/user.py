from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for Google OAuth users
    google_id = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    children = db.relationship('Child', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_month = db.Column(db.String(20), nullable=False)
    photo_1_url = db.Column(db.String(255), nullable=False)
    photo_2_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stories = db.relationship('Story', backref='child', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Child {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'birth_month': self.birth_month,
            'photo_1_url': self.photo_1_url,
            'photo_2_url': self.photo_2_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    original_idea = db.Column(db.Text, nullable=False)
    generated_title = db.Column(db.String(200), nullable=True)
    generated_summary = db.Column(db.Text, nullable=True)
    pages_content = db.Column(db.Text, nullable=True)  # JSON string of all pages
    status = db.Column(db.String(20), default='draft')  # draft, approved, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    illustrations = db.relationship('Illustration', backref='story', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='story', lazy=True)

    def __repr__(self):
        return f'<Story {self.generated_title or "Untitled"}>'

    def get_pages_content(self):
        """Parse pages_content JSON string"""
        if self.pages_content:
            try:
                return json.loads(self.pages_content)
            except json.JSONDecodeError:
                return []
        return []

    def set_pages_content(self, pages_list):
        """Set pages_content as JSON string"""
        self.pages_content = json.dumps(pages_list)

    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'original_idea': self.original_idea,
            'generated_title': self.generated_title,
            'generated_summary': self.generated_summary,
            'pages_content': self.get_pages_content(),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Illustration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    chatgpt_image_url = db.Column(db.String(255), nullable=True)
    leonardo_images = db.Column(db.Text, nullable=True)  # JSON array of image URLs
    approved_image_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Illustration Page {self.page_number} for Story {self.story_id}>'

    def get_leonardo_images(self):
        """Parse leonardo_images JSON string"""
        if self.leonardo_images:
            try:
                return json.loads(self.leonardo_images)
            except json.JSONDecodeError:
                return []
        return []

    def set_leonardo_images(self, images_list):
        """Set leonardo_images as JSON string"""
        self.leonardo_images = json.dumps(images_list)

    def to_dict(self):
        return {
            'id': self.id,
            'story_id': self.story_id,
            'page_number': self.page_number,
            'chatgpt_image_url': self.chatgpt_image_url,
            'leonardo_images': self.get_leonardo_images(),
            'approved_image_url': self.approved_image_url,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    book_title = db.Column(db.String(200), nullable=False)
    purchase_option = db.Column(db.String(20), nullable=False)  # pdf, paper, hard
    price = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    order_status = db.Column(db.String(30), default='new_order')  # new_order, payment_confirmed, processing_illustrations, customer_approved_book, sent_for_printing, packed, shipped, completed
    razorpay_order_id = db.Column(db.String(100), nullable=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    shipping_details = db.Column(db.Text, nullable=True)  # JSON string for shipping info
    pdf_file_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Order {self.id} - {self.book_title}>'

    def get_shipping_details(self):
        """Parse shipping_details JSON string"""
        if self.shipping_details:
            try:
                return json.loads(self.shipping_details)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_shipping_details(self, details_dict):
        """Set shipping_details as JSON string"""
        self.shipping_details = json.dumps(details_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'story_id': self.story_id,
            'book_title': self.book_title,
            'purchase_option': self.purchase_option,
            'price': self.price,
            'payment_status': self.payment_status,
            'order_status': self.order_status,
            'razorpay_order_id': self.razorpay_order_id,
            'razorpay_payment_id': self.razorpay_payment_id,
            'shipping_details': self.get_shipping_details(),
            'pdf_file_url': self.pdf_file_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# OTP Model for authentication
class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<OTP {self.email}>'

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_used': self.is_used
        }

