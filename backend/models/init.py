# Keep this package initializer minimal to avoid import side-effects during Alembic.
# DO NOT import model modules here (e.g., document, user, shipment, etc.).
# If you need to import a specific model elsewhere, import it explicitly from its module.

from .base import Base  # re-export for convenience
