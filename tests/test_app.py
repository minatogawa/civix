import pytest
import json
from app.models import Contact, Interaction, Campaign


def test_index_page(client):
    """Test the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'CiviX' in response.data


def test_api_hello(client):
    """Test the API hello endpoint."""
    response = client.get('/api/hello')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['message'] == 'Hello from CiviX API!'
    assert data['version'] == '1.0.0'
    assert data['status'] == 'running'
    assert 'timestamp' in data


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data


def test_api_stats_empty_database(client):
    """Test stats endpoint with empty database."""
    response = client.get('/api/stats')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['total_contacts'] == 0
    assert data['total_interactions'] == 0
    assert data['total_campaigns'] == 0
    assert data['database_status'] == 'connected'


def test_contacts_page_empty(client):
    """Test contacts page with no contacts."""
    response = client.get('/contacts')
    assert response.status_code == 200
    assert b'contacts' in response.data.lower()


def test_api_stats_with_data(client, app):
    """Test stats endpoint with test data."""
    with app.app_context():
        from app.database import db
        from datetime import datetime
        
        # Create test contact
        contact = Contact(
            telegram_user_id=999888777,
            name='Test User',
            phone='1234567890',
            username='testuser'
        )
        db.session.add(contact)
        db.session.commit()
        
        # Create test campaign
        campaign = Campaign(
            name='Test Campaign',
            description='Test Description',
            start_date=datetime.utcnow(),
            status='active'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # Create test interaction
        interaction = Interaction(
            contact_id=contact.id,
            message_text='Test interaction',
            telegram_message_id=98765,
            category='test'
        )
        db.session.add(interaction)
        db.session.commit()
    
    response = client.get('/api/stats')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['total_contacts'] == 1
    assert data['total_interactions'] == 1
    assert data['total_campaigns'] == 1
    assert data['database_status'] == 'connected'