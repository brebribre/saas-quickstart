import os
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv

from routes.telegram import telegram_bp

# Load environment variables
load_dotenv()

# Environment configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Configure allowed origins based on environment
ALLOWED_ORIGINS = [FRONTEND_URL]
if FLASK_ENV == 'production':
    ALLOWED_ORIGINS.append('https://sellis.netlify.app')

app = Flask(__name__)

# Only enable Swagger in development for security
if FLASK_ENV == 'development':
    swagger = Swagger(app)

CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

# Health check endpoint - Digital Ocean checks the root path by default
@app.route('/')
def health_check():
    """Health check endpoint for Digital Ocean."""
    return '', 200  # Return empty response with 200 status code

# Register blueprints
app.register_blueprint(telegram_bp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Digital Ocean often uses port 8000
    app.run(
        host="0.0.0.0",
        port=port,
        debug=FLASK_ENV == 'development'
    )
