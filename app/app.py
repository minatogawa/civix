from flask import render_template, jsonify, request
from database import create_app, db
from models import Contact, Interaction, Campaign
from datetime import datetime

app = create_app()

# Import models to make them available to Flask-Migrate
with app.app_context():
    # This ensures models are registered with SQLAlchemy
    pass

@app.route('/')
def index():
    """Home page with basic dashboard"""
    return render_template('index.html')

@app.route('/api/hello')
def api_hello():
    """API Hello World endpoint"""
    return jsonify({
        'message': 'Hello from CiviX API!',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint with basic statistics"""
    try:
        with app.app_context():
            total_contacts = Contact.query.count()
            total_interactions = Interaction.query.count()
            total_campaigns = Campaign.query.count()
            
            return jsonify({
                'total_contacts': total_contacts,
                'total_interactions': total_interactions,
                'total_campaigns': total_campaigns,
                'database_status': 'connected'
            })
    except Exception as e:
        return jsonify({
            'total_contacts': 0,
            'total_interactions': 0,
            'total_campaigns': 0,
            'database_status': 'error',
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint for Docker"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/contacts')
def contacts():
    """Contacts page"""
    try:
        contacts_list = Contact.query.all()
        return render_template('contacts.html', contacts=contacts_list)
    except Exception as e:
        return render_template('contacts.html', contacts=[], error=str(e))

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist (for development)
        try:
            db.create_all()
        except Exception as e:
            print(f"Database error: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)