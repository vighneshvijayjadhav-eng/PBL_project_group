import os

from pydantic import BaseModel


class SettingsConfigDict(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaseSettings(BaseModel):
    model_config = SettingsConfigDict()

    def __init__(self, **data):
        values = {}
        annotations = getattr(self.__class__, "__annotations__", {})
        for field_name in annotations:
            env_name = field_name.upper()
            field_info = getattr(self.__class__, field_name, None)
            if hasattr(field_info, "json_schema_extra") and field_info.json_schema_extra:
                env_name = field_info.json_schema_extra.get("env", env_name)
            elif hasattr(field_info, "description") and isinstance(getattr(field_info, "description"), str):
                env_name = getattr(field_info, "description")

            if env_name in os.environ:
                values[field_name] = os.environ[env_name]
            elif field_name in data:
                values[field_name] = data[field_name]

        values.update(data)
        super().__init__(**values)
