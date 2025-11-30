
#------------------------------------------------
# Day8  E-COMMERCE
#------------------------------------------------


import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# ---------------------------
# Simple E-commerce Data Layer
# ---------------------------

# Static product catalog (ACP-inspired, but simple)
PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": "mug-001",
        "name": "Stoneware Coffee Mug",
        "description": "A sturdy stoneware mug for your daily coffee.",
        "price": 499,
        "currency": "INR",
        "category": "mug",
        "color": "white",
        "sizes": [],
    },
    {
        "id": "mug-002",
        "name": "Travel Coffee Tumbler",
        "description": "Insulated stainless steel tumbler, keeps drinks hot for 6 hours.",
        "price": 899,
        "currency": "INR",
        "category": "mug",
        "color": "black",
        "sizes": [],
    },
    {
        "id": "tee-001",
        "name": "Classic Logo T-Shirt",
        "description": "Soft cotton t-shirt with printed logo.",
        "price": 799,
        "currency": "INR",
        "category": "tshirt",
        "color": "black",
        "sizes": ["S", "M", "L", "XL"],
    },
    {
        "id": "tee-002",
        "name": "Minimalist White T-Shirt",
        "description": "Plain white t-shirt, regular fit.",
        "price": 599,
        "currency": "INR",
        "category": "tshirt",
        "color": "white",
        "sizes": ["S", "M", "L", "XL"],
    },
    {
        "id": "hoodie-001",
        "name": "Black Zip Hoodie",
        "description": "Cozy black zip hoodie with pockets.",
        "price": 1499,
        "currency": "INR",
        "category": "hoodie",
        "color": "black",
        "sizes": ["S", "M", "L", "XL"],
    },
    {
        "id": "hoodie-002",
        "name": "Blue Pullover Hoodie",
        "description": "Soft blue pullover hoodie for everyday wear.",
        "price": 1399,
        "currency": "INR",
        "category": "hoodie",
        "color": "blue",
        "sizes": ["M", "L", "XL"],
    },
    {
        "id": "cap-001",
        "name": "Adjustable Baseball Cap",
        "description": "Casual cotton cap with adjustable strap.",
        "price": 499,
        "currency": "INR",
        "category": "cap",
        "color": "black",
        "sizes": [],
    },
    {
        "id": "bag-001",
        "name": "Canvas Tote Bag",
        "description": "Reusable canvas tote bag for everyday use.",
        "price": 399,
        "currency": "INR",
        "category": "bag",
        "color": "beige",
        "sizes": [],
    },
]

ORDERS_FILE = Path("orders.json")
ORDERS: List[Dict[str, Any]] = []


def _load_orders_from_file() -> None:
    """Load existing orders from orders.json, if present."""
    global ORDERS
    if ORDERS_FILE.exists():
        try:
            with ORDERS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                ORDERS = data
            else:
                ORDERS = []
        except Exception as e:
            logger.warning(f"Failed to load orders.json: {e}")
            ORDERS = []
    else:
        ORDERS = []


