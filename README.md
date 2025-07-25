# CiviX - Community Management System

CiviX é um sistema de gestão comunitária desenvolvido em Flask, projetado para facilitar a comunicação entre cidadãos e gestores públicos através de bots do Telegram e interface web.

## 🚀 Funcionalidades

- **Interface Web** - Dashboard para visualização de contatos e estatísticas
- **Bot Telegram** - Integração para recebimento de mensagens da comunidade
- **Banco de Dados** - Armazenamento de contatos, interações e campanhas
- **API REST** - Endpoints para integração e consulta de dados
- **Sistema de Logs** - Logging estruturado com Loguru
- **Versionamento** - Semantic versioning com tags Git
- **Testes Automatizados** - Cobertura completa com pytest
- **CI/CD** - Pipeline automatizado com GitHub Actions

## 📋 Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Git
- Make (opcional, para comandos simplificados)

## 🛠️ Como rodar localmente

### Opção 1: Com Docker (Recomendado)

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd civix
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

3. **Inicie os serviços:**
   ```bash
   # Usando Make
   make up

   # Ou diretamente com Docker Compose
   docker-compose up -d
   ```

4. **Execute as migrações do banco:**
   ```bash
   make migrate
   # Ou: docker-compose exec web flask db upgrade
   ```

5. **Popule o banco com dados de exemplo (opcional):**
   ```bash
   make seed
   # Ou: docker-compose exec web python scripts/seed.py
   ```

6. **Acesse a aplicação:**
   - Web: http://localhost:5000
   - API: http://localhost:5000/api/hello
   - Health check: http://localhost:5000/health
   - Bot health: http://localhost:8080/health

### Opção 2: Ambiente de desenvolvimento local

1. **Configure o ambiente Python:**
   ```bash
   # Setup completo (recomendado)
   make setup-dev

   # Ou passo a passo:
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Configure DATABASE_URL para PostgreSQL ou use SQLite para desenvolvimento
   ```

3. **Inicie apenas o PostgreSQL (se necessário):**
   ```bash
   docker-compose up -d postgres
   ```

4. **Execute as migrações:**
   ```bash
   make migrate
   # Ou: flask db upgrade
   ```

5. **Inicie os serviços localmente:**
   ```bash
   # Terminal 1 - Web App
   python app/app.py

   # Terminal 2 - Bot (opcional)
   python app/bot.py
   ```

## 🧪 Como rodar testes

### Testes básicos

```bash
# Usando Make
make test

# Ou diretamente
pytest tests/ -v
```

### Testes com cobertura

```bash
# Relatório de cobertura
make test-coverage

# Visualizar relatório HTML
open htmlcov/index.html
```

### Testes específicos

```bash
# Testar apenas um arquivo
pytest tests/test_app.py -v

# Testar uma função específica
pytest tests/test_app.py::test_api_hello -v

# Executar testes com diferentes configurações
FLASK_ENV=testing pytest tests/ -v
```

### Qualidade de código

```bash
# Linting completo
make lint-all

# Formatação de código
make format

# Verificar formatação
make format-check

# Executar pre-commit hooks
make run-hooks
```

## 🚀 Como fazer deploy

### Deploy com Docker (Produção)

1. **Prepare o ambiente de produção:**
   ```bash
   # Clone no servidor
   git clone <url-do-repositorio>
   cd civix

   # Configure variáveis de produção
   cp .env.example .env
   # Edite .env com configurações de produção
   ```

2. **Configure as variáveis de ambiente de produção:**
   ```bash
   # .env para produção
   FLASK_ENV=production
   LOG_LEVEL=INFO
   LOG_FORMAT=production
   DATABASE_URL=postgresql://user:password@db:5432/civix_prod
   SECRET_KEY=sua-chave-secreta-super-segura
   ```

3. **Execute o deploy:**
   ```bash
   # Build e start
   make build
   make up

   # Execute migrações
   make migrate

   # Verificar status
   make logs
   ```

### Deploy com GitHub Actions

