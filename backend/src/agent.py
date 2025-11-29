# IMPROVE THE AGENT AS PER YOUR NEED 1
"""
Day 8 – Voice Game Master (D&D-Style Adventure) - Voice-only GM agent

- Uses LiveKit agent plumbing similar to the provided food_agent_sqlite example.
- GM persona, universe, tone and rules are encoded in the agent instructions.
- Keeps STT/TTS/Turn detector/VAD integration untouched (murf, deepgram, silero, turn_detector).
- Tools:
    - start_adventure(): start a fresh session and introduce the scene
    - get_scene(): return the current scene description (GM text) ending with "What do you do?"
    - player_action(action_text): accept player's spoken action, update state, advance scene
    - show_journal(): list remembered facts, NPCs, named locations, choices
    - restart_adventure(): reset state and start over
- Userdata keeps continuity between turns: history, inventory, named NPCs/locations, choices, current_scene
"""

import json
import logging
import os
import asyncio
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Annotated
from pathlib import Path

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

from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# -------------------------
# Logging
# -------------------------
logger = logging.getLogger("voice_game_master")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

load_dotenv(".env.local")

# JSON state file path
STATE_FILE = Path("ocean_adventure_state.json")

# -------------------------
# Simple Game World Definition (OCEAN STORY)
# -------------------------
# A compact ocean world with a few scenes and choices forming a mini-arc.
WORLD = {
    "intro": {
        "title": "Whispers of the Drowned Reef",
        "desc": (
            "You wake on the pale sands of a crescent-shaped island, waves glowing faint blue in the pre-dawn light. "
            "Far out at sea, the silhouette of a leaning lighthouse rises from a jagged reef, its lantern long dark. "
            "To your right, a narrow path winds toward a small fishing village built on stilts over the water. "
            "Half-buried near your hand lies a barnacle-crusted shell box, washed up by the tide."
        ),
        "choices": {
            "inspect_box": {
                "desc": "Inspect the barnacle-crusted shell box beside you.",
                "result_scene": "box",
            },
            "approach_tower": {
                "desc": "Head toward the distant lighthouse out on the reef.",
                "result_scene": "tower",
            },
            "walk_to_cottages": {
                "desc": "Follow the path toward the stilted fishing village.",
                "result_scene": "cottages",
            },
        },
    },
    "box": {
        "title": "The Shell Box",
        "desc": (
            "The shell box is warm despite the salty breeze. When you pry it open, seawater spills out, "
            "leaving behind a thin strip of seaweed parchment. Faded ink shows a rough map of the reef and the words: "
            "'Below the broken light, the reef remembers.' "
            "As you read, you hear a low hum from the direction of the lighthouse, like a distant song beneath the waves."
        ),
        "choices": {
            "take_map": {
                "desc": "Take the seaweed map and keep it safe.",
                "result_scene": "tower_approach",
                "effects": {
                    "add_journal": "Found seaweed map: 'Below the broken light, the reef remembers.'"
                },
            },
            "leave_box": {
                "desc": "Leave the shell box where it lies and move on.",
                "result_scene": "intro",
            },
        },
    },
    "tower": {
        "title": "The Reef Lighthouse",
        "desc": (
            "After a careful walk over slick rocks, you reach the base of the leaning lighthouse. "
            "Barnacles grip its stone, and waves crash against the reef below. At the base, half-hidden by seaweed, "
            "you find an old iron hatch with a corroded latch, damp and recently disturbed. "
            "You could try the latch, search around the rocks for another way in, or retreat to safer ground."
        ),
        "choices": {
            "try_latch_without_map": {
                "desc": "Try the iron latch without any guidance.",
                "result_scene": "latch_fail",
            },
            "search_around": {
                "desc": "Search the rocks and tide pools for another entrance.",
                "result_scene": "secret_entrance",
            },
            "retreat": {
                "desc": "Retreat back toward the beach.",
                "result_scene": "intro",
            },
        },
    },
    "tower_approach": {
        "title": "Approaching the Broken Light",
        "desc": (
            "Clutching the seaweed map, you make your way across the reef toward the lighthouse. "
            "The markings line up with the iron hatch at the base. As you draw near, a faint humming "
            "echoes through the metal, as if the sea itself is singing through it."
        ),
        "choices": {
            "open_hatch": {
                "desc": "Use the map's clue to work the latch carefully.",
                "result_scene": "latch_open",
                "effects": {"add_journal": "Used map clue to open the lighthouse hatch."},
            },
            "search_around": {
                "desc": "Search nearby tide pools and rocks for another way in.",
                "result_scene": "secret_entrance",
            },
            "retreat": {
                "desc": "Return to the safety of the beach.",
                "result_scene": "intro",
            },
        },
    },
    "latch_fail": {
        "title": "A Jarring Turn",
        "desc": (
            "You yank the rusted latch without care. It grinds loudly, then jams with a sharp crack. "
            "The reef trembles and a cloud of startled fish explodes from below. "
            "From inside the lighthouse base, something heavy scrapes and stirs."
        ),
        "choices": {
            "run_away": {
                "desc": "Sprint back over the rocks toward the shore.",
                "result_scene": "intro",
            },
            "stand_ground": {
                "desc": "Stand your ground and face whatever rises from within.",
                "result_scene": "tower_combat",
            },
        },
    },
    "latch_open": {
        "title": "The Hatch Gives Way",
        "desc": (
            "Guided by the map's markings, you twist the latch in just the right way. "
            "It releases with a soft click, and the hatch lifts, exhaling a breath of cool, briny air. "
            "Inside, a narrow spiral of damp stone steps winds down below the reef, lit by a pale, underwater glow."
        ),
        "choices": {
            "descend": {
                "desc": "Descend the steps into the glowing depths beneath the reef.",
                "result_scene": "cellar",
            },
            "close_hatch": {
                "desc": "Close the hatch for now and reconsider your options.",
                "result_scene": "tower_approach",
            },
        },
    },
    "secret_entrance": {
        "title": "The Cracked Reef",
        "desc": (
            "Behind a jagged outcrop, you find a narrow crack in the reef, partially concealed by drifting kelp. "
            "A knotted rope disappears into the dark water below, smelling of old salt and cold iron. "
            "It looks like someone has used this way more than once."
        ),
        "choices": {
            "squeeze_in": {
                "desc": "Squeeze through the crack and follow the rope downward.",
                "result_scene": "cellar",
            },
            "mark_and_return": {
                "desc": "Mark the spot with a shell cairn and return to the beach.",
                "result_scene": "intro",
            },
        },
    },
    "cellar": {
        "title": "Grotto of Echoing Tides",
        "desc": (
            "The passage opens into a circular underwater grotto, though you somehow breathe with ease. "
            "Soft coral and glowing algae line the walls, casting shifting patterns of light. "
            "At the center stands a stone pedestal. On it rests a small brass key and a sealed coral scroll."
        ),
        "choices": {
            "take_key": {
                "desc": "Pick up the brass key from the pedestal.",
                "result_scene": "cellar_key",
                "effects": {
                    "add_inventory": "brass_key",
                    "add_journal": "Found brass key in the grotto.",
                },
            },
            "open_scroll": {
                "desc": "Break the coral seal and read the scroll.",
                "result_scene": "scroll_reveal",
                "effects": {
                    "add_journal": "Scroll reads: 'The tide remembers what the villagers forget.'"
                },
            },
            "leave_quietly": {
                "desc": "Leave the grotto and make your way back to the surface.",
                "result_scene": "intro",
            },
        },
    },
    "cellar_key": {
        "title": "Key of the Tides",
        "desc": (
            "As you lift the brass key, the coral lights dim and a hidden niche opens in the rock. "
            "Inside is a small statue of a sea spirit, its eyes pale blue. "
            "It hums softly and a gentle voice ripples through the water: 'Will you return what was taken from these shores?'"
        ),
        "choices": {
            "pledge_help": {
                "desc": "Pledge to return what was taken from the sea.",
                "result_scene": "reward",
                "effects": {"add_journal": "You pledged to return what was taken to the sea."},
            },
            "refuse": {
                "desc": "Refuse the request and pocket the key anyway.",
                "result_scene": "cursed_key",
                "effects": {
                    "add_journal": "You kept the key; a cold weight settles in your pocket."
                },
            },
        },
    },
    "scroll_reveal": {
        "title": "The Coral Scroll",
        "desc": (
            "The scroll tells of an heirloom locket stolen by a reef-dwelling creature that haunts the lighthouse base. "
            "It hints that the brass key 'speaks' when offered with honest intent in the presence of the spirit."
        ),
        "choices": {
            "search_for_key": {
                "desc": "Search the pedestal and grotto for a hidden key.",
                "result_scene": "cellar_key",
            },
            "leave_quietly": {
                "desc": "Leave the grotto, keeping the knowledge to yourself.",
                "result_scene": "intro",
            },
        },
    },
    "tower_combat": {
        "title": "Guardian of the Drowned Light",
        "desc": (
            "The hatch bursts open and a hunched, seaweed-draped creature drags itself out, water pouring from its scales. "
            "Its eyes glow like tide-lit lanterns, fixed on you with hungry curiosity. You have only a moment to act."
        ),
        "choices": {
            "fight": {
                "desc": "Stand your ground and fight the reef guardian.",
                "result_scene": "fight_win",
            },
            "flee": {
                "desc": "Turn and flee back over the rocks toward the shore.",
                "result_scene": "intro",
            },
        },
    },
    "fight_win": {
        "title": "After the Wave Breaks",
        "desc": (
            "With effort and instinct, you fend off the guardian. It tumbles back into the sea with a wounded cry, "
            "leaving behind only swirling foam. Among the wet stones, you find a small silver locket engraved with a crest—"
            "likely the heirloom mentioned in the scroll."
        ),
        "choices": {
            "take_locket": {
                "desc": "Take the locket and examine its engraving.",
                "result_scene": "reward",
                "effects": {
                    "add_inventory": "engraved_locket",
                    "add_journal": "Recovered an engraved silver locket from the reef guardian.",
                },
            },
            "leave_locket": {
                "desc": "Leave the locket where it lies and catch your breath.",
                "result_scene": "intro",
            },
        },
    },
    "reward": {
        "title": "Calm over the Shoals",
        "desc": (
            "A quiet calm settles over the island. The waves feel gentler, and distant lanterns in the fishing village seem to shine brighter. "
            "Whether you return the heirloom or keep it secret, the reef's restless song softens. "
            "You sense that this small chapter of your ocean journey has reached a gentle pause."
        ),
        "choices": {
            "end_session": {
                "desc": "End the session and return to the quiet beach (conclude mini-arc).",
                "result_scene": "intro",
            },
            "keep_exploring": {
                "desc": "Keep exploring the island and its surrounding waters.",
                "result_scene": "intro",
            },
        },
    },
    "cursed_key": {
        "title": "Weight of the Deep",
        "desc": (
            "The brass key grows cold and heavy in your hand. Each step you take seems to echo with the crash of distant waves. "
            "A lingering sorrow clings to you, as if the sea itself is waiting for a promise you refused to make."
        ),
        "choices": {
            "seek_redemption": {
                "desc": "Seek a way to make amends with the sea spirit.",
                "result_scene": "reward",
            },
            "bury_key": {
                "desc": "Bury the key in the sand and hope the weight fades.",
                "result_scene": "intro",
            },
        },
    },
    "cottages": {
        "title": "Stilted Village of Tidewalk",
        "desc": (
            "You arrive at Tidewalk, a small fishing village perched on wooden stilts above the lagoon. "
            "Lanterns sway gently, and a few early risers mend nets along the walkways. "
            "They glance at you with curiosity, whispering about strange lights near the old lighthouse."
        ),
        "choices": {
            "talk_to_fisher": {
                "desc": "Talk to a nearby fisher about the strange lights.",
                "result_scene": "intro",
                "effects": {
                    "add_journal": "Villagers fear the lights near the old reef lighthouse."
                },
            },
            "return_beach": {
                "desc": "Head back to the quiet beach to think.",
                "result_scene": "intro",
            },
        },
    },
}

