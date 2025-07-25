"""
Sistema de versionamento para CiviX seguindo Semantic Versioning (semver).
Gerencia versões automaticamente com integração ao Git.
"""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from logger import get_logger

logger = get_logger(__name__)


class Version:
    """Gerenciador de versões seguindo semver (X.Y.Z)"""

    def __init__(
        self, major: int = 0, minor: int = 1, patch: int = 0, pre_release: str = None
    ):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre_release = pre_release

    def __str__(self) -> str:
        """Retorna a versão no formato semver"""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version += f"-{self.pre_release}"
        return version

    def __repr__(self) -> str:
        return (
            f"Version({self.major}, {self.minor}, {self.patch}, {self.pre_release!r})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            return False
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre_release == other.pre_release
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented

        # Compare major.minor.patch first
        if (self.major, self.minor, self.patch) != (
            other.major,
            other.minor,
            other.patch,
        ):
            return (self.major, self.minor, self.patch) < (
                other.major,
                other.minor,
                other.patch,
            )

        # Handle pre-release versions
        if self.pre_release is None and other.pre_release is None:
            return False
        if self.pre_release is None:
            return False  # 1.0.0 > 1.0.0-alpha
        if other.pre_release is None:
            return True  # 1.0.0-alpha < 1.0.0

        return self.pre_release < other.pre_release

    def bump_major(self) -> "Version":
        """Incrementa versão major (breaking changes)"""
        return Version(self.major + 1, 0, 0)

    def bump_minor(self) -> "Version":
        """Incrementa versão minor (new features)"""
        return Version(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "Version":
        """Incrementa versão patch (bug fixes)"""
        return Version(self.major, self.minor, self.patch + 1)

    def set_pre_release(self, pre_release: str) -> "Version":
        """Define pre-release (alpha, beta, rc.1, etc.)"""
        return Version(self.major, self.minor, self.patch, pre_release)

    @classmethod
    def parse(cls, version_string: str) -> "Version":
        """
        Parse string de versão no formato semver

        Args:
            version_string: String no formato "1.2.3" ou "1.2.3-alpha"

        Returns:
            Instância de Version

        Raises:
            ValueError: Se formato for inválido
        """
        # Regex para semver: major.minor.patch[-pre_release]
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\.\-]+))?$"
        match = re.match(pattern, version_string.strip())

        if not match:
            raise ValueError(f"Invalid version format: {version_string}")

        major, minor, patch, pre_release = match.groups()
        return cls(int(major), int(minor), int(patch), pre_release)


class VersionManager:
    """Gerenciador de versionamento integrado com Git"""

    def __init__(self, version_file: str = "VERSION"):
        self.version_file = Path(version_file)
        self.logger = get_logger(__name__)

    def get_current_version(self) -> Version:
        """Lê a versão atual do arquivo VERSION"""
        try:
            if self.version_file.exists():
                version_string = self.version_file.read_text().strip()
                return Version.parse(version_string)
            else:
                # Versão inicial
                return Version(0, 1, 0)
        except Exception as e:
            self.logger.error(f"Error reading version file: {e}")
            return Version(0, 1, 0)

    def save_version(self, version: Version) -> bool:
        """Salva versão no arquivo VERSION"""
        try:
            self.version_file.write_text(str(version))
            self.logger.info(f"Version saved: {version}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving version: {e}")
            return False

    def bump_version(
        self, bump_type: str, pre_release: str = None
    ) -> Optional[Version]:
        """
        Incrementa versão baseado no tipo

        Args:
            bump_type: 'major', 'minor', 'patch'
            pre_release: String de pre-release opcional

        Returns:
            Nova versão ou None em caso de erro
        """
        current = self.get_current_version()

        if bump_type == "major":
            new_version = current.bump_major()
        elif bump_type == "minor":
            new_version = current.bump_minor()
        elif bump_type == "patch":
            new_version = current.bump_patch()
        else:
            self.logger.error(f"Invalid bump type: {bump_type}")
            return None

        if pre_release:
            new_version = new_version.set_pre_release(pre_release)

        if self.save_version(new_version):
            self.logger.info(f"Version bumped: {current} -> {new_version}")
            return new_version

        return None

    def get_git_info(self) -> dict[str, str]:
        """Obtém informações do Git sobre o commit atual"""
        try:
            # Git hash
            git_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=os.getcwd(), text=True
            ).strip()

            # Git hash curto
            git_hash_short = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], cwd=os.getcwd(), text=True
            ).strip()

            # Branch atual
            git_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=os.getcwd(), text=True
            ).strip()

            # Data do último commit
            git_date = subprocess.check_output(
                ["git", "log", "-1", "--format=%ci"], cwd=os.getcwd(), text=True
            ).strip()

            return {
                "hash": git_hash,
                "hash_short": git_hash_short,
                "branch": git_branch,
                "date": git_date,
            }
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Could not get git info: {e}")
            return {
                "hash": "unknown",
                "hash_short": "unknown",
                "branch": "unknown",
                "date": "unknown",
            }

    def create_git_tag(self, version: Version, message: str = None) -> bool:
        """
        Cria tag no Git para a versão

        Args:
            version: Versão para criar a tag
            message: Mensagem da tag (opcional)

        Returns:
            True se tag foi criada com sucesso
        """
        tag_name = f"v{version}"
        tag_message = message or f"Release {version}"

        try:
            # Criar tag anotada
            subprocess.check_output(
                ["git", "tag", "-a", tag_name, "-m", tag_message], cwd=os.getcwd()
            )

            self.logger.info(f"Git tag created: {tag_name}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create git tag: {e}")
            return False

    def get_version_info(self) -> dict:
        """Retorna informações completas da versão"""
        version = self.get_current_version()
        git_info = self.get_git_info()

        return {
            "version": str(version),
            "version_parts": {
                "major": version.major,
                "minor": version.minor,
                "patch": version.patch,
                "pre_release": version.pre_release,
            },
            "git": git_info,
            "build_date": datetime.now().isoformat(),
            "is_development": git_info["branch"] != "main",
        }

    def release(
        self, bump_type: str, message: str = None, create_tag: bool = True
    ) -> Optional[Version]:
        """
        Processo completo de release

        Args:
            bump_type: Tipo de incremento ('major', 'minor', 'patch')
            message: Mensagem do release
            create_tag: Se deve criar tag no Git

        Returns:
            Nova versão ou None em caso de erro
        """
        self.logger.info(f"Starting release process: {bump_type}")

        # Incrementar versão
        new_version = self.bump_version(bump_type)
        if not new_version:
            return None

        # Criar tag no Git
        if create_tag:
            tag_message = message or f"Release {new_version}"
            if not self.create_git_tag(new_version, tag_message):
                self.logger.warning("Failed to create git tag, but version was updated")

        self.logger.info(f"Release completed: {new_version}")
        return new_version


# Instância global do gerenciador de versão
version_manager = VersionManager()


def get_version() -> str:
    """Função helper para obter versão atual como string"""
    return str(version_manager.get_current_version())


def get_version_info() -> dict:
    """Função helper para obter informações completas da versão"""
    return version_manager.get_version_info()
