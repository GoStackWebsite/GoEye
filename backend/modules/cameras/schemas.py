from pydantic import BaseModel, ConfigDict


# Request body for creating a camera
class CameraCreate(BaseModel):
    id: str
    name: str
    source: str
    enabled: bool = True


# Camera as returned by the API
class CameraOut(CameraCreate):
    model_config = ConfigDict(from_attributes=True)
