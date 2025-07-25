from datetime import datetime

from flask import jsonify, render_template, request
from logger import get_logger, log_request_context
from models import Campaign, Contact, Interaction
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
        log_request_context(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            response_time=0,  # TODO: Implement proper timing
        )
        return response

    @app.route("/")
    def index():
        """Home page with basic dashboard"""
        logger.info("Index page accessed")
        return render_template("index.html")

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
