import os
import json
from fastapi import FastAPI, UploadFile, File, Form,HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
from dotenv import load_dotenv
from schema import TextRequest
import jwt


load_dotenv()

  # Load environment variables from .env file

SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("SCERET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

model = os.getenv("CHAT_MODEL")
if not model:
    raise ValueError("CHAT_MODEL is not set in the environment variables.")

app = FastAPI(
    title="Module 1 - API Interaction of AI Tutor Project",
    description="This API allows interaction with the Gemini API for generating text based on a given topic, course, and student level.",
    version="1.0.0"
)

ai_client = genai.Client(api_key=gemini_api_key)

def get_current_user(token: str = Header(...)):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["username"]
    except Exception:
        raise HTTPException(status_code=401, detail={"message": "Token Invalid or Expired"})


# Text input to generate explanation for the topic, course, and student level
@app.post("/generate_text")
async def generate_explanation(request: TextRequest, username: str = Depends(get_current_user)):
    prompt = f"""
    You are an AI tutor creating study material for a student.
    Topic: "{request.topic}"
    Subject: "{request.course or "Not specified"}"
    Student level: "{request.student_level}"

    Explain the topic clearly and accurately using language suited to the student.
    Output a valid JSON response containing:
    1. "topic": string
    2. "lesson_content": string (clear explanation for study)
    3. "key_terms": list of objects with "term" and "definition" strings
    4. "example": string (a relevant example)
    5. "practice_questions": list of 3 questions
    """

    try:
        response = ai_client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )

        response_json = json.loads(response.text)
        return JSONResponse(status_code=200, content=response_json)
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Academic Image Analysis and Explanation
@app.post("/analyze_image")
async def analyze_image(file: UploadFile = File(...), question: str = Form(...), username: str = Depends(get_current_user)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        return JSONResponse(status_code=400, content={"error": "Invalid file type. Only JPEG and PNG are allowed."})

    try:
        image_bytes = await file.read()
        image_input = types.Part.from_bytes(data=image_bytes, mime_type=file.content_type)

        prompt = f"""
        You are an AI tutor analyzing an academic image.
        Question: "{question}"

        Provide a clear and accurate explanation of the image in relation to the question.
        Output a valid JSON response containing:
        1. "image_analysis": string (detailed analysis of the image)
        2. "key_points": list of strings (important points from the analysis)
        3. "related_concepts": list of strings (concepts related to the image and question)
        """

        response = ai_client.models.generate_content(
            model=model,
            contents=[prompt, image_input],
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
        )

        response_json = json.loads(response.text)
        return JSONResponse(status_code=200, content=response_json)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Text Question and Audio Answer Evaluation
@app.post("/evaluate_audio_answer")
async def evaluate_audio_answer(file: UploadFile = File(...), question: str = Form(...), username: str = Depends(get_current_user)):
    if file.content_type not in ["audio/mpeg", "audio/wav"]:
        return JSONResponse(status_code=400, content={"error": "Invalid file type. Only MP3 and WAV are allowed."})

    try:
        audio_bytes = await file.read()
        audio_input = types.Part.from_bytes(data=audio_bytes, mime_type=file.content_type)

        prompt = f"""
        You are an AI tutor evaluating a student's answer to a question.
        Question: "{question}"

        Evaluate the student's answer provided in the audio file.
        Output a valid JSON response containing:
        1. "evaluation": string (detailed evaluation of the answer)
        2. "score": integer (score out of 10)
        3. "feedback": string (constructive feedback for improvement)
        """

        response = ai_client.models.generate_content(
            model=model,
            contents=[prompt, audio_input],
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
        )

        response_json = json.loads(response.text)
        return JSONResponse(status_code=200, content=response_json)
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Video Analysis and Generate 3 MCQ Questions with options and answers
@app.post("/analyze_video")
async def analyze_video(file: UploadFile = File(...), question: str = Form(...), username: str = Depends(get_current_user)):
    if file.content_type not in ["video/mp4", "video/avi"]:
        return JSONResponse(status_code=400, content={"error": "Invalid file type. Only MP4 and AVI are allowed."})

    try:
        video_bytes = await file.read()
        video_input = types.Part.from_bytes(data=video_bytes, mime_type=file.content_type)

        prompt = f"""
        You are an AI tutor analyzing an academic video.
        Question: "{question}"

        Provide a clear and accurate analysis of the video in relation to the question.
        Generate 3 multiple-choice questions (MCQs) based on the video content, each with 4 options and the correct answer.
        Output a valid JSON response containing:
        1. "video_analysis": string (detailed analysis of the video)
        2. "mcq_questions": list of objects with "question", "options" (list of strings), and "correct_answer" (string)
        """

        response = ai_client.models.generate_content(
            model=model,
            contents=[prompt, video_input],
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
        )

        response_json = json.loads(response.text)
        return JSONResponse(status_code=200, content=response_json)
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})    



@app.post("/analyze_document")

# Line 2: Define asynchronous function
async def analyze_document(
    file: UploadFile = File(...),
    question: str = Form(...)
):

    # Line 3: Define supported document formats
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]

    # Line 4: Validate uploaded document format
    if file.content_type not in allowed_types:

        # Line 5: Return error for unsupported file format
        return JSONResponse(
            status_code=400,
            content={
                "error": "Only PDF, DOC and DOCX files are allowed."
            }
        )

    try:

        # Line 6: Read uploaded document as bytes
        document_bytes = await file.read()

        # Line 7: Convert document into AI-compatible input
        document_input = types.Part.from_bytes(
            data=document_bytes,
            mime_type=file.content_type
        )

        # Line 8: Create AI prompt for document analysis
        prompt = f"""
        You are an AI tutor analyzing an academic document.

        User Question: "{question}"

        Analyze the uploaded document carefully.

        Provide a detailed explanation of the document.
        Identify important concepts and key points.
        Answer the user's question.
        Generate 3 multiple-choice questions.
        Each question must contain 4 options.
        Provide the correct answer.

        Return the response in valid JSON format containing:
        1. document_analysis
        2. key_points
        3. answer
        4. mcq_questions
        """

        # Line 9: Send prompt and document to Google AI model
        response = ai_client.models.generate_content(
            model=model,
            contents=[prompt, document_input],

            # Line 10: Configure AI response
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
        )

        # Line 11: Convert AI response into Python JSON object
        response_json = json.loads(response.text)

        # Line 12: Return successful document analysis
        return JSONResponse(
            status_code=200,
            content=response_json
        )

    except Exception as e:

        # Line 13: Handle errors during document processing
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


    

