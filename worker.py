import os
import json
import uuid
import aiohttp
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import openai, silero

load_dotenv()

API_KEY = os.getenv("API_KEY")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# 🔹 RAG tool: calls external API and returns response text


@function_tool
async def rag_answer(context: RunContext, prompt: str,auth_token: str, app_ref_code: str):
    """
    Fetches RAG-based response for a given user prompt using Neo-world API.
    """
    url = "https://console-staging1.neo-world.com/neomichatbot/app/v1/voice/rag"
    headers = {
        "authorization": f"{auth_token}",
        "Content-Type": "application/json",
    }

    data = {
        "app_ref_code": app_ref_code, # random short code
        "prompt": prompt,
        "app_prompt": prompt,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            result = await resp.text()
            try:
                result_json = json.loads(result)
                return result_json
            except json.JSONDecodeError:
                return {"response": result}

@function_tool
async def infinity_answer(context: RunContext, prompt: str, auth_token: str, app_ref_code: str, app_prompt: str):

    url = "https://console-staging1.neo-world.com/neomichatbot/app/v1/voice/infinity"

    headers = {
        "authorization": f"{auth_token}",
        "Content-Type": "application/json",
    }

    data = {
        "app_ref_code": app_ref_code,
        "prompt": prompt,
        "app_prompt": app_prompt,
    }


    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            result_text = await resp.text()
            try:
                result_json = json.loads(result_text)
                return result_json
            except json.JSONDecodeError:
                return {"response": result_text}
    

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="""You are an intelligent AI assistant for Neo Group, a financial asset management company.
        You are knowledgeable, professional, and helpful conversational AI female version that mimics a friendly, witty human chatting in real time.
        Rules:
        
        1. Use **infinity_answer** ONLY for queries involving a *client* or their personal/financial data, such as:
           - portfolio details
           - holdings
           - profit/loss (P&L)
           - performance
           - transactions
           - taxation
           - personal info (email, PAN, Aadhaar, contact, etc.)
           - any query referring to a client's name or family group
        
           **Examples:**
           - “What is the overall performance of Manjeet Kripalani and Family?”
           - “Aadhaar card and PAN card details of Sanjeev Junjeja.”
           - “Show portfolio breakdown for Rahul Patel.”
        
        2. Use **rag_answer** for **all other queries**, including:
           - general company/product info
           - policies, leave, help, errors
           - app-related actions
           - downloads, reports, documents, files
           - help with any questions about Neo Group's investment products, financial information, or general queries.
        
           **Examples:**
           - “Tell me about Neo’s investment process.”
           - “Download soa of riyaz ladiwala”
           - “Steps to apply for leave.”
           - "Scout vijay patel at neo wealth",
           - "Scan Manisha Ambulkar 8902020459,manish@new.com Finserv",
           - "My profile details"
        
        3. Never mention any tool names to the user.
        4. Always keep responses short, confident, and conversational.
        Strictly never mention about any keyword to user""",
        tools=[rag_answer, infinity_answer],
    )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model="gpt-4o-mini-transcribe", api_key=API_KEY),
        llm=openai.LLM(model="gpt-4o-mini", api_key=API_KEY),
        tts=openai.TTS(voice="nova", api_key=API_KEY),
    )

    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(instructions="Greet the user and ask how you can help today.")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
        )
    )
