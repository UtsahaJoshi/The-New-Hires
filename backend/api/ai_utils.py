import openai
from fastapi import HTTPException
import os
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def analyze_diff(diff: str, pr_title: str) -> dict:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API Key not configured")

    try:
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        Act as a senior software engineer. Review the following code diff and provide constructive feedback.
        Return the response as a JSON object with a key "comments", which is a list of objects containing "file", "line", and "message".
        IMPORTANT: The "file" must be the filename as seen in the diff. The "line" must be the line number in the new file (right side of diff).
        
        PR Title: {pr_title}
        
        Diff:
        {diff}
        """
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        print(f"OpenAI Error: {e}")
        # Return empty comments on error to avoid crashing the webhook
        return {"comments": []}

# Voice Mapping
VOICE_MAP = {
    "Sarah": "nova",
    "Mike": "onyx",
    "Alex": "echo",
    "Emily": "shimmer",
    "David": "fable"
}

async def generate_coworker_update(name: str, role: str, context: str) -> str:
    if not OPENAI_API_KEY:
        return f"I am working on {context}. No blockers."
        
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""
    Act as {name}, a {role} at a tech startup. Give a very short (1-2 sentences) daily standup update.
    Context: {context}.
    Tone: Casual, slightly tired but professional.
    """
    
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

async def generate_voice(text: str, name: str) -> bytes:
    if not OPENAI_API_KEY:
        # Return empty bytes - frontend will handle this gracefully
        return b''
    
    try:
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        voice = VOICE_MAP.get(name, "alloy")
        
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        return response.content
    except Exception as e:
        print(f"Voice generation failed: {e}")
        # Return empty bytes on error - frontend will show skip button
        return b''

async def transcribe_audio(file_path: str) -> str:
    if not OPENAI_API_KEY:
        return "Mock transcription: I worked on the login feature."
        
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    with open(file_path, "rb") as audio_file:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text
