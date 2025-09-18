from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline.pipeline import MedRecommendationPipeline
from api_auth import require_api_key, api_manager
from dotenv import load_dotenv
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global pipeline instance
pipeline = None

def init_pipeline():
    """Initialize the medical recommendation pipeline"""
    global pipeline
    try:
        logger.info("Initializing Medical Recommendation Pipeline...")
        pipeline = MedRecommendationPipeline()
        logger.info("Pipeline initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        return False

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/get-api-key')
def get_api_key_page():
    """Serve the API key registration page"""
    return render_template('get_api_key.html')

@app.route('/api/docs')
def api_documentation():
    """Serve API documentation"""
    return render_template('api_docs.html')

@app.route('/api/search', methods=['POST'])
def search_medicines():
    """API endpoint for medicine search"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Please provide a search query'
            }), 400

        if pipeline is None:
            return jsonify({
                'success': False,
                'error': 'Medical recommendation system is not initialized'
            }), 500

        # Get recommendations from your existing pipeline
        logger.info(f"Processing query: {query}")
        recommendation = pipeline.recommend(query)
        
        # Enhance the response with additional metadata
        enhanced_recommendation = f"""
**AI-POWERED MEDICAL RECOMMENDATION**

**Query Processed:** {query}

**Database:** 4+ Lakh Medicines Analyzed

{recommendation}

---
*Powered by Advanced AI • Real-time Analysis • Comprehensive Database*
        """.strip()
        
        return jsonify({
            'success': True,
            'query': query,
            'recommendation': enhanced_recommendation,
            'metadata': {
                'database_size': '4+ Lakh medicines',
                'processing_type': 'AI-powered analysis',
                'response_time': 'Real-time'
            }
        })

    except Exception as e:
        logger.error(f"Error processing search request: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your request'
        }), 500

# ========== API v1 ENDPOINTS (WITH AUTHENTICATION) ==========

@app.route('/api/v1/search', methods=['POST'])
@require_api_key
def api_v1_search():
    """
    Enhanced API endpoint for medicine search (requires API key)
    Headers: X-API-Key: your_api_key_here
    Body: {"query": "medicine name or condition"}
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Query parameter is required",
                "code": "MISSING_QUERY"
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                "success": False,
                "error": "Query cannot be empty",
                "code": "EMPTY_QUERY"
            }), 400

        if pipeline is None:
            return jsonify({
                "success": False,
                "error": "Medical recommendation system is not initialized",
                "code": "PIPELINE_ERROR"
            }), 500

        # Get recommendations from pipeline
        logger.info(f"API v1 request from {request.api_user['user_email']}: {query}")
        recommendation = pipeline.recommend(query)
        
        # Enhanced response
        enhanced_recommendation = f"""
**TheraSwitchRx AI RECOMMENDATION**

**Query:** {query}
**Database:** 6+ Lakh Medicines Analyzed
**Analysis:** Real-time AI Processing

{recommendation}

---
*Powered by Advanced AI • Comprehensive Medical Database • Instant Results*
        """.strip()
        
        return jsonify({
            "success": True,
            "data": {
                "query": query,
                "recommendation": enhanced_recommendation,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4()),
                    "database_size": "6+ Lakh medicines",
                    "processing_type": "AI-powered analysis",
                    "response_time": "< 2 seconds"
                }
            },
            "message": "Recommendations generated successfully",
            "api_usage": {
                "requests_remaining": request.api_user["requests_remaining"],
                "plan": request.api_user["plan"],
                "user": request.api_user["user_email"]
            }
        })
        
    except Exception as e:
        logger.error(f"API v1 search error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/v1/medicine/<medicine_name>', methods=['GET'])
@require_api_key
def get_medicine_info(medicine_name):
    """Get detailed information about a specific medicine"""
    try:
        if pipeline is None:
            return jsonify({
                "success": False,
                "error": "Medical recommendation system is not initialized",
                "code": "PIPELINE_ERROR"
            }), 500
        
        # Use your existing pipeline to get medicine info
        query = f"detailed information about {medicine_name}"
        medicine_info = pipeline.recommend(query)
        
        return jsonify({
            "success": True,
            "data": {
                "medicine_name": medicine_name,
                "information": medicine_info,
                "timestamp": datetime.now().isoformat()
            },
            "message": f"Information for {medicine_name} retrieved successfully",
            "api_usage": {
                "requests_remaining": request.api_user["requests_remaining"],
                "plan": request.api_user["plan"]
            }
        })
        
    except Exception as e:
        logger.error(f"Medicine info error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve medicine information",
            "code": "MEDICINE_INFO_ERROR"
        }), 500

