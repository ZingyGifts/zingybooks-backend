from flask import Blueprint, request, jsonify
from src.models.user import db, User, Story, Order, Illustration, Child
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# Simple admin authentication (in production, use proper JWT or session management)
ADMIN_CREDENTIALS = {
    'admin@zingybooks.com': 'admin123'  # Demo credentials
}

def verify_admin(email, password):
    """Verify admin credentials"""
    return ADMIN_CREDENTIALS.get(email) == password

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        if verify_admin(email, password):
            return jsonify({
                'message': 'Admin login successful',
                'admin': {
                    'email': email,
                    'role': 'admin',
                    'login_time': datetime.utcnow().isoformat()
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid admin credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    try:
        # Get dashboard statistics
        total_users = User.query.count()
        total_stories = Story.query.count()
        total_orders = Order.query.count()
        completed_orders = Order.query.filter_by(payment_status='completed').count()
        
        # Revenue calculation
        completed_order_objects = Order.query.filter_by(payment_status='completed').all()
        total_revenue = sum(order.price for order in completed_order_objects)
        
        # Recent orders (last 10)
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        
        # Orders by status
        order_statuses = db.session.query(
            Order.order_status,
            func.count(Order.id).label('count')
        ).group_by(Order.order_status).all()
        
        # Orders by type
        order_types = db.session.query(
            Order.purchase_option,
            func.count(Order.id).label('count')
        ).group_by(Order.purchase_option).all()
        
        # Monthly revenue (last 6 months)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        monthly_revenue = db.session.query(
            func.strftime('%Y-%m', Order.created_at).label('month'),
            func.sum(Order.price).label('revenue')
        ).filter(
            Order.payment_status == 'completed',
            Order.created_at >= six_months_ago
        ).group_by(func.strftime('%Y-%m', Order.created_at)).all()
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'total_stories': total_stories,
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'total_revenue': total_revenue,
                'conversion_rate': round((completed_orders / total_orders * 100) if total_orders > 0 else 0, 2)
            },
            'recent_orders': [order.to_dict() for order in recent_orders],
            'order_statuses': [{'status': status, 'count': count} for status, count in order_statuses],
            'order_types': [{'type': type_name, 'count': count} for type_name, count in order_types],
            'monthly_revenue': [{'month': month, 'revenue': float(revenue or 0)} for month, revenue in monthly_revenue]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/orders', methods=['GET'])
def admin_get_orders():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status')
        
        query = Order.query
        
        if status_filter:
            query = query.filter_by(order_status=status_filter)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': orders.total,
                'pages': orders.pages,
                'has_next': orders.has_next,
                'has_prev': orders.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/orders/<int:order_id>', methods=['GET'])
def admin_get_order_details(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Include full details
        order_dict = order.to_dict()
        order_dict['story'] = order.story.to_dict()
        order_dict['child'] = order.story.child.to_dict()
        order_dict['user'] = order.user.to_dict()
        
        # Get illustrations
        illustrations = Illustration.query.filter_by(story_id=order.story_id).all()
        order_dict['illustrations'] = [ill.to_dict() for ill in illustrations]
        
        return jsonify({
            'order': order_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/orders/<int:order_id>/update-status', methods=['PUT'])
def admin_update_order_status(order_id):
    try:
        data = request.get_json()
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        new_status = data.get('status')
        notes = data.get('notes', '')
        
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

@admin_bp.route('/admin/users', methods=['GET'])
def admin_get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/stories', methods=['GET'])
def admin_get_stories():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status')
        
        query = Story.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        stories = query.order_by(Story.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'stories': [story.to_dict() for story in stories.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': stories.total,
                'pages': stories.pages,
                'has_next': stories.has_next,
                'has_prev': stories.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/stories/<int:story_id>', methods=['GET'])
def admin_get_story_details(story_id):
    try:
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        # Include full details
        story_dict = story.to_dict()
        story_dict['child'] = story.child.to_dict()
        story_dict['user'] = story.child.user.to_dict()
        
        # Get illustrations
        illustrations = Illustration.query.filter_by(story_id=story_id).all()
        story_dict['illustrations'] = [ill.to_dict() for ill in illustrations]
        
        return jsonify({
            'story': story_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/analytics', methods=['GET'])
def admin_analytics():
    try:
        # User registration trends (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_registrations = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= thirty_days_ago
        ).group_by(func.date(User.created_at)).all()
        
        # Story completion rates
        total_stories = Story.query.count()
        approved_stories = Story.query.filter_by(status='approved').count()
        
        # Order conversion funnel
        total_approved_stories = Story.query.filter_by(status='approved').count()
        total_paid_orders = Order.query.filter_by(payment_status='completed').count()
        
        # Average order value
        completed_orders = Order.query.filter_by(payment_status='completed').all()
        avg_order_value = sum(order.price for order in completed_orders) / len(completed_orders) if completed_orders else 0
        
        return jsonify({
            'daily_registrations': [
                {'date': str(date), 'count': count} 
                for date, count in daily_registrations
            ],
            'story_completion_rate': round((approved_stories / total_stories * 100) if total_stories > 0 else 0, 2),
            'order_conversion_rate': round((total_paid_orders / total_approved_stories * 100) if total_approved_stories > 0 else 0, 2),
            'average_order_value': round(avg_order_value, 2),
            'total_stories': total_stories,
            'approved_stories': approved_stories,
            'total_paid_orders': total_paid_orders
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

