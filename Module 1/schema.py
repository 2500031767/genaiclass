from pydantic import BaseModel, Field

class TextRequest(BaseModel):
    topic: str = Field(..., description="The topic for which to generate text.", example="Artificial Intelligence")
    course: str = Field(..., description="The subject matter related to the topic.", example="The impact of AI on modern society.")
    student_level: str = Field(..., description="The educational level of the student.", example="beginner")
