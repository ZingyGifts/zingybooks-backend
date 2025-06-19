from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return {"message": "ZingyBooks Backend API", "status": "running"}

@app.route('/api/health')
def health():
    return {"status": "healthy", "message": "ZingyBooks API is running"}

@app.route('/api/test')
def test():
    return {"message": "Backend is working!", "version": "1.0"}

# Vercel serverless function handler
def handler(request, context):
    return app(request, context)

if __name__ == "__main__":
    app.run(debug=True)
