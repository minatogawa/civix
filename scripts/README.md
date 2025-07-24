# Scripts de Banco de Dados

## Scripts Disponíveis

### `init_migration.py`
Cria a migração inicial do banco de dados sem necessidade do PostgreSQL estar rodando.

```bash
python scripts/init_migration.py
```

### `seed.py`
Popula o banco com dados de exemplo para desenvolvimento.

```bash
python scripts/seed.py
# ou
make seed
```

## Ordem de Execução

1. **Configurar ambiente**:
   ```bash
   make setup
   # Editar .env com suas configurações
   ```

2. **Iniciar PostgreSQL**:
   ```bash
   docker-compose up -d postgres
   ```

3. **Aplicar migrações**:
   ```bash
   make migrate
   ```

4. **Popular com dados de exemplo**:
   ```bash
   make seed
   ```

## Dados de Exemplo

O script de seed cria:

- **20 contatos** com nomes brasileiros
- **50 interações** categorizadas:
  - Zeladoria (buracos, limpeza, iluminação)
  - Saúde (postos, medicamentos, consultas)
  - Educação (escolas, professores, merenda)
  - Transporte (ônibus, sinalização, ciclovias)
  - Segurança (policiamento, iluminação)
- **3 campanhas** de exemplo (ativa, completada, em andamento)

Todos os dados usam nomes, endereços e telefones brasileiros realistas.