# -------------------------
# Per-session Userdata
# -------------------------
@dataclass
class Userdata:
    player_name: Optional[str] = None
    current_scene: str = "intro"
    history: List[Dict] = field(default_factory=list)  # list of {'scene', 'action', 'time', 'result_scene'}
    journal: List[str] = field(default_factory=list)
    inventory: List[str] = field(default_factory=list)
    named_npcs: Dict[str, str] = field(default_factory=dict)
    choices_made: List[str] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

# -------------------------
# JSON SAVE HELPER
# -------------------------
def save_state_to_json(userdata: Userdata):
    """
    Save the current session state + current scene info into a JSON file.
    This does NOT change gameplay, only records it.
    """
    scene_key = userdata.current_scene or "intro"
    scene = WORLD.get(scene_key, {})
    state = {
        "session": asdict(userdata),
        "current_scene": {
            "key": scene_key,
            "title": scene.get("title"),
            "description": scene.get("desc"),
            "choices": scene.get("choices"),
        },
        "journal": userdata.journal,
        "inventory": userdata.inventory,
        "history": userdata.history,
        "last_updated_at": datetime.utcnow().isoformat() + "Z",
    }
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        logger.info(f"State saved to {STATE_FILE.resolve()}")
    except Exception as e:
        logger.warning(f"Failed to save state to JSON: {e}")