@app.route('/api/v1/alternatives', methods=['POST'])
@require_api_key
def get_bulk_alternatives():
    """
    Get alternatives for multiple medicines
    Body: {"medicines": ["med1", "med2", "med3"]}
    """
    try:
        data = request.get_json()
        
        if not data or 'medicines' not in data:
            return jsonify({
                "success": False,
                "error": "Medicines list is required",
                "code": "MISSING_MEDICINES"
            }), 400
        
        medicines = data['medicines']
        
        if not isinstance(medicines, list) or not medicines:
            return jsonify({
                "success": False,
                "error": "Medicines must be a non-empty list",
                "code": "INVALID_MEDICINES_FORMAT"
            }), 400
        
        if len(medicines) > 10:  # Limit bulk requests
            return jsonify({
                "success": False,
                "error": "Maximum 10 medicines allowed per request",
                "code": "TOO_MANY_MEDICINES"
            }), 400
        
        if pipeline is None:
            return jsonify({
                "success": False,
                "error": "Medical recommendation system is not initialized",
                "code": "PIPELINE_ERROR"
            }), 500
        
        results = {}
        for medicine in medicines:
            try:
                query = f"alternatives for {medicine}"
                alternatives = pipeline.recommend(query)
                results[medicine] = {
                    "alternatives": alternatives,
                    "status": "success"
                }
            except Exception as e:
                results[medicine] = {
                    "error": str(e),
                    "status": "failed"
                }
        
        return jsonify({
            "success": True,
            "data": {
                "results": results,
                "processed_count": len(medicines),
                "timestamp": datetime.now().isoformat()
            },
            "message": f"Alternatives processed for {len(medicines)} medicines",
            "api_usage": {
                "requests_remaining": request.api_user["requests_remaining"],
                "plan": request.api_user["plan"]
            }
        })
        
    except Exception as e:
        logger.error(f"Bulk alternatives error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to process bulk alternatives request",
            "code": "BULK_ALTERNATIVES_ERROR"
        }), 500

# ========== API KEY MANAGEMENT ENDPOINTS ==========

@app.route('/api/v1/get-api-key', methods=['POST'])
def create_api_key():
    """
    Generate a new API key
    Body: {"email": "user@example.com", "name": "User Name", "plan": "free"}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required",
                "code": "MISSING_DATA"
            }), 400
        
        email = data.get('email', '').strip()
        name = data.get('name', '').strip()
        plan = data.get('plan', 'free').strip()
        
        if not email or not name:
            return jsonify({
                "success": False,
                "error": "Email and name are required",
                "code": "MISSING_CREDENTIALS"
            }), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({
                "success": False,
                "error": "Invalid email format",
                "code": "INVALID_EMAIL"
            }), 400
        
        # Validate plan
        if plan not in ['free', 'basic', 'pro', 'enterprise']:
            return jsonify({
                "success": False,
                "error": "Invalid plan type. Choose from: free, basic, pro, enterprise",
                "code": "INVALID_PLAN"
            }), 400
        
        # Generate API key
        result = api_manager.generate_api_key(email, name, plan)
        
        if not result:
            return jsonify({
                "success": False,
                "error": "Failed to generate API key. Email might already be registered.",
                "code": "GENERATION_FAILED"
            }), 400
        
        logger.info(f"New API key generated for {email} ({plan} plan)")
        
        return jsonify({
            "success": True,
            "data": result,
            "message": "API key generated successfully"
        })
        
    except Exception as e:
        logger.error(f"API key generation error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/v1/key-info', methods=['GET'])
@require_api_key
def get_api_key_info():
    """Get information about your API key"""
    return jsonify({
        "success": True,
        "data": {
            "email": request.api_user["user_email"],
            "plan": request.api_user["plan"],
            "requests_remaining": request.api_user["requests_remaining"],
            "status": "active"
        },
        "message": "API key information retrieved successfully"
    })

# ========== PUBLIC ENDPOINTS (NO AUTHENTICATION) ==========

@app.route('/api/v1/health', methods=['GET'])
def api_v1_health():
    """API Health check (public endpoint)"""
    return jsonify({
        "success": True,
        "data": {
            "status": "healthy",
            "version": "1.0.0",
            "pipeline_initialized": pipeline is not None,
            "total_medicines": "6+ lakh",
            "uptime": "Active",
            "features": [
                "Medicine alternatives",
                "AI-powered recommendations", 
                "Real-time processing",
                "Comprehensive database"
            ]
        },
        "message": "TheraSwitchRx API is running"
    })

@app.route('/api/v1/stats', methods=['GET'])
def api_v1_stats():
    """Get API statistics (public endpoint)"""
    return jsonify({
        "success": True,
        "data": {
            "total_medicines": "6+ lakh",
            "api_version": "1.0.0",
            "features": {
                "medicine_search": "Advanced AI search",
                "alternatives": "Smart alternatives",
                "bulk_processing": "Multiple medicines",
                "real_time": "< 2 second response"
            },
            "plans": {
                "free": "100 requests/day",
                "basic": "1,000 requests/day", 
                "pro": "10,000 requests/day",
                "enterprise": "Unlimited"
            }
        },
        "message": "API statistics retrieved successfully"
    })

# ========== LEGACY ENDPOINTS (BACKWARD COMPATIBILITY) ==========

@app.route('/api/health')
def health_check():
    """Legacy health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pipeline_initialized': pipeline is not None
    })

if __name__ == '__main__':
    print("🚀 Starting TheraSwitchRx | by MedQ AI...")
    
    # Initialize the pipeline
    if init_pipeline():
        print("✅ Pipeline initialized successfully!")
        print("🌐 Starting web server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to initialize pipeline. Please check your configuration.")
        sys.exit(1)
