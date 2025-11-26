#-------------------------------------------------------------------------
# 💼 DAY 5: AI SALES DEVELOPMENT REP (SDR)
# ✈️ "TripWave Travels" - Auto-Lead Capture Agent
# 🚀 Features: FAQ Retrieval, Lead Qualification, JSON Database
#-------------------------------------------------------------------------

import logging
import json
import os
import asyncio
from datetime import datetime
from typing import Annotated, Literal, Optional, List
from dataclasses import dataclass, asdict

from dotenv import load_dotenv
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)

# 🔌 PLUGINS
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")


# 📂 1. KNOWLEDGE BASE (FAQ)

FAQ_FILE = "store_faq.json"      # keeping filename same, only content changed to travel
LEADS_FILE = "leads_db.json"

# Default FAQ data for "TripWave Travels"
DEFAULT_FAQ = [
    {
        "question": "What services do you offer?",
        "answer": (
            "TripWave Travels is an Indian travel agency that offers domestic and international tour packages, "
            "custom trip planning, hotel and flight bookings, and weekend getaways. We also help with visas "
            "and airport transfers for selected destinations."
        )
    },
    {
        "question": "How much do your tour packages cost?",
        "answer": (
            "We have budget, standard and premium packages. Pricing depends on destination, hotel category, "
            "travel dates and group size. For this demo, I’ll only talk in rough ranges instead of exact prices."
        )
    },
    {
        "question": "Do you offer EMI or flexible payment options?",
        "answer": (
            "For many trips we support part-payment or staged payments before the travel date. In this demo, "
            "details are kept high level, but in a real setup we would share exact EMI and payment options."
        )
    },
    {
        "question": "Do you handle corporate or group travel?",
        "answer": (
            "Yes, TripWave Travels also handles corporate offsites, college trips and family group tours. "
            "We can customize itineraries based on budget, headcount and duration."
        )
    }
]

def load_knowledge_base():
    """Generates FAQ file if missing, then loads it."""
    try:
        path = os.path.join(os.path.dirname(__file__), FAQ_FILE)
        if not os.path.exists(path):
            with open(path, "w", encoding='utf-8') as f:
                json.dump(DEFAULT_FAQ, f, indent=4)
        with open(path, "r", encoding='utf-8') as f:
            return json.dumps(json.load(f))  # Return as string for the Prompt
    except Exception as e:
        print(f"⚠️ Error loading FAQ: {e}")
        return ""

STORE_FAQ_TEXT = load_knowledge_base()


# 💾 2. LEAD DATA STRUCTURE

@dataclass
class LeadProfile:
    name: str | None = None
    people: str | None = None   # here: how many people in the group or solo 
    email: str | None = None
    role: str | None = None      # e.g. traveller, group lead, HR, admin
    use_case: str | None = None  # what trip they want to plan
    team_size: str | None = None # group size / number of travellers
    timeline: str | None = None  # when they want to travel

    def is_qualified(self):
        """Returns True if we have the minimum info (Name + Email + Use Case)"""
        return all([self.name, self.email, self.use_case])

@dataclass
class Userdata:
    lead_profile: LeadProfile


# 🛠️ 3. SDR TOOLS

@function_tool
async def update_lead_profile(
    ctx: RunContext[Userdata],
    name: Annotated[Optional[str], Field(description="Customer's name")] = None,
    people: Annotated[Optional[str], Field(description="Customer's company/group name (if any)")] = None,
    email: Annotated[Optional[str], Field(description="Customer's email address")] = None,
    role: Annotated[Optional[str], Field(description="Customer's role (e.g. traveller, HR, organizer)")] = None,
    use_case: Annotated[Optional[str], Field(description="What kind of trip they want to plan")] = None,
    team_size: Annotated[Optional[str], Field(description="Number of travellers in their group")] = None,
    timeline: Annotated[Optional[str], Field(description="When they want to travel (e.g. next month, in winter)")] = None,
) -> str:
    """
    ✍️ Captures lead details provided by the user during conversation.
    Only call this when the user explicitly provides information.
    """
    profile = ctx.userdata.lead_profile

    # Update only fields that are provided (not None)
    if name: profile.name = name
    if people: profile.people = people
    if email: profile.email = email
    if role: profile.role = role
    if use_case: profile.use_case = use_case
    if team_size: profile.team_size = team_size
    if timeline: profile.timeline = timeline

    print(f"📝 UPDATING LEAD: {profile}")
    return "Lead profile updated. Continue the conversation."

@function_tool
async def submit_lead_and_end(
    ctx: RunContext[Userdata],
) -> str:
    """
    💾 Saves the lead to the database and signals the end of the call.
    Call this when the user says goodbye or 'that's all'.
    """
    profile = ctx.userdata.lead_profile

    # Save to JSON file (Append mode)
    db_path = os.path.join(os.path.dirname(__file__), LEADS_FILE)

    entry = asdict(profile)
    entry["timestamp"] = datetime.now().isoformat()

    # Read existing, append, write back (Simple JSON DB)
    existing_data = []
    if os.path.exists(db_path):
        try:
            with open(db_path, "r") as f:
                existing_data = json.load(f)
        except:
            pass

    existing_data.append(entry)

    with open(db_path, "w") as f:
        json.dump(existing_data, f, indent=4)

    print(f"✅ LEAD SAVED TO {LEADS_FILE}")
    return (
        f"Lead saved. Summarize the call for the user: "
        f"'Thanks {profile.name}, I have your info regarding your trip: {profile.use_case}. "
        f"We will email you at {profile.email} with trip details. Goodbye!'"
    )


# 🧠 4. AGENT DEFINITION

class SDRAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=f"""
            You are Sarah, the SDR for TripWave Travels, a travel service that helps customers plan trips, book packages, 
            and arrange travel experiences stress-free.

            📘 **YOUR KNOWLEDGE BASE (FAQ):**
            {STORE_FAQ_TEXT}

            🎯 **YOUR GOAL:**
            1. Answer questions about our travel packages, destinations, pricing ranges and services using the FAQ.
            2. **QUALIFY THE LEAD:** Naturally ask for the following details during the chat:
               - Name
               - Company / Group / Role (for example: solo traveller, family, HR, organizer)
               - Email
               - What kind of trip they want to plan (Use Case)
               - Group size (Team size)
               - Timeline (When they want to travel)

            ⚙️ **BEHAVIOR:**
            - Be conversational and warm, like a human travel planner.
            - Answer a question, THEN gently ask for one detail.
            - Example: "Our Goa packages include flights and hotels. By the way, how many people are travelling with you?"
            - Use `update_lead_profile` whenever the user gives new details.
            - When they say they're done or goodbye, use `submit_lead_and_end`.

            🚫 **RESTRICTIONS:**
            - Do NOT invent exact prices or confirm bookings.
            - If you don't know an answer, say "I'll check with our travel team and email you the details."

            Keep responses short, clear and friendly for voice interaction.
            """,
            tools=[update_lead_profile, submit_lead_and_end],
        )


# 🎬 ENTRYPOINT

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    print("\n" + "💼" * 25)
    print("🚀 STARTING TRAVEL SDR SESSION")

    # 1. Initialize State
    userdata = Userdata(lead_profile=LeadProfile())

    # 2. Setup Agent
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-natalie",  # Professional, warm female voice
            style="Promo",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )

    # 3. Start
    await session.start(
        agent=SDRAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