# -------------------------
# Helper functions
# -------------------------
def scene_text(scene_key: str, userdata: Userdata) -> str:
    """
    Build the descriptive text for the current scene, and append choices as short hints.
    Always end with 'What do you do?' so the voice flow prompts player input.
    """
    scene = WORLD.get(scene_key)
    if not scene:
        return "You are surrounded by open water and fog, unsure where you are. What do you do?"

    desc = f"{scene['desc']}\n\nChoices:\n"
    for cid, cmeta in scene.get("choices", {}).items():
        desc += f"- {cmeta['desc']} (say: {cid})\n"
    # GM MUST end with the action prompt
    desc += "\nWhat do you do?"
    return desc

def apply_effects(effects: dict, userdata: Userdata):
    if not effects:
        return
    if "add_journal" in effects:
        userdata.journal.append(effects["add_journal"])
    if "add_inventory" in effects:
        userdata.inventory.append(effects["add_inventory"])
    # Extendable for more effect keys

def summarize_scene_transition(old_scene: str, action_key: str, result_scene: str, userdata: Userdata) -> str:
    """Record the transition into history and return a short narrative the GM can use."""
    entry = {
        "from": old_scene,
        "action": action_key,
        "to": result_scene,
        "time": datetime.utcnow().isoformat() + "Z",
    }
    userdata.history.append(entry)
    userdata.choices_made.append(action_key)
    return f"You chose '{action_key}'."

