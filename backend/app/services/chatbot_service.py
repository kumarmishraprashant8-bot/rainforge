"""
WhatsApp Chatbot Service
Dialogflow / Rasa integration for conversational AI
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    """Recognized user intents."""
    GREETING = "greeting"
    CHECK_TANK = "check_tank"
    CHECK_WEATHER = "check_weather"
    CHECK_PAYMENT = "check_payment"
    BOOK_INSTALLER = "book_installer"
    GET_QUOTE = "get_quote"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class ChatMessage:
    """Chat message structure."""
    user_id: str
    text: str
    intent: Intent
    entities: Dict[str, Any]
    confidence: float
    timestamp: datetime


@dataclass
class BotResponse:
    """Bot response structure."""
    text: str
    quick_replies: Optional[List[str]] = None
    buttons: Optional[List[Dict]] = None
    media_url: Optional[str] = None


class ChatbotService:
    """
    Conversational AI chatbot for RainForge.
    
    Supports:
    - Rule-based intent matching
    - Dialogflow integration (optional)
    - Multi-turn conversations
    - Quick actions
    """
    
    # Intent patterns (regex-based for rule matching)
    PATTERNS = {
        Intent.GREETING: [
            r'\b(hi|hello|hey|namaste|good morning|good evening)\b',
            r'^(hi|hey|hello)$'
        ],
        Intent.CHECK_TANK: [
            r'\b(tank|level|water level|kitna pani|storage)\b',
            r'\b(check|show|what is).*(tank|level)\b'
        ],
        Intent.CHECK_WEATHER: [
            r'\b(weather|rain|forecast|barish|mausam)\b',
            r'\b(will it rain|kya barish hogi)\b'
        ],
        Intent.CHECK_PAYMENT: [
            r'\b(payment|paisa|money|bill|invoice)\b',
            r'\b(pending|due|status).*(payment)\b'
        ],
        Intent.BOOK_INSTALLER: [
            r'\b(installer|book|install|lagwana|technician)\b',
            r'\b(find|need|want).*(installer)\b'
        ],
        Intent.GET_QUOTE: [
            r'\b(quote|quotation|price|cost|kitna lagega)\b',
            r'\b(how much|estimate|budget)\b'
        ],
        Intent.HELP: [
            r'\b(help|support|assist|madad|problem)\b',
            r'^(help|help me)$'
        ]
    }
    
    # Response templates
    RESPONSES = {
        Intent.GREETING: [
            "🌧️ Namaste! Welcome to RainForge. How can I help you today?",
            "Hello! I'm your RainForge assistant. What would you like to know?"
        ],
        Intent.CHECK_TANK: [
            "📊 Let me check your tank level... Your tank is at {level}%.",
            "🛢️ Your current tank status:\n• Level: {level}%\n• Status: {status}"
        ],
        Intent.CHECK_WEATHER: [
            "🌤️ Today's weather:\n• Temperature: {temp}°C\n• Rain chance: {rain_chance}%\n• {condition}",
            "🌧️ Rainfall forecast:\n{forecast}"
        ],
        Intent.CHECK_PAYMENT: [
            "💰 Your payment status:\n• Pending: ₹{pending}\n• Last payment: ₹{last_amount} on {last_date}"
        ],
        Intent.BOOK_INSTALLER: [
            "🔧 I'll help you find an installer. Please share your location or pin code.",
            "Looking for verified installers in your area..."
        ],
        Intent.GET_QUOTE: [
            "📋 To get a quote, I need:\n1️⃣ Your roof area (sq ft)\n2️⃣ Building type\n3️⃣ Location\n\nPlease share your roof area first."
        ],
        Intent.HELP: [
            "📚 I can help you with:\n1️⃣ Check tank level\n2️⃣ Weather forecast\n3️⃣ Payment status\n4️⃣ Book installer\n5️⃣ Get a quote\n\nJust type what you need!"
        ],
        Intent.UNKNOWN: [
            "I'm not sure I understand. Try asking about:\n• Tank level\n• Weather\n• Payments\n• Installers\n\nOr type 'help' for more options."
        ]
    }
    
    def __init__(self):
        self._sessions: Dict[str, Dict] = {}  # User conversation sessions
        self._dialogflow_client = None  # Optional Dialogflow integration
    
    async def process_message(
        self,
        user_id: str,
        message_text: str,
        context: Optional[Dict] = None
    ) -> BotResponse:
        """
        Process incoming message and generate response.
        """
        # Get or create session
        session = self._get_session(user_id)
        
        # Parse message
        intent, entities, confidence = self._parse_intent(message_text)
        
        # Log message
        chat_msg = ChatMessage(
            user_id=user_id,
            text=message_text,
            intent=intent,
            entities=entities,
            confidence=confidence,
            timestamp=datetime.utcnow()
        )
        session["history"].append(chat_msg)
        
        # Generate response based on intent
        response = await self._generate_response(intent, entities, user_id, session)
        
        return response
    
    def _parse_intent(self, text: str) -> Tuple[Intent, Dict, float]:
        """Parse user intent from message text."""
        text_lower = text.lower().strip()
        
        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    entities = self._extract_entities(text_lower, intent)
                    return intent, entities, 0.85
        
        return Intent.UNKNOWN, {}, 0.3
    
    def _extract_entities(self, text: str, intent: Intent) -> Dict:
        """Extract entities from message."""
        entities = {}
        
        # Extract numbers
        numbers = re.findall(r'\d+', text)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]
        
        # Extract locations (pin codes)
        pin_code = re.search(r'\b\d{6}\b', text)
        if pin_code:
            entities["pin_code"] = pin_code.group()
        
        # Extract roof area mentions
        area_match = re.search(r'(\d+)\s*(sq\s*ft|sqft|square feet|sqm)', text)
        if area_match:
            entities["roof_area"] = int(area_match.group(1))
            entities["area_unit"] = "sqft" if "ft" in area_match.group(2) else "sqm"
        
        return entities
    
    async def _generate_response(
        self,
        intent: Intent,
        entities: Dict,
        user_id: str,
        session: Dict
    ) -> BotResponse:
        """Generate response based on intent."""
        import random
        
        templates = self.RESPONSES.get(intent, self.RESPONSES[Intent.UNKNOWN])
        template = random.choice(templates)
        
        # Fill in template with real data if available
        response_text = template
        quick_replies = None
        
        if intent == Intent.CHECK_TANK:
            # Get real tank data (mock for now)
            level, status = await self._get_tank_data(user_id)
            response_text = template.format(level=level, status=status)
            quick_replies = ["🔄 Refresh", "📊 History", "🔔 Set Alert"]
        
        elif intent == Intent.CHECK_WEATHER:
            # Get weather data (mock for now)
            weather = await self._get_weather_data(user_id)
            response_text = template.format(**weather)
            quick_replies = ["📅 7-day forecast", "🌧️ Rain alerts"]
        
        elif intent == Intent.GREETING:
            quick_replies = ["🛢️ Tank Level", "🌧️ Weather", "💰 Payments", "🔧 Book Installer"]
        
        elif intent == Intent.HELP:
            quick_replies = ["Tank Level", "Weather", "Payment Status", "Get Quote"]
        
        elif intent == Intent.GET_QUOTE:
            session["context"] = {"flow": "quote", "step": "roof_area"}
        
        return BotResponse(
            text=response_text,
            quick_replies=quick_replies
        )
    
    async def _get_tank_data(self, user_id: str) -> Tuple[float, str]:
        """Get tank data for user (placeholder)."""
        # In production, would query actual tank sensor data
        import random
        level = random.uniform(30, 90)
        status = "Low" if level < 30 else "Full" if level > 80 else "Normal"
        return round(level, 1), status
    
    async def _get_weather_data(self, user_id: str) -> Dict:
        """Get weather data for user location (placeholder)."""
        return {
            "temp": 28,
            "rain_chance": 60,
            "condition": "Partly cloudy with chance of rain",
            "forecast": "Tomorrow: 🌧️ 80% rain expected\nDay after: ☀️ Sunny"
        }
    
    def _get_session(self, user_id: str) -> Dict:
        """Get or create user session."""
        if user_id not in self._sessions:
            self._sessions[user_id] = {
                "user_id": user_id,
                "started_at": datetime.utcnow(),
                "context": {},
                "history": []
            }
        return self._sessions[user_id]
    
    def get_quick_actions(self) -> List[Dict]:
        """Get list of quick actions for UI."""
        return [
            {"id": "tank", "label": "🛢️ Tank Level", "action": "check tank"},
            {"id": "weather", "label": "🌧️ Weather", "action": "weather forecast"},
            {"id": "payment", "label": "💰 Payments", "action": "payment status"},
            {"id": "installer", "label": "🔧 Installer", "action": "book installer"},
            {"id": "quote", "label": "📋 Quote", "action": "get quote"},
            {"id": "help", "label": "❓ Help", "action": "help"}
        ]


# Singleton
_chatbot: Optional[ChatbotService] = None

def get_chatbot_service() -> ChatbotService:
    global _chatbot
    if _chatbot is None:
        _chatbot = ChatbotService()
    return _chatbot
