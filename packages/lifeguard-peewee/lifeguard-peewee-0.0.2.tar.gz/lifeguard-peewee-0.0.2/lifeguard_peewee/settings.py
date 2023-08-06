"""
Lifeguard MongoDB Settings
"""
from lifeguard.settings import SettingsManager

SETTINGS_MANAGER = SettingsManager(
    {
        "LIFEGUARD_PEEWEE_DBMS_NAME": {"default": "mysql", "description": "DBMS name"},
        "LIFEGUARD_PEEWEE_HOST": {"default": "localhost", "description": "DBMS host"},
        "LIFEGUARD_PEEWEE_PORT": {"default": "3306", "description": "DBMS port"},
        "LIFEGUARD_PEEWEE_USER": {"default": "user", "description": "DBMS user"},
        "LIFEGUARD_PEEWEE_PASSWORD": {
            "default": "password",
            "description": "DBMS password",
        },
        "LIFEGUARD_PEEWEE_DATABASE": {
            "default": "lifeguard",
            "description": "DBMS database name",
        },
    }
)

LIFEGUARD_PEEWEE_DBMS_NAME = SETTINGS_MANAGER.read_value("LIFEGUARD_PEEWEE_DBMS_NAME")
LIFEGUARD_PEEWEE_HOST = SETTINGS_MANAGER.read_value("LIFEGUARD_PEEWEE_HOST")
LIFEGUARD_PEEWEE_PORT = int(SETTINGS_MANAGER.read_value("LIFEGUARD_PEEWEE_PORT"))
LIFEGUARD_PEEWEE_USER = SETTINGS_MANAGER.read_value("LIFEGUARD_PEEWEE_USER")
LIFEGUARD_PEEWEE_PASSWORD = SETTINGS_MANAGER.read_value("LIFEGUARD_PEEWEE_PASSWORD")
LIFEGUARD_PEEWEE_DATABASE = SETTINGS_MANAGER.read_value("LIFEGUARD_PEEWEE_DATABASE")