# -------------------------
# Agent Tools (function_tool)
# -------------------------

@function_tool
async def start_adventure(
    ctx: RunContext[Userdata],
    player_name: Annotated[Optional[str], Field(description="Player name", default=None)] = None,
) -> str:
    """Initialize a new adventure session for the player and return the opening description."""
    userdata = ctx.userdata
    if player_name:
        userdata.player_name = player_name
    userdata.current_scene = "intro"
    userdata.history = []
    userdata.journal = []
    userdata.inventory = []
    userdata.named_npcs = {}
    userdata.choices_made = []
    userdata.session_id = str(uuid.uuid4())[:8]
    userdata.started_at = datetime.utcnow().isoformat() + "Z"

    # save JSON state at session start
    save_state_to_json(userdata)

    opening = (
        f"Greetings {userdata.player_name or 'traveler'}. "
        f"Welcome to '{WORLD['intro']['title']}', a small tale amid the endless ocean.\n\n"
        + scene_text("intro", userdata)
    )
    # Ensure GM prompt present
    if not opening.endswith("What do you do?"):
        opening += "\nWhat do you do?"
    return opening

@function_tool
async def get_scene(
    ctx: RunContext[Userdata],
) -> str:
    """Return the current scene description (useful for 'remind me where I am')."""
    userdata = ctx.userdata
    scene_k = userdata.current_scene or "intro"
    # optional: save state here too (so latest scene stays in JSON)
    save_state_to_json(userdata)
    txt = scene_text(scene_k, userdata)
    return txt

