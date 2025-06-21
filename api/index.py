from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "message": "ZingyBooks Backend API", 
        "status": "running",
        "version": "1.0"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy", 
        "message": "ZingyBooks API is running"
    })

@app.route('/api/stories/create', methods=['POST'])
def create_story():
    data = request.get_json()
    return jsonify({
        "success": True,
        "story_id": "demo-story-123",
        "message": "Story creation started",
        "child_name": data.get('child_name', 'Child')
    })

@app.route('/api/stories/<story_id>/generate', methods=['POST'])
def generate_story(story_id):
    return jsonify({
        "success": True,
        "story": {
            "title": "Emma's Magical Adventure",
            "pages": [
                {"page": 3, "content": "Once upon a time, there was a brave little girl named Emma..."},
                {"page": 4, "content": "Emma discovered a magical forest..."},
                {"page": 5, "content": "She met friendly woodland creatures..."}
            ]
        }
    })

@app.route('/api/stories/<story_id>/generate-illustrations', methods=['POST'])
def generate_illustrations(story_id):
    return jsonify({
        "success": True,
        "illustrations": [
            {"page": 3, "image_url": "demo-image-1.jpg"},
            {"page": 4, "image_url": "demo-image-2.jpg"},
            {"page": 5, "image_url": "demo-image-3.jpg"}
        ]
    })

# This is required for Vercel
app = app
