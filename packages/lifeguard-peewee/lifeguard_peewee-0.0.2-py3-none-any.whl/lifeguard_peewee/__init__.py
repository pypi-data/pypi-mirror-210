"""
Lifeguard integration with MongoDB
"""
from lifeguard.repositories import declare_implementation

from lifeguard_peewee.context import CONTEXT
from lifeguard_peewee.repositories import (
    PeeweeValidationRepository,
    PeeweeNotificationRepository,
)


class LifeguardPeeweePlugin:
    def __init__(self, lifeguard_context):
        self.lifeguard_context = lifeguard_context
        CONTEXT["database"].connect()
        declare_implementation("notification", PeeweeNotificationRepository)
        declare_implementation("validation", PeeweeValidationRepository)


def init(lifeguard_context):
    LifeguardPeeweePlugin(lifeguard_context)
