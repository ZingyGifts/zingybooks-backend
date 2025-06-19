from flask import Blueprint, request, jsonify
from src.models.user import db, Story, Illustration
from datetime import datetime

illustration_bp = Blueprint('illustration', __name__)

@illustration_bp.route('/illustrations/story/<int:story_id>', methods=['GET'])
def get_story_illustrations(story_id):
    try:
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        illustrations = Illustration.query.filter_by(story_id=story_id).order_by(Illustration.page_number).all()
        
        return jsonify({
            'illustrations': [illustration.to_dict() for illustration in illustrations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@illustration_bp.route('/illustrations/<int:story_id>/generate', methods=['POST'])
def generate_illustrations(story_id):
    """Generate illustrations for a story"""
    try:
        data = request.get_json()
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        pages_content = story.get_pages_content()
        if not pages_content:
            return jsonify({'error': 'Story content not found'}), 400
        
        # Generate illustrations for each page (simulate AI generation)
        generated_count = 0
        for page in pages_content:
            page_number = page['page_number']
            
            # Check if illustration already exists
            existing_illustration = Illustration.query.filter_by(
                story_id=story_id,
                page_number=page_number
            ).first()
            
            if not existing_illustration:
                # Simulate ChatGPT image generation
                chatgpt_image_url = f"/api/generated/chatgpt/story_{story_id}_page_{page_number}.jpg"
                
                # Simulate Leonardo.ai image generation (2 images per page)
                leonardo_images = [
                    f"/api/generated/leonardo/story_{story_id}_page_{page_number}_option_1.jpg",
                    f"/api/generated/leonardo/story_{story_id}_page_{page_number}_option_2.jpg"
                ]
                
                illustration = Illustration(
                    story_id=story_id,
                    page_number=page_number,
                    chatgpt_image_url=chatgpt_image_url,
                    status='pending'
                )
                illustration.set_leonardo_images(leonardo_images)
                
                db.session.add(illustration)
                generated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Generated {generated_count} illustrations',
            'story_id': story_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@illustration_bp.route('/illustrations/<int:illustration_id>/approve', methods=['PUT'])
def approve_illustration(illustration_id):
    try:
        data = request.get_json()
        illustration = Illustration.query.get(illustration_id)
        if not illustration:
            return jsonify({'error': 'Illustration not found'}), 404
        
        # Set approved image URL
        approved_image_url = data.get('approved_image_url')
        if not approved_image_url:
            return jsonify({'error': 'Approved image URL is required'}), 400
        
        illustration.approved_image_url = approved_image_url
        illustration.status = 'approved'
        db.session.commit()
        
        return jsonify({
            'message': 'Illustration approved successfully',
            'illustration': illustration.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@illustration_bp.route('/illustrations/<int:illustration_id>/regenerate', methods=['POST'])
def regenerate_illustration(illustration_id):
    try:
        illustration = Illustration.query.get(illustration_id)
        if not illustration:
            return jsonify({'error': 'Illustration not found'}), 404
        
        # Simulate regeneration by updating URLs with timestamp
        timestamp = int(datetime.utcnow().timestamp())
        
        illustration.chatgpt_image_url = f"/api/generated/chatgpt/story_{illustration.story_id}_page_{illustration.page_number}_{timestamp}.jpg"
        
        leonardo_images = [
            f"/api/generated/leonardo/story_{illustration.story_id}_page_{illustration.page_number}_option_1_{timestamp}.jpg",
            f"/api/generated/leonardo/story_{illustration.story_id}_page_{illustration.page_number}_option_2_{timestamp}.jpg"
        ]
        illustration.set_leonardo_images(leonardo_images)
        illustration.status = 'pending'
        illustration.approved_image_url = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Illustration regenerated successfully',
            'illustration': illustration.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@illustration_bp.route('/illustrations/story/<int:story_id>/approved-count', methods=['GET'])
def get_approved_illustrations_count(story_id):
    try:
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        approved_count = Illustration.query.filter_by(
            story_id=story_id,
            status='approved'
        ).count()
        
        total_count = Illustration.query.filter_by(story_id=story_id).count()
        
        return jsonify({
            'approved_count': approved_count,
            'total_count': total_count,
            'ready_for_payment': approved_count >= 5  # Payment after 5 approved illustrations
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

