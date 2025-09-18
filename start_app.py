#!/usr/bin/env python3
"""
Enhanced Medical Alternatives Recommender Web Application
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, render_template, request, jsonify
    from flask_cors import CORS
    from pipeline.pipeline import MedRecommendationPipeline
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please make sure all required packages are installed:")
    print("pip install flask flask-cors python-dotenv")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        logger.info("🔄 Initializing Medical Recommendation Pipeline...")
        pipeline = MedRecommendationPipeline()
        logger.info("✅ Pipeline initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize pipeline: {e}")
        return False

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

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
        logger.info(f"🔍 Processing query: {query}")
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
                'response_time': 'Real-time',
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"❌ Error processing search request: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your request'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pipeline_initialized': pipeline is not None,
        'timestamp': datetime.now().isoformat()
    })

def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    return None

if __name__ == '__main__':
    print("🚀 Starting TheraSwitchRx | by MedQ AI...")
    print("=" * 60)
    
    # Initialize the pipeline
    if not init_pipeline():
        print("❌ Failed to initialize pipeline. Please check your configuration.")
        sys.exit(1)
    
    # Find available port
    port = find_available_port(5000, 10)
    if not port:
        print("❌ Could not find an available port")
        sys.exit(1)
    
    print(f"✅ Pipeline initialized successfully!")
    print(f"🌐 Starting enhanced web server...")
    print(f"📱 Access your app at: http://localhost:{port}")
    print("=" * 60)
    
    try:
        app.run(
            debug=False,
            host='0.0.0.0',
            port=port,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
