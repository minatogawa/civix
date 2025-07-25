"""
Utilitário para configurar logging levels dinamicamente via .env
Permite alterar níveis de log sem reiniciar a aplicação.
"""

import os

from loguru import logger


class LoggerConfig:
    """Gerenciador de configuração dinâmica do logger"""

    VALID_LEVELS = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]

    @classmethod
    def get_current_config(cls) -> dict[str, str]:
        """Retorna a configuração atual do logger"""
        return {
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "LOG_FORMAT": os.getenv("LOG_FORMAT", "development"),
            "LOG_REQUESTS": os.getenv("LOG_REQUESTS", "true"),
            "LOG_DATABASE": os.getenv("LOG_DATABASE", "true"),
            "LOG_TELEGRAM": os.getenv("LOG_TELEGRAM", "true"),
            "LOG_RETENTION_DAYS": os.getenv("LOG_RETENTION_DAYS", "30"),
            "LOG_ERROR_RETENTION_DAYS": os.getenv("LOG_ERROR_RETENTION_DAYS", "90"),
        }

    @classmethod
    def validate_level(cls, level: str) -> bool:
        """Valida se o nível de log é válido"""
        return level.upper() in cls.VALID_LEVELS

    @classmethod
    def set_level(cls, level: str) -> bool:
        """
        Define o nível de log dinamicamente

        Args:
            level: Nível de log (TRACE, DEBUG, INFO, etc.)

        Returns:
            True se alterado com sucesso, False caso contrário
        """
        if not cls.validate_level(level):
            logger.error(
                f"Invalid log level: {level}. Valid levels: {cls.VALID_LEVELS}"
            )
            return False

        os.environ["LOG_LEVEL"] = level.upper()
        logger.info(f"Log level changed to: {level.upper()}")
        return True

    @classmethod
    def enable_category(cls, category: str) -> bool:
        """
        Habilita uma categoria de log

        Args:
            category: requests, database, telegram

        Returns:
            True se alterado com sucesso, False caso contrário
        """
        env_var = f"LOG_{category.upper()}"
        if env_var not in ["LOG_REQUESTS", "LOG_DATABASE", "LOG_TELEGRAM"]:
            logger.error(f"Invalid log category: {category}")
            return False

        os.environ[env_var] = "true"
        logger.info(f"Log category {category} enabled")
        return True

    @classmethod
    def disable_category(cls, category: str) -> bool:
        """
        Desabilita uma categoria de log

        Args:
            category: requests, database, telegram

        Returns:
            True se alterado com sucesso, False caso contrário
        """
        env_var = f"LOG_{category.upper()}"
        if env_var not in ["LOG_REQUESTS", "LOG_DATABASE", "LOG_TELEGRAM"]:
            logger.error(f"Invalid log category: {category}")
            return False

        os.environ[env_var] = "false"
        logger.info(f"Log category {category} disabled")
        return True

    @classmethod
    def get_enabled_categories(cls) -> list[str]:
        """Retorna lista de categorias habilitadas"""
        categories = []
        if os.getenv("LOG_REQUESTS", "true").lower() == "true":
            categories.append("requests")
        if os.getenv("LOG_DATABASE", "true").lower() == "true":
            categories.append("database")
        if os.getenv("LOG_TELEGRAM", "true").lower() == "true":
            categories.append("telegram")
        return categories

    @classmethod
    def print_config(cls) -> None:
        """Imprime a configuração atual do logger"""
        config = cls.get_current_config()
        enabled_categories = cls.get_enabled_categories()

        logger.info("=== LOGGER CONFIGURATION ===")
        logger.info(f"Log Level: {config['LOG_LEVEL']}")
        logger.info(f"Log Format: {config['LOG_FORMAT']}")
        logger.info(f"Enabled Categories: {', '.join(enabled_categories)}")
        logger.info(f"Log Retention: {config['LOG_RETENTION_DAYS']} days")
        logger.info(f"Error Retention: {config['LOG_ERROR_RETENTION_DAYS']} days")
        logger.info("============================")


def configure_from_env():
    """Configura o logger baseado nas variáveis de ambiente atuais"""
    from logger import setup_logger

    setup_logger()


if __name__ == "__main__":
    # Exemplo de uso
    config = LoggerConfig()
    config.print_config()

    # Alterar nível para DEBUG
    config.set_level("DEBUG")

    # Desabilitar logs de requests
    config.disable_category("requests")

    # Mostrar configuração atualizada
    config.print_config()
