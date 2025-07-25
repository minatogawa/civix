from datetime import datetime

from flask import jsonify, render_template, request
from logger import get_logger, log_request_context
from models import (
    Campaign,
    Contact,
    Demanda,
    Interaction,
    TipoDemanda,
    db,
)
from version import get_version, get_version_info

logger = get_logger(__name__)


def register_routes(app):
    """Register all application routes."""

    @app.before_request
    def log_request_info():
        """Log incoming requests"""
        logger.info(
            "Incoming request",
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get("User-Agent", ""),
        )

    @app.after_request
    def log_response_info(response):
        """Log response information"""
        try:
            log_request_context(
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                response_time=0,  # TODO: Implement proper timing
            )
        except Exception as e:
            logger.warning(f"Failed to log response info: {e}")
        return response

    @app.route("/")
    def index():
        """Home page with basic dashboard"""
        logger.info("Index page accessed")
        try:
            # Estatísticas básicas
            total_demandas = Demanda.query.count()
            demandas_novas = Demanda.query.filter_by(status="nova").count()
            demandas_andamento = Demanda.query.filter_by(status="em_andamento").count()
            demandas_resolvidas = Demanda.query.filter_by(status="resolvida").count()

            # Demandas recentes
            demandas_recentes = (
                Demanda.query.order_by(Demanda.timestamp_captura.desc()).limit(10).all()
            )

            # Estatísticas por tipo
            from sqlalchemy import func

            stats_tipo = (
                db.session.query(
                    TipoDemanda.nome, func.count(Demanda.id_registro).label("total")
                )
                .join(Demanda)
                .group_by(TipoDemanda.nome)
                .all()
            )

            stats = {
                "total_demandas": total_demandas,
                "demandas_novas": demandas_novas,
                "demandas_andamento": demandas_andamento,
                "demandas_resolvidas": demandas_resolvidas,
                "demandas_recentes": demandas_recentes,
                "stats_tipo": stats_tipo,
            }

            logger.info("Dashboard stats loaded", total_demandas=total_demandas)
            return render_template("index.html", stats=stats)

        except Exception as e:
            logger.error("Error loading dashboard", error=str(e), exc_info=True)
            return render_template("index.html", stats=None, error=str(e))

    @app.route("/api/hello")
    def api_hello():
        """API Hello World endpoint"""
        logger.info("API hello endpoint accessed")
        return jsonify(
            {
                "message": "Hello from CiviX API!",
                "timestamp": datetime.now().isoformat(),
                "version": get_version(),
                "status": "running",
            }
        )

    @app.route("/api/stats")
    def api_stats():
        """API endpoint with basic statistics"""
        logger.info("API stats endpoint accessed")
        try:
            total_contacts = Contact.query.count()
            total_interactions = Interaction.query.count()
            total_campaigns = Campaign.query.count()

            logger.info(
                "Database stats retrieved successfully",
                total_contacts=total_contacts,
                total_interactions=total_interactions,
                total_campaigns=total_campaigns,
            )

            return jsonify(
                {
                    "total_contacts": total_contacts,
                    "total_interactions": total_interactions,
                    "total_campaigns": total_campaigns,
                    "database_status": "connected",
                }
            )
        except Exception as e:
            logger.error("Error retrieving database stats", error=str(e), exc_info=True)
            return (
                jsonify(
                    {
                        "total_contacts": 0,
                        "total_interactions": 0,
                        "total_campaigns": 0,
                        "database_status": "error",
                        "error": str(e),
                    }
                ),
                500,
            )

    @app.route("/health")
    def health():
        """Health check endpoint for Docker"""
        logger.info("Health check endpoint accessed")
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": get_version(),
            }
        )

    @app.route("/api/version")
    def api_version():
        """API endpoint with detailed version information"""
        logger.info("API version endpoint accessed")
        return jsonify(get_version_info())

    @app.route("/contacts")
    def contacts():
        """Contacts page"""
        logger.info("Contacts page accessed")
        try:
            contacts_list = Contact.query.all()
            logger.info(f"Retrieved {len(contacts_list)} contacts from database")
            return render_template("contacts.html", contacts=contacts_list)
        except Exception as e:
            logger.error("Error loading contacts page", error=str(e), exc_info=True)
            return render_template("contacts.html", contacts=[], error=str(e))

    @app.route("/demandas")
    def demandas():
        """Demandas page"""
        logger.info("Demandas page accessed")
        try:
            demandas_list = (
                Demanda.query.order_by(Demanda.timestamp_captura.desc()).limit(50).all()
            )
            logger.info(f"Retrieved {len(demandas_list)} demandas from database")
            return render_template("demandas.html", demandas=demandas_list)
        except Exception as e:
            logger.error("Error loading demandas page", error=str(e), exc_info=True)
            return render_template("demandas.html", demandas=[], error=str(e))

    @app.route("/api/demandas")
    def api_demandas():
        """API endpoint for demandas data"""
        logger.info("API demandas endpoint accessed")
        try:
            demandas_list = (
                Demanda.query.order_by(Demanda.timestamp_captura.desc()).limit(20).all()
            )

            demandas_data = []
            for demanda in demandas_list:
                demandas_data.append(
                    {
                        "id": demanda.id_registro,
                        "nome": demanda.nome,
                        "bairro": demanda.bairro_ref.nome
                        if demanda.bairro_ref
                        else None,
                        "tipo": demanda.tipo_demanda_ref.nome
                        if demanda.tipo_demanda_ref
                        else None,
                        "descricao": demanda.descricao_curta,
                        "status": demanda.status,
                        "urgencia": demanda.urgencia,
                        "impacto": demanda.impacto,
                        "prioridade_calculada": demanda.prioridade_calculada,
                        "data_captura": demanda.timestamp_captura.isoformat()
                        if demanda.timestamp_captura
                        else None,
                        "canal_origem": demanda.canal_origem,
                        "confianca": demanda.confianca_global,
                    }
                )

            logger.info(f"API returned {len(demandas_data)} demandas")
            return jsonify({"total": len(demandas_data), "demandas": demandas_data})

        except Exception as e:
            logger.error("Error in API demandas endpoint", error=str(e), exc_info=True)
            return jsonify({"error": str(e), "total": 0, "demandas": []}), 500
