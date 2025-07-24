#!/usr/bin/env python
"""
Script para popular o banco de dados com dados iniciais de desenvolvimento.
"""

import os
import sys
from datetime import datetime, timedelta
from faker import Faker

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import create_app, db
from app.models import Contact, Interaction, Campaign

fake = Faker('pt_BR')  # Brazilian Portuguese locale

def create_sample_contacts(num_contacts=20):
    """Create sample contacts"""
    contacts = []
    
    for i in range(num_contacts):
        contact = Contact(
            telegram_user_id=fake.random_int(min=100000000, max=999999999),
            name=fake.name(),
            phone=fake.phone_number(),
            username=fake.user_name() if fake.boolean(chance_of_getting_true=70) else None,
            first_contact=fake.date_time_between(start_date='-6M', end_date='now'),
            last_interaction=fake.date_time_between(start_date='-1M', end_date='now')
        )
        contacts.append(contact)
    
    return contacts

def create_sample_interactions(contacts, num_interactions=50):
    """Create sample interactions for contacts"""
    interactions = []
    
    # Sample messages for different categories
    messages_by_category = {
        'zeladoria': [
            'Tem um buraco na rua da minha casa, muito perigoso para carros',
            'A lâmpada do poste está queimada há semanas',
            'Precisa cortar o mato da praça, está muito alto',
            'Tem lixo acumulado na esquina da Rua das Flores',
            'O semáforo está piscando amarelo desde ontem'
        ],
        'saude': [
            'Posto de saúde está sem médico há 3 dias',
            'Falta remédio para hipertensão na farmácia básica',
            'Demora muito para conseguir consulta especializada',
            'Ambulância não veio quando chamamos ontem'
        ],
        'educacao': [
            'Escola do meu filho está sem professor de matemática',
            'Merenda escolar está com qualidade ruim',
            'Falta material escolar para as crianças',
            'Quadra da escola precisa de reforma urgente'
        ],
        'transporte': [
            'Ônibus está passando com atraso todos os dias',
            'Parada de ônibus não tem cobertura',
            'Falta sinalização na rua principal',
            'Ciclovia está em péssimo estado'
        ],
        'seguranca': [
            'Muitos assaltos acontecendo no bairro',
            'Falta iluminação na praça, muito perigoso à noite',
            'Precisa de mais policiamento na região',
            'Tem gente usando drogas na pracinha'
        ]
    }
    
    categories = list(messages_by_category.keys())
    priorities = ['low', 'medium', 'high', 'urgent']
    sentiments = ['positive', 'neutral', 'negative']
    
    for i in range(num_interactions):
        category = fake.random_element(categories)
        message = fake.random_element(messages_by_category[category])
        
        interaction = Interaction(
            contact_id=fake.random_element(contacts).id,
            message_text=message,
            message_type='text',
            telegram_message_id=fake.random_int(min=1000, max=9999),
            category=category,
            priority=fake.random_element(priorities),
            location=f"{fake.street_name()}, {fake.city()}",
            sentiment=fake.random_element(sentiments),
            created_at=fake.date_time_between(start_date='-3M', end_date='now'),
            processed=fake.boolean(chance_of_getting_true=80),
            processed_at=fake.date_time_between(start_date='-3M', end_date='now') if fake.boolean(chance_of_getting_true=80) else None
        )
        interactions.append(interaction)
    
    return interactions

def create_sample_campaigns():
    """Create sample campaigns"""
    campaigns = [
        Campaign(
            name="Campanha Zeladoria 2024",
            description="Foco em melhorias de infraestrutura urbana e limpeza pública",
            start_date=datetime.now() - timedelta(days=90),
            end_date=datetime.now() + timedelta(days=30),
            status="active",
            total_contacts=15,
            total_interactions=32
        ),
        Campaign(
            name="Saúde para Todos",
            description="Atendimento das demandas de saúde pública do município",
            start_date=datetime.now() - timedelta(days=60),
            end_date=None,
            status="active",
            total_contacts=8,
            total_interactions=18
        ),
        Campaign(
            name="Educação de Qualidade",
            description="Melhorias na rede municipal de ensino",
            start_date=datetime.now() - timedelta(days=120),
            end_date=datetime.now() - timedelta(days=30),
            status="completed",
            total_contacts=12,
            total_interactions=25
        )
    ]
    
    return campaigns

def seed_database():
    """Main function to seed the database"""
    app = create_app()
    
    with app.app_context():
        print("Limpando dados existentes...")
        
        # Clear existing data
        Interaction.query.delete()
        Contact.query.delete()
        Campaign.query.delete()
        db.session.commit()
        
        print("Criando contatos de exemplo...")
        contacts = create_sample_contacts(20)
        db.session.add_all(contacts)
        db.session.commit()
        
        print("Criando interações de exemplo...")
        interactions = create_sample_interactions(contacts, 50)
        db.session.add_all(interactions)
        db.session.commit()
        
        print("Criando campanhas de exemplo...")
        campaigns = create_sample_campaigns()
        db.session.add_all(campaigns)
        db.session.commit()
        
        print(f"Seed concluído!")
        print(f"- {len(contacts)} contatos criados")
        print(f"- {len(interactions)} interações criadas")
        print(f"- {len(campaigns)} campanhas criadas")

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"Erro durante o seed: {e}")
        print("Certifique-se de que o PostgreSQL está rodando e as migrações foram aplicadas.")
        print("Execute: docker-compose up -d postgres && python -m flask db upgrade")