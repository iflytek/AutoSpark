from pydantic import BaseModel


class ValidateAPIKeyRequest(BaseModel):
    model_source: str
    model_api_key: str
    model_api_secret: str
    model_app_id: str
