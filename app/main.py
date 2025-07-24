from flask import render_template, jsonify
from database import db
from models import Contact, Interaction, Campaign
from datetime import datetime


def register_routes(app):
    """Register all application routes."""
    
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