#!/usr/bin/env python
"""
Script para backup e restore do banco PostgreSQL
"""

import os
import subprocess
import datetime
from dotenv import load_dotenv

load_dotenv()

def get_db_config():
    """Get database configuration from environment"""
    return {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'user': os.getenv('POSTGRES_USER', 'civix_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'civix_password'),
        'database': os.getenv('POSTGRES_DB', 'civix_db')
    }

def create_backup():
    """Create database backup"""
    config = get_db_config()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = 'data/postgres'
    backup_file = f"{backup_dir}/backup_{timestamp}.sql"
    
    # Ensure backup directory exists
    os.makedirs(backup_dir, exist_ok=True)
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = config['password']
    
    # Create backup command
    cmd = [
        'docker', 'exec', 'civix-postgres-1',
        'pg_dump',
        '-h', config['host'],
        '-p', config['port'],
        '-U', config['user'],
        '-d', config['database'],
        '--clean',
        '--create'
    ]
    
    try:
        with open(backup_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env, text=True)
        
        if result.returncode == 0:
            print(f"Backup criado com sucesso: {backup_file}")
            return backup_file
        else:
            print(f"Erro no backup: {result.stderr}")
            return None
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
        return None

def restore_backup(backup_file):
    """Restore database from backup"""
    if not os.path.exists(backup_file):
        print(f"Arquivo de backup não encontrado: {backup_file}")
        return False
    
    config = get_db_config()
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = config['password']
    
    # Restore command
    cmd = [
        'docker', 'exec', '-i', 'civix-postgres-1',
        'psql',
        '-h', config['host'],
        '-p', config['port'],
        '-U', config['user'],
        '-d', 'postgres'  # Connect to postgres db first
    ]
    
    try:
        with open(backup_file, 'r') as f:
            result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, env=env, text=True)
        
        if result.returncode == 0:
            print(f"Restore concluído com sucesso de: {backup_file}")
            return True
        else:
            print(f"Erro no restore: {result.stderr}")
            return False
    except Exception as e:
        print(f"Erro ao restaurar backup: {e}")
        return False

def list_backups():
    """List available backups"""
    backup_dir = 'data/postgres'
    if not os.path.exists(backup_dir):
        print("Nenhum backup encontrado")
        return []
    
    backups = [f for f in os.listdir(backup_dir) if f.startswith('backup_') and f.endswith('.sql')]
    backups.sort(reverse=True)  # Most recent first
    
    if backups:
        print("Backups disponíveis:")
        for i, backup in enumerate(backups, 1):
            backup_path = os.path.join(backup_dir, backup)
            size = os.path.getsize(backup_path) / 1024  # KB
            print(f"  {i}. {backup} ({size:.1f} KB)")
    else:
        print("Nenhum backup encontrado")
    
    return backups

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python scripts/backup.py create          - Criar backup")
        print("  python scripts/backup.py list            - Listar backups")
        print("  python scripts/backup.py restore <file>  - Restaurar backup")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create':
        create_backup()
    elif command == 'list':
        list_backups()
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("Especifique o arquivo de backup para restaurar")
            sys.exit(1)
        restore_backup(sys.argv[2])
    else:
        print(f"Comando desconhecido: {command}")
        sys.exit(1)