from datetime import datetime

from database import db
from sqlalchemy.dialects.postgresql import JSONB


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.BigInteger, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(50), nullable=True)
    first_contact = db.Column(db.DateTime, default=datetime.utcnow)
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with interactions
    interactions = db.relationship("Interaction", backref="contact", lazy=True)

    def __repr__(self):
        return f"<Contact {self.name}>"


class Interaction(db.Model):
    __tablename__ = "interactions"

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    message_type = db.Column(
        db.String(20), default="text"
    )  # text, photo, document, etc.
    telegram_message_id = db.Column(db.BigInteger, nullable=False)

    # Extracted data from LLM processing
    category = db.Column(
        db.String(50), nullable=True
    )  # zeladoria, saúde, educação, etc.
    priority = db.Column(db.String(10), default="medium")  # low, medium, high, urgent
    location = db.Column(db.String(200), nullable=True)
    sentiment = db.Column(db.String(20), nullable=True)  # positive, neutral, negative

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    processed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Interaction {self.id} - {self.category}>"


# Tabelas de Referência
class Bairro(db.Model):
    __tablename__ = "bairros"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    zona = db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamentos
    demandas = db.relationship("Demanda", backref="bairro_ref", lazy=True)

    def __repr__(self):
        return f"<Bairro {self.nome}>"


class TipoDemanda(db.Model):
    __tablename__ = "tipos_demanda"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    categoria = db.Column(db.String(50), nullable=True)
    cor = db.Column(db.String(7), nullable=True)  # Hex color
    descricao = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamentos
    demandas = db.relationship("Demanda", backref="tipo_demanda_ref", lazy=True)

    def __repr__(self):
        return f"<TipoDemanda {self.nome}>"


class Fonte(db.Model):
    __tablename__ = "fontes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.String(200), nullable=True)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamentos
    demandas = db.relationship("Demanda", backref="fonte_ref", lazy=True)

    def __repr__(self):
        return f"<Fonte {self.nome}>"


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True, unique=True)
    telefone = db.Column(db.String(20), nullable=True)
    tipo = db.Column(db.String(20), default="agente")  # agente, responsavel, admin
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    demandas_processadas = db.relationship(
        "Demanda", foreign_keys="Demanda.agente_id", backref="agente", lazy=True
    )
    demandas_responsavel = db.relationship(
        "Demanda",
        foreign_keys="Demanda.responsavel_id",
        backref="responsavel",
        lazy=True,
    )

    def __repr__(self):
        return f"<Usuario {self.nome}>"


# Tabela Principal
class Demanda(db.Model):
    __tablename__ = "demandas"

    # Identificação
    id_registro = db.Column(db.Integer, primary_key=True)
    raw_text_id = db.Column(db.String(50), nullable=True, index=True)

    # Dados de Contato
    data_contato = db.Column(db.Date, nullable=True)
    hora_contato = db.Column(db.Time, nullable=True)
    nome = db.Column(db.String(100), nullable=True)
    telefone = db.Column(db.String(50), nullable=True)

    # Localização
    bairro_id = db.Column(db.Integer, db.ForeignKey("bairros.id"), nullable=True)
    referencia_local = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Demanda
    tipo_demanda_id = db.Column(
        db.Integer, db.ForeignKey("tipos_demanda.id"), nullable=True
    )
    descricao_curta = db.Column(db.Text, nullable=True)
    prioridade_percebida = db.Column(db.String(20), nullable=True)
    urgencia = db.Column(db.Integer, nullable=True)  # 1-5
    impacto = db.Column(db.Integer, nullable=True)  # 1-5

    # Status e Gestão
    status = db.Column(
        db.String(20), default="nova"
    )  # nova, em_andamento, resolvida, cancelada
    responsavel_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    prazo_estimado = db.Column(db.Date, nullable=True)
    data_resolucao = db.Column(db.DateTime, nullable=True)

    # Metadados
    consentimento_comunicacao = db.Column(db.Boolean, default=False)
    fonte_id = db.Column(db.Integer, db.ForeignKey("fontes.id"), nullable=True)
    canal_origem = db.Column(
        db.String(20), nullable=True
    )  # telegram, whatsapp, presencial
    confianca_global = db.Column(db.Float, nullable=True)
    flags = db.Column(JSONB, nullable=True)
    metadata_json = db.Column(JSONB, nullable=True)

    # Controle
    revisado = db.Column(db.Boolean, default=False)
    agente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    # Texto Original
    texto_original = db.Column(db.Text, nullable=True)

    # Timestamps
    timestamp_processamento = db.Column(db.DateTime, nullable=True)
    timestamp_captura = db.Column(db.DateTime, default=datetime.utcnow)

    # Campos extras para futuras expansões
    campo_extra1 = db.Column(db.Text, nullable=True)

    # Relacionamentos
    historico = db.relationship(
        "HistoricoDemanda", backref="demanda", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def prioridade_calculada(self):
        """Calcula prioridade baseada em urgência e impacto"""
        if self.urgencia and self.impacto:
            return self.urgencia * self.impacto
        return 1

    def __repr__(self):
        return f"<Demanda {self.id_registro} - {self.descricao_curta[:50] if self.descricao_curta else 'N/A'}>"


# Tabela de Histórico
class HistoricoDemanda(db.Model):
    __tablename__ = "historico_demandas"

    id = db.Column(db.Integer, primary_key=True)
    demanda_id = db.Column(
        db.Integer, db.ForeignKey("demandas.id_registro"), nullable=False
    )

    # Mudanças
    campo_alterado = db.Column(db.String(50), nullable=False)
    valor_anterior = db.Column(db.Text, nullable=True)
    valor_novo = db.Column(db.Text, nullable=True)

    # Metadados
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<HistoricoDemanda {self.demanda_id} - {self.campo_alterado}>"


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="active")  # active, paused, completed

    # Analytics
    total_contacts = db.Column(db.Integer, default=0)
    total_interactions = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Campaign {self.name}>"
