"""
Implementation of repositories using MongoDB
"""
import json

from lifeguard.notifications import NotificationStatus
from lifeguard.validations import ValidationResponse

from lifeguard_peewee.models import ValidationModel, NotificationModel


def save_or_update(model, query, data):
    """
    Check if entry exists and create or update entry
    :param collection:
    :param query:
    :param data:
    """
    if model.select().where(query).count():
        model.update(**data).where(query).execute()
    else:
        model.create(**data)


class PeeweeValidationRepository:
    """
    Implementation of ValidationRepository with Peewee
    """

    def save_validation_result(self, validation_result):
        save_or_update(
            ValidationModel,
            (ValidationModel.validation_name == validation_result.validation_name),
            {
                "validation_name": validation_result.validation_name,
                "status": validation_result.status,
                "details": json.dumps(validation_result.details),
                "settings": json.dumps(validation_result.settings or {}),
                "last_execution": validation_result.last_execution,
            },
        )

    def fetch_last_validation_result(self, validation_name):
        result = ValidationModel.get(ValidationModel.validation_name == validation_name)
        if result:
            return self.__convert_to_validation(result)
        return None

    def fetch_all_validation_results(self):
        results = []
        for result in ValidationModel.select():
            results.append(self.__convert_to_validation(result))

        return results

    def __convert_to_validation(self, validation_document):
        return ValidationResponse(
            validation_document.status,
            json.loads(validation_document.details),
            json.loads(validation_document.settings),
            last_execution=validation_document.last_execution,
            validation_name=validation_document.validation_name,
        )


class PeeweeNotificationRepository:
    """
    Implementation of NotificationRepository with Peewee
    """

    def save_last_notification_for_a_validation(self, notification):
        save_or_update(
            NotificationModel,
            (NotificationModel.validation_name == notification.validation_name),
            {
                "validation_name": notification.validation_name,
                "thread_ids": json.dumps(notification.thread_ids),
                "is_opened": notification.is_opened,
                "options": json.dumps(notification.options),
                "last_notification": notification.last_notification,
            },
        )

    def fetch_last_notification_for_a_validation(self, validation_name):
        result = (
            NotificationModel.select()
            .where(NotificationModel.validation_name == validation_name)
            .first()
        )
        if result:
            last_notification_status = NotificationStatus(
                validation_name,
                json.loads(result["thread_ids"]),
                json.loads(result["options"]),
            )
            last_notification_status.last_notification = result["last_notification"]
            last_notification_status.is_opened = result["is_opened"]
            return last_notification_status
        return None
