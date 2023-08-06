"""
Lifeguard integration with TinyDB
"""
from lifeguard.repositories import declare_implementation

from lifeguard_tinydb.repositories import (
    TinyDBNotificationRepository,
    TinyDBValidationRepository,
)


class LifeguardTinyDBPlugin:
    def __init__(self, lifeguard_context):
        self.lifeguard_context = lifeguard_context
        declare_implementation("notification", TinyDBNotificationRepository)
        declare_implementation("validation", TinyDBValidationRepository)


def init(lifeguard_context):
    LifeguardTinyDBPlugin(lifeguard_context)
