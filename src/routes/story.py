from flask import Blueprint, request, jsonify
from src.models.user import db, User, Child, Story, Illustration
from src.services.ai_services import chatgpt_service, leonardo_service
from datetime import datetime
import json

story_bp = Blueprint('story', __name__)

@story_bp.route('/stories/create', methods=['POST'])
def create_story():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'child_name', 'child_age', 'birth_date', 'birth_month', 'story_idea']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        user_id = data['user_id']
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create or find child
        child = Child.query.filter_by(
            user_id=user_id,
            name=data['child_name']
        ).first()
        
        if not child:
            # Create new child record
            child = Child(
                user_id=user_id,
                name=data['child_name'],
                age=int(data['child_age']),
                birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date(),
                birth_month=data['birth_month'],
                photo_1_url=data.get('photo_1_url', ''),
                photo_2_url=data.get('photo_2_url', '')
            )
            db.session.add(child)
            db.session.flush()  # Get the child ID
        
        # Create story
        story = Story(
            child_id=child.id,
            original_idea=data['story_idea'],
            status='draft'
        )
        db.session.add(story)
        db.session.commit()
        
        return jsonify({
            'message': 'Story creation initiated',
            'story_id': story.id,
            'child': child.to_dict(),
            'story': story.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<int:story_id>/generate', methods=['POST'])
def generate_story_content(story_id):
    """Generate story content using AI services"""
    try:
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        child = story.child
        
        # Use ChatGPT service to generate story
        story_result = chatgpt_service.generate_story(
            child_name=child.name,
            child_age=child.age,
            birth_month=child.birth_month,
            story_idea=story.original_idea
        )
        
        # Update story with generated content
        story.generated_title = story_result['title']
        story.generated_summary = story_result['summary']
        story.set_pages_content(story_result['pages'])
        story.status = 'generated'
        story.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Story generated successfully using AI',
            'story': story.to_dict(),
            'generation_stats': {
                'word_count': story_result['word_count'],
                'generation_time': story_result['generation_time'],
                'pages_generated': len(story_result['pages'])
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<int:story_id>/generate-illustrations', methods=['POST'])
def generate_story_illustrations(story_id):
    """Generate illustrations for story pages using Leonardo.ai simulation"""
    try:
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        child = story.child
        pages_content = story.get_pages_content()
        
        if not pages_content:
            return jsonify({'error': 'Story content not found'}), 400
        
        generated_count = 0
        
        # Generate illustrations for each page
        for page in pages_content:
            page_number = page['page_number']
            illustration_prompt = page.get('illustration_prompt', f"Illustration for {page['title']}")
            
            # Check if illustration already exists
            existing_illustration = Illustration.query.filter_by(
                story_id=story_id,
                page_number=page_number
            ).first()
            
            if not existing_illustration:
                # Use Leonardo.ai service to generate illustrations
                illustration_result = leonardo_service.generate_illustration(
                    prompt=illustration_prompt,
                    child_name=child.name,
                    page_number=page_number,
                    story_id=story_id
                )
                
                # Create illustration record
                illustration = Illustration(
                    story_id=story_id,
                    page_number=page_number,
                    chatgpt_image_url=f"/api/generated/chatgpt/story_{story_id}_page_{page_number}.jpg",
                    status='pending'
                )
                
                # Set Leonardo images
                leonardo_urls = [img['url'] for img in illustration_result['illustrations']]
                illustration.set_leonardo_images(leonardo_urls)
                
                db.session.add(illustration)
                generated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Generated {generated_count} illustrations using AI',
            'story_id': story_id,
            'generated_count': generated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<int:story_id>', methods=['GET'])
def get_story(story_id):
    try:
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        return jsonify({
            'story': story.to_dict(),
            'child': story.child.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<int:story_id>/approve', methods=['PUT'])
def approve_story(story_id):
    try:
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        story.status = 'approved'
        story.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Story approved successfully',
            'story': story.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<int:story_id>/regenerate', methods=['POST'])
def regenerate_story(story_id):
    try:
        data = request.get_json()
        story = Story.query.get(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        child = story.child
        
        # Update story idea if provided
        if data and data.get('new_idea'):
            story.original_idea = data['new_idea']
        
        # Regenerate story using AI service
        story_result = chatgpt_service.generate_story(
            child_name=child.name,
            child_age=child.age,
            birth_month=child.birth_month,
            story_idea=story.original_idea
        )
        
        # Update story with new content
        story.generated_title = story_result['title']
        story.generated_summary = story_result['summary']
        story.set_pages_content(story_result['pages'])
        story.status = 'regenerated'
        story.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Story regenerated successfully using AI',
            'story': story.to_dict(),
            'generation_stats': {
                'word_count': story_result['word_count'],
                'generation_time': story_result['generation_time']
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@story_bp.route('/user/<int:user_id>/stories', methods=['GET'])
def get_user_stories(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all stories for user's children
        stories = db.session.query(Story).join(Child).filter(Child.user_id == user_id).all()
        
        return jsonify({
            'stories': [story.to_dict() for story in stories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

