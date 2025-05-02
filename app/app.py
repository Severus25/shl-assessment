from flask import Flask, request, jsonify, render_template
import os
from .engine import get_recommendations # Use relative import within the package

# Detect if running on PythonAnywhere
PYTHONANYWHERE_USERNAME = os.environ.get('PYTHONANYWHERE_USERNAME')
if PYTHONANYWHERE_USERNAME:
    # Adjust path for PythonAnywhere deployment
    project_home = f'/home/{PYTHONANYWHERE_USERNAME}/shl-recommendation-engine/'
    # Ensure engine uses the correct data path if deployed
    from . import engine
    engine.DATA_FILE = os.path.join(project_home, 'data', 'shl_products.json')
    print(f"Running on PythonAnywhere. Data file set to: {engine.DATA_FILE}")


app = Flask(__name__)

@app.route('/')
def index():
    """Serves the main HTML page."""
    # Pass potential competency list to the template for dynamic population
    # For now, we'll hardcode a few common ones in the HTML,
    # but ideally, you'd extract all unique competencies from the data.
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    """API endpoint to get recommendations."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        job_title = data.get('job_title', '')
        job_level = data.get('job_level')
        competencies = data.get('competencies', [])

        if not job_level or not competencies:
            return jsonify({"error": "Missing required fields: job_level and competencies"}), 400

        if not isinstance(competencies, list):
             return jsonify({"error": "'competencies' must be a list of strings"}), 400

        recommendations = get_recommendations(job_title, job_level, competencies)
        return jsonify(recommendations)

    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Error during recommendation: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

# Add basic logging
if __name__ != '__main__': # Only configure logging if not running directly
    import logging
    # You might want more sophisticated logging in production
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


# For local development:
# if __name__ == '__main__':
#    app.run(debug=True)
# Running via Flask CLI (`flask run`) is generally preferred for development.