@function_tool
async def player_action(
    ctx: RunContext[Userdata],
    action: Annotated[str, Field(description="Player spoken action or the short action code (e.g., 'inspect_box' or 'take the box')")],
) -> str:
    """
    Accept player's action (natural language or action key), try to resolve it to a defined choice,
    update userdata, advance to the next scene and return the GM's next description (ending with 'What do you do?').
    """
    userdata = ctx.userdata
    current = userdata.current_scene or "intro"
    scene = WORLD.get(current)
    action_text = (action or "").strip()

    # Attempt 1: match exact action key (e.g., 'inspect_box')
    chosen_key = None
    if action_text.lower() in (scene.get("choices") or {}):
        chosen_key = action_text.lower()

    # Attempt 2: fuzzy match by checking if action_text contains the choice key or descriptive words
    if not chosen_key:
        # try to find a choice whose description words appear in action_text
        for cid, cmeta in (scene.get("choices") or {}).items():
            desc = cmeta.get("desc", "").lower()
            if cid in action_text.lower() or any(w in action_text.lower() for w in desc.split()[:4]):
                chosen_key = cid
                break

    # Attempt 3: fallback by simple keyword matching against choice descriptions
    if not chosen_key:
        for cid, cmeta in (scene.get("choices") or {}).items():
            for keyword in cmeta.get("desc", "").lower().split():
                if keyword and keyword in action_text.lower():
                    chosen_key = cid
                    break
            if chosen_key:
                break

    if not chosen_key:
        # If we still can't resolve, ask a clarifying GM response but keep it short and end with prompt.
        resp = (
            "I didn't quite catch that action for this part of the island. "
            "Try one of the listed choices, or use a simple phrase like "
            "'inspect the box', 'go to the lighthouse', or 'walk to the village'.\n\n"
            + scene_text(current, userdata)
        )
        return resp

    # Apply the chosen choice
    choice_meta = scene["choices"].get(chosen_key)
    result_scene = choice_meta.get("result_scene", current)
    effects = choice_meta.get("effects", None)

    # Apply effects (inventory/journal, etc.)
    apply_effects(effects or {}, userdata)

    # Record transition
    _note = summarize_scene_transition(current, chosen_key, result_scene, userdata)

    # Update current scene
    userdata.current_scene = result_scene

    # save JSON state after each action
    save_state_to_json(userdata)

    # Build narrative reply: echo a short confirmation, then describe next scene
    next_desc = scene_text(result_scene, userdata)

    # A small flourish so the GM sounds more persona-driven
    persona_pre = (
        "The Game Master, speaking in a calm, ocean-worn voice, replies:\n\n"
    )
    reply = f"{persona_pre}{_note}\n\n{next_desc}"
    # ensure final prompt present
    if not reply.endswith("What do you do?"):
        reply += "\nWhat do you do?"
    return reply

