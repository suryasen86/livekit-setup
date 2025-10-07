from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import  openai, silero
from dotenv import load_dotenv

load_dotenv()
import os
api_key = os.getenv("API_KEY")

@function_tool
async def lookup_weather(
    context: RunContext,
    location: str,
):
    """Used to look up weather information."""

    return {"weather": "sunny", "temperature": 70}


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="You are a friendly voice assistant built by Surya.",
        tools=[lookup_weather],
    )
    session = AgentSession(
        vad=silero.VAD.load(),
        # any combination of STT, LLM, TTS, or realtime API can be used
        stt=openai.STT(model="gpt-4o-mini-transcribe", api_key=api_key),
        llm=openai.LLM(model="gpt-4o-mini", api_key=api_key),
        tts=openai.TTS(api_key=api_key),
    )

    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(instructions="greet the user and ask about their day")

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            host="localhost",
            port=7881,
            api_key="mykey",
            api_secret="mysecret"
        )
    )
