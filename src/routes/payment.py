from flask import Blueprint, request, jsonify
from src.models.user import db, User, Story, Order, Illustration
from datetime import datetime
import json
import random
import string

payment_bp = Blueprint('payment', __name__)

# Pricing configuration
PRICING = {
    'pdf': 497,      # ₹497 for PDF Digital Book
    'paper': 1297,   # ₹1297 for Paperback Printed Book  
    'hard': 1897     # ₹1897 for Hardcover Premium Book
}

def generate_order_id():
    """Generate a unique order ID"""
    timestamp = str(int(datetime.utcnow().timestamp()))
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ZB{timestamp}{random_str}"

def generate_razorpay_order_id():
    """Simulate Razorpay order ID generation"""
    return f"order_{''.join(random.choices(string.ascii_lowercase + string.digits, k=14))}"

def generate_razorpay_payment_id():
    """Simulate Razorpay payment ID generation"""
    return f"pay_{''.join(random.choices(string.ascii_lowercase + string.digits, k=14))}"

@payment_bp.route('/payment/pricing', methods=['GET'])
def get_pricing():
    """Get pricing information for all book types"""
    try:
        return jsonify({
            'pricing': PRICING,
            'currency': 'INR',
            'options': [
                {
                    'type': 'pdf',
                    'name': 'PDF Digital Book',
                    'price': PRICING['pdf'],
                    'description': 'Instant download, high-quality PDF format',
                    'delivery': 'Immediate digital delivery',
                    'features': ['24-page personalized story', 'High-resolution illustrations', 'Instant download']
                },
                {
                    'type': 'paper',
                    'name': 'Paperback Printed Book',
                    'price': PRICING['paper'],
                    'description': 'Physical paperback book with premium printing',
                    'delivery': '7-10 business days',
                    'features': ['24-page personalized story', 'High-quality paperback printing', 'Free shipping in India']
                },
                {
                    'type': 'hard',
                    'name': 'Hardcover Premium Book',
                    'price': PRICING['hard'],
                    'description': 'Premium hardcover book with dust jacket',
                    'delivery': '7-10 business days',
                    'features': ['24-page personalized story', 'Premium hardcover binding', 'Dust jacket included', 'Free shipping in India']
                }
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/payment/create-order', methods=['POST'])
def create_payment_order():
    """Create a payment order for Razorpay"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'story_id', 'book_type']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        user_id = data['user_id']
        story_id = data['story_id']
        book_type = data['book_type']
        
        # Validate book type
        if book_type not in PRICING:
            return jsonify({'error': 'Invalid book type'}), 400
        
        # Verify user and story exist
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        # Check if story is approved
        if story.status != 'approved':
            return jsonify({'error': 'Story must be approved before payment'}), 400
        
        # Check if at least 5 illustrations are approved (as per workflow)
        approved_illustrations = Illustration.query.filter_by(
            story_id=story_id,
            status='approved'
        ).count()
        
        if approved_illustrations < 5:
            return jsonify({'error': 'At least 5 illustrations must be approved before payment'}), 400
        
        # Get price
        price = PRICING[book_type]
        
        # Generate Razorpay order (simulation)
        razorpay_order_id = generate_razorpay_order_id()
        
        # Create order record
        order = Order(
            user_id=user_id,
            story_id=story_id,
            book_title=story.generated_title or f"{story.child.name}'s Story",
            purchase_option=book_type,
            price=price,
            payment_status='pending',
            order_status='new_order',
            razorpay_order_id=razorpay_order_id
        )
        
        # Add shipping details if physical book
        if book_type in ['paper', 'hard']:
            shipping_details = data.get('shipping_details', {})
            if shipping_details:
                order.set_shipping_details(shipping_details)
        
        db.session.add(order)
        db.session.commit()
        
        # Simulate Razorpay order creation response
        razorpay_response = {
            'id': razorpay_order_id,
            'amount': price * 100,  # Razorpay expects amount in paise
            'currency': 'INR',
            'status': 'created'
        }
        
        return jsonify({
            'message': 'Payment order created successfully',
            'order': order.to_dict(),
            'razorpay_order': razorpay_response,
            'key': 'rzp_test_demo_key'  # Demo Razorpay key
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/payment/verify', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment and update order status"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        razorpay_order_id = data['razorpay_order_id']
        razorpay_payment_id = data['razorpay_payment_id']
        razorpay_signature = data['razorpay_signature']
        
        # Find order
        order = Order.query.filter_by(razorpay_order_id=razorpay_order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # In a real application, you would verify the signature using Razorpay's webhook secret
        # For demo purposes, we'll simulate successful verification
        
        # Update order with payment details
        order.razorpay_payment_id = razorpay_payment_id
        order.payment_status = 'completed'
        order.order_status = 'payment_confirmed'
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # If PDF order, generate PDF immediately
        if order.purchase_option == 'pdf':
            order.pdf_file_url = f"/api/generated/pdf/order_{order.id}_book.pdf"
            order.order_status = 'completed'
            db.session.commit()
        
        return jsonify({
            'message': 'Payment verified successfully',
            'order': order.to_dict(),
            'payment_status': 'success'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/payment/webhook', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhook notifications"""
    try:
        data = request.get_json()
        
        # In a real application, you would verify the webhook signature
        # For demo purposes, we'll process the webhook data
        
        event = data.get('event')
        payload = data.get('payload', {})
        
        if event == 'payment.captured':
            payment_entity = payload.get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id')
            payment_id = payment_entity.get('id')
            
            if order_id and payment_id:
                order = Order.query.filter_by(razorpay_order_id=order_id).first()
                if order:
                    order.razorpay_payment_id = payment_id
                    order.payment_status = 'completed'
                    order.order_status = 'payment_confirmed'
                    order.updated_at = datetime.utcnow()
                    db.session.commit()
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    """Get all orders for a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
        
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Include story and child details
        order_dict = order.to_dict()
        order_dict['story'] = order.story.to_dict()
        order_dict['child'] = order.story.child.to_dict()
        
        return jsonify({
            'order': order_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/orders/<int:order_id>/update-status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status (for admin use)"""
    try:
        data = request.get_json()
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        # Valid order statuses
        valid_statuses = [
            'new_order', 'payment_confirmed', 'processing_illustrations',
            'customer_approved_book', 'sent_for_printing', 'packed', 'shipped', 'completed'
        ]
        
        if new_status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        order.order_status = new_status
        order.updated_at = datetime.utcnow()
        
        # If completing PDF order, generate PDF URL
        if new_status == 'completed' and order.purchase_option == 'pdf' and not order.pdf_file_url:
            order.pdf_file_url = f"/api/generated/pdf/order_{order.id}_book.pdf"
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/orders/stats', methods=['GET'])
def get_order_stats():
    """Get order statistics for admin dashboard"""
    try:
        total_orders = Order.query.count()
        completed_orders = Order.query.filter_by(payment_status='completed').count()
        pending_orders = Order.query.filter_by(payment_status='pending').count()
        
        # Revenue calculation
        completed_order_objects = Order.query.filter_by(payment_status='completed').all()
        total_revenue = sum(order.price for order in completed_order_objects)
        
        # Orders by type
        pdf_orders = Order.query.filter_by(purchase_option='pdf', payment_status='completed').count()
        paper_orders = Order.query.filter_by(purchase_option='paper', payment_status='completed').count()
        hard_orders = Order.query.filter_by(purchase_option='hard', payment_status='completed').count()
        
        return jsonify({
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'total_revenue': total_revenue,
            'orders_by_type': {
                'pdf': pdf_orders,
                'paper': paper_orders,
                'hard': hard_orders
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

