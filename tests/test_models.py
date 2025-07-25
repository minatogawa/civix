import os
import sys
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from app.database import db
from app.models import Campaign, Contact, Interaction


def test_contact_creation(app):
    """Test creating a contact."""
    with app.app_context():
        contact = Contact(
            telegram_user_id=123456789,
            name="John Doe",
            phone="1234567890",
            username="johndoe",
        )
        db.session.add(contact)
        db.session.commit()

        # Test the contact was created
        saved_contact = Contact.query.filter_by(telegram_user_id=123456789).first()
        assert saved_contact is not None
        assert saved_contact.name == "John Doe"
        assert saved_contact.phone == "1234567890"
        assert saved_contact.username == "johndoe"
        assert saved_contact.first_contact is not None


def test_contact_repr(app):
    """Test contact string representation."""
    with app.app_context():
        contact = Contact(
            telegram_user_id=987654321, name="Jane Doe", username="janedoe"
        )
        db.session.add(contact)
        db.session.commit()

        assert "<Contact Jane Doe>" in str(contact)


def test_campaign_creation(app):
    """Test creating a campaign."""
    with app.app_context():
        from datetime import datetime

        campaign = Campaign(
            name="Test Campaign",
            description="This is a test campaign",
            start_date=datetime.utcnow(),
            status="active",
        )
        db.session.add(campaign)
        db.session.commit()

        saved_campaign = Campaign.query.filter_by(name="Test Campaign").first()
        assert saved_campaign is not None
        assert saved_campaign.name == "Test Campaign"
        assert saved_campaign.description == "This is a test campaign"
        assert saved_campaign.status == "active"
        assert saved_campaign.created_at is not None


def test_interaction_creation(app):
    """Test creating an interaction."""
    with app.app_context():
        from datetime import datetime

        # Create contact first
        contact = Contact(
            telegram_user_id=555666777, name="Test User", username="testuser"
        )
        db.session.add(contact)
        db.session.commit()

        # Create interaction
        interaction = Interaction(
            contact_id=contact.id,
            message_text="Test message content",
            telegram_message_id=12345,
            category="test",
            priority="medium",
        )
        db.session.add(interaction)
        db.session.commit()

        saved_interaction = Interaction.query.filter_by(category="test").first()
        assert saved_interaction is not None
        assert saved_interaction.contact_id == contact.id
        assert saved_interaction.message_text == "Test message content"
        assert saved_interaction.telegram_message_id == 12345
        assert saved_interaction.category == "test"
        assert saved_interaction.created_at is not None


def test_contact_interactions_relationship(app):
    """Test the relationship between contacts and interactions."""
    with app.app_context():
        contact = Contact(
            telegram_user_id=111222333, name="Relationship Test", username="reltest"
        )
        db.session.add(contact)
        db.session.commit()

        # Create multiple interactions for the same contact
        interaction1 = Interaction(
            contact_id=contact.id,
            message_text="First interaction",
            telegram_message_id=11111,
            category="test1",
        )
        interaction2 = Interaction(
            contact_id=contact.id,
            message_text="Second interaction",
            telegram_message_id=22222,
            category="test2",
        )
        db.session.add(interaction1)
        db.session.add(interaction2)
        db.session.commit()

        # Test the relationship
        saved_contact = Contact.query.filter_by(telegram_user_id=111222333).first()
        assert len(saved_contact.interactions) == 2
        assert any(i.category == "test1" for i in saved_contact.interactions)
        assert any(i.category == "test2" for i in saved_contact.interactions)


def test_campaign_basic_fields(app):
    """Test campaign basic functionality."""
    with app.app_context():
        from datetime import datetime

        campaign = Campaign(
            name="Campaign Test",
            description="Test campaign",
            start_date=datetime.utcnow(),
            status="active",
        )
        db.session.add(campaign)
        db.session.commit()

        # Test the campaign
        saved_campaign = Campaign.query.filter_by(name="Campaign Test").first()
        assert saved_campaign is not None
        assert saved_campaign.description == "Test campaign"
        assert saved_campaign.status == "active"
        assert "<Campaign Campaign Test>" in str(saved_campaign)
