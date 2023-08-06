from peewee import (
    SQL,
    BareField,
    CharField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)

# Use a database unknown before runtime
database = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = database


class ExportVersion(BaseModel):
    version = BareField(adapt=int)

    class Meta:
        table_name = "export_version"
        primary_key = False


class WorkerVersion(BaseModel):
    id = CharField(primary_key=True)
    slug = CharField()
    name = CharField()
    repository_url = TextField()
    revision = CharField()
    type = CharField()

    class Meta:
        table_name = "worker_version"


class ImageServer(BaseModel):
    id = CharField(primary_key=True)
    url = TextField(unique=True)
    display_name = CharField()
    max_width = IntegerField(null=True)
    max_height = IntegerField(null=True)

    class Meta:
        table_name = "image_server"


class Image(BaseModel):
    id = CharField(primary_key=True)
    server = ForeignKeyField(column_name="server_id", field="id", model=ImageServer)
    url = TextField(unique=True)
    width = IntegerField()
    height = IntegerField()

    class Meta:
        table_name = "image"


class Element(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    type = CharField()
    image = ForeignKeyField(column_name="image_id", field="id", model=Image, null=True)
    polygon = TextField(null=True)
    confidence = FloatField(null=True)
    rotation_angle = IntegerField(constraints=[SQL("DEFAULT 0")])
    mirrored = IntegerField(constraints=[SQL("DEFAULT 0")])
    worker_version = ForeignKeyField(
        column_name="worker_version_id", field="id", model=WorkerVersion, null=True
    )

    created = FloatField()
    updated = FloatField()

    class Meta:
        table_name = "element"


class Classification(BaseModel):
    id = CharField(primary_key=True)
    class_name = CharField()
    confidence = FloatField(null=True)
    state = CharField(constraints=[SQL("DEFAULT 'pending'")])
    element = ForeignKeyField(column_name="element_id", field="id", model=Element)
    high_confidence = IntegerField(constraints=[SQL("DEFAULT 0")])
    moderator = CharField(null=True)
    worker_version = ForeignKeyField(
        column_name="worker_version_id", field="id", model=WorkerVersion, null=True
    )

    class Meta:
        table_name = "classification"


class ElementPath(BaseModel):
    id = CharField(primary_key=True)
    parent = ForeignKeyField(
        backref="element_parent_set", column_name="parent_id", field="id", model=Element
    )
    child = ForeignKeyField(column_name="child_id", field="id", model=Element)
    ordering = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = "element_path"
        indexes = ((("parent", "child"), True),)


class EntityType(BaseModel):
    color = CharField(constraints=[SQL("DEFAULT 'ff0000'")])
    id = CharField(primary_key=True)
    name = TextField(unique=True)

    class Meta:
        table_name = "entity_type"


class Entity(BaseModel):
    id = CharField(primary_key=True)
    name = TextField()
    type = ForeignKeyField(column_name="type_id", field="id", model=EntityType)
    metas = TextField(null=True)
    moderator = CharField(null=True)
    validated = IntegerField(constraints=[SQL("DEFAULT 0")])
    worker_version = ForeignKeyField(
        column_name="worker_version_id", field="id", model=WorkerVersion, null=True
    )

    class Meta:
        table_name = "entity"


class EntityRole(BaseModel):
    id = CharField(primary_key=True)
    parent_name = CharField()
    parent_type = ForeignKeyField(
        backref="entity_type_parent_type_set",
        column_name="parent_type_id",
        field="id",
        model=EntityType,
    )
    child_name = CharField()
    child_type = ForeignKeyField(
        column_name="child_type_id", field="id", model=EntityType
    )

    class Meta:
        table_name = "entity_role"
        indexes = ((("parent_name", "child_name", "parent_type", "child_type"), True),)


class EntityLink(BaseModel):
    id = CharField(primary_key=True)
    parent = ForeignKeyField(
        backref="entity_parent_set", column_name="parent_id", field="id", model=Entity
    )
    child = ForeignKeyField(column_name="child_id", field="id", model=Entity)
    role = ForeignKeyField(column_name="role_id", field="id", model=EntityRole)

    class Meta:
        table_name = "entity_link"


class Metadata(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    value = TextField()
    type = CharField()
    element = ForeignKeyField(column_name="element_id", field="id", model=Element)
    entity = ForeignKeyField(
        column_name="entity_id", field="id", model=Entity, null=True
    )
    worker_version = ForeignKeyField(
        column_name="worker_version_id", field="id", model=WorkerVersion, null=True
    )

    class Meta:
        table_name = "metadata"


class Transcription(BaseModel):
    id = CharField(primary_key=True)
    text = TextField()
    confidence = FloatField(null=True)
    element = ForeignKeyField(column_name="element_id", field="id", model=Element)
    worker_version = ForeignKeyField(
        column_name="worker_version_id", field="id", model=WorkerVersion, null=True
    )

    class Meta:
        table_name = "transcription"


class TranscriptionEntity(BaseModel):
    id = CharField(primary_key=True)
    entity = ForeignKeyField(column_name="entity_id", field="id", model=Entity)
    length = IntegerField()
    offset = IntegerField()
    confidence = FloatField(null=True)
    transcription = ForeignKeyField(
        column_name="transcription_id", field="id", model=Transcription
    )
    worker_version = ForeignKeyField(
        column_name="worker_version_id", field="id", model=WorkerVersion, null=True
    )

    class Meta:
        table_name = "transcription_entity"
        indexes = (
            (("transcription", "entity", "offset", "length", "worker_version"), True),
        )
