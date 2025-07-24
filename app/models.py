from datetime import datetime
from database import db


class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.BigInteger, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(50), nullable=True)
    first_contact = db.Column(db.DateTime, default=datetime.utcnow)
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with interactions
    interactions = db.relationship('Interaction', backref='contact', lazy=True)
    
    def __repr__(self):
        return f'<Contact {self.name}>'


class Interaction(db.Model):
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, photo, document, etc.
    telegram_message_id = db.Column(db.BigInteger, nullable=False)
    
    # Extracted data from LLM processing
    category = db.Column(db.String(50), nullable=True)  # zeladoria, saúde, educação, etc.
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, urgent
    location = db.Column(db.String(200), nullable=True)
    sentiment = db.Column(db.String(20), nullable=True)  # positive, neutral, negative
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Interaction {self.id} - {self.category}>'


class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    
    # Analytics
    total_contacts = db.Column(db.Integer, default=0)
    total_interactions = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Campaign {self.name}>'