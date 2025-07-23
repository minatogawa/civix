# Template Repository

Este é um template repository para projetos de desenvolvimento.

## 📁 Estrutura do Projeto

```
├── src/           # Código fonte
├── tests/         # Testes
├── docs/          # Documentação
├── .github/       # Configurações do GitHub
│   ├── workflows/ # GitHub Actions
│   └── ISSUE_TEMPLATE/ # Templates de issues
├── .gitignore     # Arquivos ignorados pelo Git
└── README.md      # Este arquivo
```

## 🚀 Como Usar Este Template

1. Clique em "Use this template" no GitHub
2. Clone o repositório criado
3. Instale as dependências necessárias
4. Comece a desenvolver!

## 🔧 Configuração do Pre-commit

Este template inclui configuração completa do pre-commit para Python/Flask e frontend.

### Instalação

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar os hooks
pre-commit install
```

### Hooks Incluídos

#### 🔧 **Hooks Gerais (pre-commit-hooks)**
- **trailing-whitespace**: Remove espaços em branco no final das linhas
- **end-of-file-fixer**: Garante que arquivos terminem com uma nova linha
- **check-yaml**: Valida sintaxe de arquivos YAML
- **check-json**: Valida sintaxe de arquivos JSON
- **check-toml**: Valida sintaxe de arquivos TOML
- **check-xml**: Valida sintaxe de arquivos XML
- **check-merge-conflict**: Detecta marcadores de conflito de merge não resolvidos
- **check-case-conflict**: Detecta conflitos de case-sensitivity em nomes de arquivos
- **check-docstring-first**: Verifica se docstrings estão no início das funções
- **check-executables-have-shebangs**: Verifica se arquivos executáveis têm shebang
- **check-added-large-files**: Previne commits de arquivos muito grandes (>500KB)
- **debug-statements**: Detecta declarações de debug (pdb, ipdb, etc.)

#### 🐍 **Python/Flask**
- **Black**: Formatação automática de código Python seguindo padrões PEP 8 (linha de 88 caracteres)
- **isort**: Organiza imports automaticamente, compatível com Black
- **flake8**: Linting e verificação de estilo de código Python (ignora E203, W503)
- **bandit**: Análise estática de segurança, detecta vulnerabilidades comuns
- **mypy**: Verificação de tipos estáticos com suporte a types-all
- **python-safety-dependencies-check**: Verifica vulnerabilidades conhecidas em dependências

#### 🎨 **Frontend**
- **prettier**: Formatação automática de CSS, SCSS, JavaScript, TypeScript, JSON, HTML, YAML, Markdown
- **eslint**: Linting JavaScript/TypeScript com configuração compatível com Prettier

#### 📝 **Commits**
- **commitizen**: Enforce conventional commits (feat:, fix:, docs:, etc.)

## 📋 Próximos Passos

- [ ] Configurar requirements.txt para Python
- [ ] Adicionar workflows do GitHub Actions
- [ ] Configurar package.json (se usar frontend JS)
- [ ] Adicionar templates de issues e pull requests
- [ ] Personalizar este README com informações do seu projeto

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.