def _save_orders_to_file() -> None:
    """Persist all orders to orders.json."""
    try:
        with ORDERS_FILE.open("w", encoding="utf-8") as f:
            json.dump(ORDERS, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save orders.json: {e}")


def list_products_backend(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    color: Optional[str] = None,
    name_query: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filter the product list using simple criteria.
    All filters are optional and combined with AND logic.
    """
    results = []
    for p in PRODUCTS:
        # Category filter
        if category and p.get("category", "").lower() != category.lower():
            continue

        # Max price filter
        if max_price is not None and float(p.get("price", 0)) > float(max_price):
            continue

        # Color filter
        if color and p.get("color", "").lower() != color.lower():
            continue

        # Name / description contains substring
        if name_query:
            nq = name_query.lower()
            if nq not in p.get("name", "").lower() and nq not in p.get("description", "").lower():
                continue

        results.append(p)

    return results


def create_order_backend(
    line_items: List[Dict[str, Any]],
    currency: str = "INR",
) -> Dict[str, Any]:
    """
    Create an order from a list of line items:
    line_items: [{ "product_id": "...", "quantity": 1, "size": "M" (optional) }, ...]

    Returns a full order dict:
    {
      "id": "...",
      "items": [...],
      "total": 0,
      "currency": "INR",
      "created_at": "ISO timestamp"
    }
    """
    if not line_items:
        raise ValueError("line_items cannot be empty")

    items: List[Dict[str, Any]] = []
    total = 0.0

    product_map = {p["id"]: p for p in PRODUCTS}

    for li in line_items:
        product_id = li.get("product_id")
        quantity = int(li.get("quantity", 1))
        size = li.get("size")  # Optional

        if not product_id or product_id not in product_map:
            raise ValueError(f"Invalid product_id: {product_id}")

        product = product_map[product_id]
        unit_price = float(product["price"])
        line_total = unit_price * quantity
        total += line_total

        items.append(
            {
                "product_id": product_id,
                "name": product["name"],
                "quantity": quantity,
                "unit_amount": unit_price,
                "line_total": line_total,
                "currency": product["currency"],
                "size": size,
            }
        )

    order = {
        "id": str(uuid.uuid4()),
        "items": items,
        "total": total,
        "currency": currency,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    ORDERS.append(order)
    _save_orders_to_file()
    return order


def get_last_order_backend() -> Optional[Dict[str, Any]]:
    """Return the most recent order, or None if no orders exist."""
    if not ORDERS:
        return None
    return ORDERS[-1]


# ---------------------------
# Agent Definition + Tools
# ---------------------------


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "Instroduce your self You are a SwiftCart voice shopping assistant for a small e-commerce store." \
                "ake for name of user "
                
                "You can browse a catalog of products (mugs, t-shirts, hoodies, caps, bags) and create orders. "
                "Always use the available tools to:\n"
                "- List or filter products from the catalog.\n"
                "- Create orders when the user wants to buy something.\n"
                "- Fetch the most recent order when the user asks what they bought.\n\n"
                "Behaviour guidelines:\n"
                "- When the user asks about products (e.g. 'show me all hoodies', "
                "'do you have t-shirts under 1000', 'black hoodie', 'blue mug'), "
                "call the product listing tool with appropriate filters and then summarize a few relevant products "
                "with their name, price, and product ID.\n"
                "- When the user wants to buy, ask clarifying questions if anything is ambiguous (size, color, quantity), "
                "then call the order creation tool. After creating the order, clearly confirm the order ID, products, "
                "sizes, quantities, and total amount.\n"
                "- When the user asks things like 'what did I just buy?' or 'what was my last order?', "
                "use the last-order tool and summarize the most recent order.\n"
                "- Be concise and friendly. Do NOT use markdown, emojis, or any special formatting."
            )
        )

    # ---------------------------
    # Tools exposed to the LLM
    # ---------------------------

    @function_tool
    async def list_products(
        self,
        context: RunContext,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        color: Optional[str] = None,
        name_query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        

        


        Args:
            category: Optional product category (e.g. "mug", "tshirt", "hoodie", "cap", "bag").
            max_price: Optional max price in INR.
            color: Optional exact color filter (e.g. "black", "white", "blue").
            name_query: Optional free text search term for product name/description.

        Returns:
            A list of product dicts with fields like:
            id, name, description, price, currency, category, color, sizes.
        """
        logger.info(
            f"Listing products with filters: "
            f"category={category}, max_price={max_price}, color={color}, name_query={name_query}"
        )
        return list_products_backend(
            category=category,
            max_price=max_price,
            color=color,
            name_query=name_query,
        )

    @function_tool
    async def create_order(
        self,
        context: RunContext,
        line_items: List[Dict[str, Any]],
        currency: str = "INR",
    ) -> Dict[str, Any]:
        """
        Create an order from selected products.

        The LLM should call this when the user confirms they want to buy.
        For example:
        - "I'll buy the second hoodie you mentioned in size M."
        - "Add 2 of the black t-shirt in size L."

        Args:
            line_items: A list of line items. Each line item should include:
                - product_id: ID of the product (string).
                - quantity: Integer quantity (default 1 if omitted).
                - size: Optional size (e.g. "S", "M", "L", "XL"), only for wearable items.
            currency: Currency code, default "INR".

        Returns:
            An order object with fields:
            - id: Generated order ID.
            - items: List of line items with product details.
            - total: Total price.
            - currency: Currency code.
            - created_at: ISO timestamp string.
        """
        logger.info(f"Creating order with line_items={line_items}, currency={currency}")
        order = create_order_backend(line_items=line_items, currency=currency)
        logger.info(f"Created order {order['id']}")
        return order

    @function_tool
    async def get_last_order(
        self,
        context: RunContext,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch the most recent order that was created.

        Use this when the user asks questions like:
        - "What did I just buy?"
        - "What was my last order?"
        - "Can you remind me what I ordered?"

        Returns:
            The most recent order dict (same shape as create_order result),
            or null if there are no orders yet.
        """
        logger.info("Fetching last order")
        return get_last_order_backend()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    # Load persisted orders when the worker starts
    _load_orders_from_file()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Voice AI pipeline using Deepgram STT, Google LLM, Murf TTS
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(
            model="gemini-2.5-flash",
        ),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Metrics
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session with our shopping Assistant
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
