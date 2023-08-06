import os

from arkindex_export.models import (
    Classification,
    Element,
    ElementPath,
    Entity,
    EntityLink,
    EntityRole,
    EntityType,
    ExportVersion,
    Image,
    ImageServer,
    Metadata,
    Transcription,
    TranscriptionEntity,
    WorkerVersion,
    database,
)

# Expose all these models to library users  if they want to import them all
__all__ = [
    "ExportVersion",
    "WorkerVersion",
    "ImageServer",
    "Image",
    "Element",
    "Classification",
    "ElementPath",
    "Entity",
    "EntityType",
    "EntityRole",
    "EntityLink",
    "Metadata",
    "Transcription",
    "TranscriptionEntity",
]


def open_database(path: str, minimum_version: int = None):
    """
    Open connection towards an SQLite database
    and use it as source for Arkindex export models
    """
    assert os.path.exists(path), f"Invalid path {path}"

    database.init(
        path,
        pragmas={
            # Recommended settings from peewee
            # http://docs.peewee-orm.com/en/latest/peewee/database.html#recommended-settings
            # Do not set journal mode to WAL as it writes in the database
            "cache_size": -1 * 64000,  # 64MB
            "foreign_keys": 1,
            "ignore_check_constraints": 0,
            "synchronous": 0,
        },
    )

    # Check this database is compatible with the minimum version requested
    if minimum_version is not None:
        version = ExportVersion.select().first().version
        if version < minimum_version:
            raise Exception(
                f"Database (version {version}) is not compatible with minimum version {minimum_version}"
            )
