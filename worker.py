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
async def rag_answer(context: RunContext, prompt: str):
    """
    Fetches RAG-based response for a given user prompt using Neo-world API.
    """
    url = "https://console-staging1.neo-world.com/neomichatbot/app/v1/voice/rag"
    headers = {
        "authorization": "Bearer ory_st_2hGwYWSr6X0ty9WPb5kj6NTFQ2RFGHCl",
        "Content-Type": "application/json",
    }

    data = {
        "app_ref_code": str(uuid.uuid4())[:8],  # random short code
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


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="""You are an intelligent AI assistant for Neo Group, a financial asset management company.
You are knowledgeable, professional, and helpful conversational AI female version that mimics a friendly, witty human chatting in real time.
Your role is to:
Answer Queries – Provide accurate, clear, and contextual answers about Neo's products,policies,e-card,funds, portfolio ,applying leave,scout process,asking for help,error and client services.
Provide Live Updates – Deliver real-time market data including stock prices, exchanges, indices, and recent financial news,relevant recent updates (e.g., market news, company updates, weather, global events).
Portfolio Insights of Client – Share portfolio holdings, P&L, performance analysis, transactions, taxation, and account statements,personal and financial details of clients.

Avoid robotic tones, keep responses short and breezy.
Strictly never mention about any keyword to user""",
        tools=[rag_answer],
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
