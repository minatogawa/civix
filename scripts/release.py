#!/usr/bin/env python
"""
Script de release automatizado para CiviX.
Gerencia versionamento semântico e criação de tags no Git.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from logger import get_logger
from version import VersionManager

logger = get_logger(__name__)


def main():
    """Função principal do script de release"""
    parser = argparse.ArgumentParser(
        description="CiviX Release Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/release.py patch              # Release patch (0.1.0 -> 0.1.1)
  python scripts/release.py minor              # Release minor (0.1.1 -> 0.2.0)
  python scripts/release.py major              # Release major (0.2.0 -> 1.0.0)
  python scripts/release.py patch --pre alpha  # Pre-release (0.1.0 -> 0.1.1-alpha)
  python scripts/release.py --current          # Show current version
  python scripts/release.py --info             # Show detailed version info
        """,
    )

    # Argumentos principais
    parser.add_argument(
        "bump_type",
        nargs="?",
        choices=["major", "minor", "patch"],
        help="Type of version bump (major, minor, patch)",
    )

    # Opções
    parser.add_argument(
        "--pre",
        "--pre-release",
        dest="pre_release",
        help="Pre-release identifier (alpha, beta, rc.1, etc.)",
    )

    parser.add_argument("--message", "-m", help="Release message for git tag")

    parser.add_argument("--no-tag", action="store_true", help="Don't create git tag")

    parser.add_argument(
        "--current", action="store_true", help="Show current version and exit"
    )

    parser.add_argument(
        "--info", action="store_true", help="Show detailed version information and exit"
    )

    args = parser.parse_args()

    # Inicializar gerenciador de versão
    version_manager = VersionManager()

    # Mostrar versão atual
    if args.current:
        current_version = version_manager.get_current_version()
        print(f"Current version: {current_version}")
        return 0

    # Mostrar informações detalhadas
    if args.info:
        version_info = version_manager.get_version_info()
        print("=== CiviX Version Information ===")
        print(f"Version: {version_info['version']}")
        print(f"Git Branch: {version_info['git']['branch']}")
        print(f"Git Hash: {version_info['git']['hash_short']}")
        print(f"Git Date: {version_info['git']['date']}")
        print(f"Build Date: {version_info['build_date']}")
        print(f"Development: {version_info['is_development']}")
        return 0

    # Validar argumentos para release
    if not args.bump_type:
        parser.error(
            "bump_type is required for release (unless using --current or --info)"
        )

    logger.info(f"Starting release process: {args.bump_type}")

    # Verificar se estamos em um repositório git
    if not Path(".git").exists():
        logger.error("Not in a git repository")
        return 1

    # Processo de release
    try:
        new_version = version_manager.release(
            bump_type=args.bump_type, message=args.message, create_tag=not args.no_tag
        )

        if new_version:
            print(f"✅ Release successful: {new_version}")

            # Mostrar próximos passos
            print("\n📋 Next steps:")
            print("1. Review the changes")
            if not args.no_tag:
                print(f"2. Push the tag: git push origin v{new_version}")
            print("3. Create a release on GitHub/GitLab")
            print("4. Deploy to production")

            return 0
        else:
            print("❌ Release failed")
            return 1

    except Exception as e:
        logger.error(f"Release failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
