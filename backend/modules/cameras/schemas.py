from pydantic import BaseModel


# A configured camera and whether its live frames are arriving
class CameraOut(BaseModel):
    id: str
    online: bool