@function_tool
async def show_journal(
    ctx: RunContext[Userdata],
) -> str:
    userdata = ctx.userdata
    lines = []
    lines.append(f"Session: {userdata.session_id} | Started at: {userdata.started_at}")
    if userdata.player_name:
        lines.append(f"Player: {userdata.player_name}")
    if userdata.journal:
        lines.append("\nJournal entries:")
        for j in userdata.journal:
            lines.append(f"- {j}")
    else:
        lines.append("\nJournal is empty.")
    if userdata.inventory:
        lines.append("\nInventory:")
        for it in userdata.inventory:
            lines.append(f"- {it}")
    else:
        lines.append("\nNo items in inventory.")
    lines.append("\nRecent choices:")
    for h in userdata.history[-6:]:
        lines.append(f"- {h['time']} | from {h['from']} -> {h['to']} via {h['action']}")
    lines.append("\nWhat do you do?")

    # save JSON state when journal is requested
    save_state_to_json(userdata)

    return "\n".join(lines)

@function_tool
async def restart_adventure(
    ctx: RunContext[Userdata],
) -> str:
    """Reset the userdata and start again."""
    userdata = ctx.userdata
    userdata.current_scene = "intro"
    userdata.history = []
    userdata.journal = []
    userdata.inventory = []
    userdata.named_npcs = {}
    userdata.choices_made = []
    userdata.session_id = str(uuid.uuid4())[:8]
    userdata.started_at = datetime.utcnow().isoformat() + "Z"

    # save JSON state after reset
    save_state_to_json(userdata)

    greeting = (
        "The tides shift, and the island rewinds to the beginning. "
        "You find yourself once more on the quiet shore as dawn approaches.\n\n"
        + scene_text("intro", userdata)
    )
    if not greeting.endswith("What do you do?"):
        greeting += "\nWhat do you do?"
    return greeting

# -------------------------
# The Agent (GameMasterAgent)
# -------------------------
class GameMasterAgent(Agent):
    def __init__(self):
        # System instructions define Universe, Tone, Role
        instructions = """
        You are 'Alica', the Game Master (GM) for a voice-only, short ocean-fantasy adventure.
        Ask for the name of user first
        Universe: Low-magic ocean world of small islands and reefs (glowing tides, fishing villages, water spirits).
        Tone: Slightly mysterious, gentle, and empathetic (not overly scary), with a sense of quiet wonder.
        Role: You are the GM. You describe scenes vividly, remember the player's past choices, named NPCs, inventory and locations,
              and you always end your descriptive messages with the prompt: 'What do you do?'
        Rules:
            - Use the provided tools to start the adventure, get the current scene, accept the player's spoken action,
              show the player's journal, or restart the adventure.
            - Keep continuity using the per-session userdata. Reference journal items and inventory when relevant.
            - Keep the story grounded in the ocean/island setting: shores, reefs, lighthouses, villages on stilts, and underwater grottoes.
            - Drive short sessions (aim for several meaningful turns). Each GM message MUST end with 'What do you do?'.
            - Respect that this agent is voice-first: responses should be concise enough for spoken delivery but still evocative.
        """
        super().__init__(
            instructions=instructions,
            tools=[start_adventure, get_scene, player_action, show_journal, restart_adventure],
        )

# -------------------------
# Entrypoint & Prewarm (keeps speech functionality)
# -------------------------
def prewarm(proc: JobProcess):
    # load VAD model and stash on process userdata, try/catch like original file
    try:
        proc.userdata["vad"] = silero.VAD.load()
    except Exception:
        logger.warning("VAD prewarm failed; continuing without preloaded VAD.")

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    logger.info("\n" + "🌊" * 8)
    logger.info("🚀 STARTING VOICE GAME MASTER (Ocean Mini-Arc)")

    userdata = Userdata()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-alicia",
            style="Conversational",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata.get("vad"),
        userdata=userdata,
    )

    # Start the agent session with the GameMasterAgent
    await session.start(
        agent=GameMasterAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
