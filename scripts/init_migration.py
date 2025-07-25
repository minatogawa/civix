#!/usr/bin/env python
"""
Script para gerar a migração inicial sem necessidade de PostgreSQL rodando.
Este script cria os arquivos de migração que podem ser executados depois.
"""

import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def create_initial_migration():
    """Create initial migration file manually"""

    migration_content = '''"""Initial migration: contacts, interactions, campaigns

Revision ID: 001_initial
Revises:
Create Date: {create_date}

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create contacts table
    op.create_table('contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('first_contact', sa.DateTime(), nullable=True),
        sa.Column('last_interaction', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_user_id')
    )

    # Create interactions table
    op.create_table('interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=True),
        sa.Column('telegram_message_id', sa.BigInteger(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=10), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create campaigns table
    op.create_table('campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('total_contacts', sa.Integer(), nullable=True),
        sa.Column('total_interactions', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('campaigns')
    op.drop_table('interactions')
    op.drop_table('contacts')
'''.format(create_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

    # Create versions directory if it doesn't exist
    versions_dir = os.path.join("migrations", "versions")
    os.makedirs(versions_dir, exist_ok=True)

    # Write migration file
    migration_file = os.path.join(versions_dir, "001_initial_migration.py")
    with open(migration_file, "w") as f:
        f.write(migration_content)

    print(f"Created initial migration: {migration_file}")
    print("Run 'python -m flask db upgrade' when PostgreSQL is running")


if __name__ == "__main__":
    create_initial_migration()
