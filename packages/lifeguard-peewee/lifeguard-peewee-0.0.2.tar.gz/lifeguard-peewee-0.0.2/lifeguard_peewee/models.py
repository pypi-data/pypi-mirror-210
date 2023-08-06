from peewee import BooleanField, CharField, DateTimeField, Model, TextField

from lifeguard_peewee.context import connection_factory

database = connection_factory()


class BaseModel(Model):
    class Meta:
        database = database


class ValidationModel(BaseModel):
    """
    Validation Model
    """

    validation_name = CharField(unique=True)
    status = CharField()
    details = TextField()
    settings = TextField()
    last_execution = DateTimeField()

    class Meta:
        """
        Base Model Meta
        """

        db_table = "validations"


class NotificationModel(BaseModel):
    """
    Notification Model
    """

    validation_name = CharField(unique=True)
    thread_ids = TextField()
    is_opened = BooleanField()
    options = TextField()
    last_execution = DateTimeField()

    class Meta:
        """
        Base Model Meta
        """

        db_table = "notifications"


def create_tables():
    with database:
        database.create_tables([ValidationModel, NotificationModel])
