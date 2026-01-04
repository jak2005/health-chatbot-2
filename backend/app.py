# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.gemini_handler import GeminiHandler
from database.chromadb_manager import ChromaDBManager
from services.health_tips import HealthTipsService
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load configuration
config = Config()

# Initialize handlers
gemini_handler = GeminiHandler(config)
db_manager = ChromaDBManager(config.CHROMA_DB_PATH)

# Initialize services
gemini_handler.set_managers(db_manager)
health_tips_service = HealthTipsService(db_manager)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Health chatbot API is running",
        "features": {
            "chat": True,
            "tips": True,
            "feedback": True
        }
    })

@app.route('/chat', methods=['POST'])
async def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        message = data.get('message')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Get response from Gemini
        response = await gemini_handler.get_response(
            user_id=user_id,
            message=message
        )
        
        # Store chat history
        db_manager.store_chat(user_id, message, response)
        
        return jsonify({
            "response": response,
            "user_id": user_id
        })

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Failed to process chat message"}), 500

@app.route('/tips/random', methods=['GET'])
def get_random_tip():
    """Get random health tip"""
    try:
        category = request.args.get('category')
        tip = health_tips_service.get_random_tip(category)
        
        return jsonify({
            "tip": tip.get('tip', config.DEFAULT_RESPONSE),
            "category": tip.get('category', "general_health"),
            "related_products": tip.get('related_products', [])
        })
    except Exception as e:
        print(f"Error in random tip endpoint: {str(e)}")
        return jsonify({
            "tip": config.DEFAULT_RESPONSE,
            "category": "general_health",
            "related_products": []
        })

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if rating is None:
            return jsonify({"error": "Rating is required"}), 400

        # Store feedback
        db_manager.store_feedback(user_id, rating, comment)
        
        return jsonify({
            "message": "Thank you for your feedback!",
            "status": "success"
        })
    except Exception as e:
        print(f"Error in feedback endpoint: {str(e)}")
        return jsonify({"error": "Failed to process feedback"}), 500

@app.route('/admin/feedback', methods=['GET'])
def get_all_feedback():
    try:
        feedback = db_manager.get_all_feedback()
        return jsonify({
            "status": "success",
            "feedback": feedback
        })
    except Exception as e:
        print(f"Error getting feedback: {str(e)}")
        return jsonify({"error": "Failed to get feedback"}), 500

@app.route('/clear-context', methods=['POST'])
def clear_context():
    """Clear user context"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        gemini_handler.clear_context(user_id)
        
        return jsonify({
            "message": "Context cleared successfully",
            "status": "success"
        })
    except Exception as e:
        print(f"Error clearing context: {str(e)}")
        return jsonify({"error": "Failed to clear context"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)