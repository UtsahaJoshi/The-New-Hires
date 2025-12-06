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