1. **Configure os secrets no GitHub:**
   - `DOCKER_USERNAME` - Usuário do Docker Hub
   - `DOCKER_PASSWORD` - Senha do Docker Hub
   - Outros secrets necessários

2. **Crie um release:**
   ```bash
   # Localmente
   make release-patch  # ou release-minor, release-major
   git push origin main --tags

   # Ou via GitHub Actions (manual)
   # Acesse Actions > Release > Run workflow
   ```

3. **Deploy automatizado:**
   - O pipeline criará imagens Docker
   - Tags serão criadas automaticamente
   - Release será publicado no GitHub

### Deploy manual (VPS/Servidor)

1. **Instale dependências no servidor:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose git make

   # Inicie Docker
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **Configure o projeto:**
   ```bash
   git clone <url-do-repositorio>
   cd civix

   # Configure .env para produção
   cp .env.example .env
   nano .env
   ```

3. **Execute deployment:**
   ```bash
   sudo make deploy
   # Ou: sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

4. **Configure reverse proxy (Nginx exemplo):**
   ```nginx
   server {
       listen 80;
       server_name seu-dominio.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 📊 Monitoramento

### Logs

```bash
# Ver logs em tempo real
make logs

# Logs específicos do serviço
docker-compose logs -f web
docker-compose logs -f bot
docker-compose logs -f postgres

# Logs locais (arquivos)
tail -f logs/civix.log
tail -f logs/errors.log
```

### Health Checks

```bash
# Web app
curl http://localhost:5000/health

# Bot service
curl http://localhost:8080/health

# API com informações detalhadas
curl http://localhost:5000/api/version
```

### Backup do banco de dados

```bash
# Criar backup
make backup

# Listar backups
python scripts/backup.py list

# Restaurar backup
make restore-file BACKUP=backup_20241201_120000.sql
```

## 🔧 Comandos úteis

### Makefile

```bash
make help              # Ver todos os comandos disponíveis
make setup            # Setup inicial do projeto
make setup-dev        # Setup completo para desenvolvimento
make version          # Ver versão atual
make version-info     # Informações detalhadas da versão
make clean            # Limpar containers e volumes
```

### Desenvolvimento

```bash
# Instalar hooks de pre-commit
make install-hooks

# Executar todos os hooks
make run-hooks

# Atualizar dependências dos hooks
make update-hooks

# Corrigir problemas de código
make fix
```

### Database

```bash
make migrate          # Aplicar migrações
make seed            # Popular com dados de exemplo
make backup          # Backup do banco
```

## 🏗️ Estrutura do projeto

```
civix/
├── app/                    # Código da aplicação
│   ├── __init__.py
│   ├── app.py             # Aplicação Flask principal
│   ├── bot.py             # Bot do Telegram
│   ├── database.py        # Configuração do banco
│   ├── models.py          # Modelos SQLAlchemy
│   ├── main.py            # Rotas principais
│   ├── logger.py          # Sistema de logging
│   ├── logger_config.py   # Configuração de logs
│   └── version.py         # Sistema de versionamento
├── tests/                 # Testes automatizados
├── scripts/               # Scripts utilitários
├── migrations/            # Migrações do banco
├── logs/                  # Arquivos de log
├── .github/workflows/     # CI/CD pipelines
├── docker-compose.yml     # Configuração Docker
├── Dockerfile            # Imagem Docker
├── requirements.txt      # Dependências Python
├── Makefile             # Comandos automatizados
└── README.md            # Este arquivo
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Guidelines

- Siga os padrões de código (black, flake8, ruff)
- Escreva testes para novas funcionalidades
- Execute `make run-hooks` antes de fazer commit
- Mantenha o CHANGELOG.md atualizado

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Issues**: Abra uma issue no GitHub
- **Documentação**: Consulte a wiki do projeto
- **Email**: contato@civix.com.br

## 🔖 Versões

Este projeto segue [Semantic Versioning](https://semver.org/). Para as versões disponíveis, veja as [tags neste repositório](../../tags).

### Versão atual

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)

Para ver informações detalhadas da versão atual:
```bash
make version-info
```
