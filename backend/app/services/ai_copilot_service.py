"""
AI Copilot Service
GPT-4 powered intelligent assistant for rainwater harvesting.

Features:
- Natural language assessment queries
- Document parsing and extraction
- Proactive recommendations
- Multi-lingual support (Hindi, Tamil, Telugu, etc.)
- Context-aware responses
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import re

logger = logging.getLogger(__name__)


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    MARATHI = "mr"
    BENGALI = "bn"
    GUJARATI = "gu"


class IntentType(str, Enum):
    """Detected user intent."""
    ASSESSMENT_QUERY = "assessment_query"
    SUBSIDY_INFO = "subsidy_info"
    INSTALLER_SEARCH = "installer_search"
    MAINTENANCE_HELP = "maintenance_help"
    GENERAL_INFO = "general_info"
    PROJECT_STATUS = "project_status"
    DOCUMENT_HELP = "document_help"
    COMPLAINT = "complaint"
    UNKNOWN = "unknown"


@dataclass
class ConversationContext:
    """Context for ongoing conversation."""
    user_id: str
    session_id: str
    current_page: Optional[str] = None
    project_id: Optional[int] = None
    language: Language = Language.ENGLISH
    previous_intents: List[IntentType] = field(default_factory=list)
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    messages: List[Dict] = field(default_factory=list)


@dataclass
class CopilotResponse:
    """AI Copilot response."""
    message: str
    intent: IntentType
    confidence: float
    suggestions: List[str] = field(default_factory=list)
    actions: List[Dict] = field(default_factory=list)
    data: Optional[Dict] = None
    follow_up_questions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "message": self.message,
            "intent": self.intent.value,
            "confidence": self.confidence,
            "suggestions": self.suggestions,
            "actions": self.actions,
            "data": self.data,
            "follow_up_questions": self.follow_up_questions
        }


@dataclass
class ExtractedDocumentData:
    """Data extracted from uploaded document."""
    document_type: str
    confidence: float
    extracted_fields: Dict[str, Any]
    raw_text: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "document_type": self.document_type,
            "confidence": self.confidence,
            "fields": self.extracted_fields
        }


class AICopilotService:
    """
    AI-powered assistant for RainForge platform.
    
    Features:
    - Natural language understanding for RWH queries
    - Document OCR and data extraction
    - Proactive maintenance recommendations
    - Multi-lingual support
    
    Note: Mock implementation using rule-based NLU.
    Production would integrate with GPT-4/Claude API.
    """
    
    def __init__(self):
        self._sessions: Dict[str, ConversationContext] = {}
        
        # Intent patterns (regex-based for demo)
        self._intent_patterns = {
            IntentType.ASSESSMENT_QUERY: [
                r"(water|rain|rwh|rainwater|harvest)",
                r"(potential|capacity|how much|estimate)",
                r"(roof|terrace|building|house)",
                r"(sqft|sq\s*ft|square\s*feet|area)"
            ],
            IntentType.SUBSIDY_INFO: [
                r"(subsidy|grant|scheme|government|sarkari)",
                r"(eligible|eligibility|apply|application)",
                r"(jal shakti|amrut|pmay)"
            ],
            IntentType.INSTALLER_SEARCH: [
                r"(installer|contractor|vendor|plumber)",
                r"(install|setup|build|construct)",
                r"(find|search|recommend|best)"
            ],
            IntentType.MAINTENANCE_HELP: [
                r"(maintain|maintenance|clean|filter)",
                r"(problem|issue|broken|leak|not working)",
                r"(repair|fix|service)"
            ],
            IntentType.PROJECT_STATUS: [
                r"(status|progress|update|where)",
                r"(my project|my application|my rwh)"
            ],
            IntentType.COMPLAINT: [
                r"(complaint|grievance|problem|issue)",
                r"(report|file|lodge)"
            ]
        }
        
        # City rainfall data for assessments
        self._city_rainfall = {
            "mumbai": 2400, "delhi": 800, "bangalore": 970,
            "chennai": 1400, "hyderabad": 800, "kolkata": 1600,
            "jaipur": 650, "lucknow": 1000, "pune": 750,
            "ahmedabad": 800, "bhopal": 1200, "indore": 1000
        }
        
        # Multilingual responses
        self._translations = {
            Language.HINDI: {
                "greeting": "नमस्ते! मैं RainForge AI सहायक हूं। मैं आपकी कैसे मदद कर सकता हूं?",
                "assessment_intro": "आपके छत की क्षमता के बारे में जानकारी:",
                "subsidy_intro": "आप इन सरकारी योजनाओं के लिए पात्र हो सकते हैं:"
            },
            Language.TAMIL: {
                "greeting": "வணக்கம்! நான் RainForge AI உதவியாளர். நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
                "assessment_intro": "உங்கள் கூரை திறன் பற்றிய தகவல்:"
            }
        }
        
        logger.info("🤖 AI Copilot Service initialized")
    
    # ==================== CHAT ====================
    
    async def chat(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process chat message and generate response.
        
        Args:
            user_id: User identifier
            message: User's message
            session_id: Conversation session ID
            context: Additional context (current page, project, etc.)
        """
        # Get or create session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationContext(
                user_id=user_id,
                session_id=session_id
            )
        
        conv = self._sessions[session_id]
        
        # Update context
        if context:
            conv.current_page = context.get("page")
            conv.project_id = context.get("project_id")
            if context.get("language"):
                conv.language = Language(context["language"])
        
        # Detect language
        detected_lang = self._detect_language(message)
        if detected_lang != Language.ENGLISH:
            conv.language = detected_lang
        
        # Store message
        conv.messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Detect intent
        intent, confidence = self._detect_intent(message)
        conv.previous_intents.append(intent)
        
        # Extract entities
        entities = self._extract_entities(message)
        conv.extracted_entities.update(entities)
        
        # Generate response based on intent
        response = await self._generate_response(conv, message, intent, entities)
        
        # Store assistant message
        conv.messages.append({
            "role": "assistant",
            "content": response.message,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "response": response.to_dict()
        }
    
    def _detect_language(self, text: str) -> Language:
        """Detect language of input text."""
        # Simple detection based on Unicode ranges
        hindi_pattern = re.compile(r'[\u0900-\u097F]')
        tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')
        telugu_pattern = re.compile(r'[\u0C00-\u0C7F]')
        
        if hindi_pattern.search(text):
            return Language.HINDI
        elif tamil_pattern.search(text):
            return Language.TAMIL
        elif telugu_pattern.search(text):
            return Language.TELUGU
        
        return Language.ENGLISH
    
    def _detect_intent(self, message: str) -> tuple[IntentType, float]:
        """Detect user intent from message."""
        message_lower = message.lower()
        
        intent_scores = {}
        
        for intent, patterns in self._intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            if score > 0:
                intent_scores[intent] = score / len(patterns)
        
        if not intent_scores:
            return IntentType.GENERAL_INFO, 0.5
        
        best_intent = max(intent_scores, key=intent_scores.get)
        return best_intent, min(intent_scores[best_intent] * 1.5, 0.95)
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from message."""
        entities = {}
        message_lower = message.lower()
        
        # Extract area (sqft)
        area_match = re.search(r'(\d+)\s*(sqft|sq\s*ft|square\s*feet)', message_lower)
        if area_match:
            entities["roof_area_sqft"] = int(area_match.group(1))
        
        # Extract city
        for city in self._city_rainfall.keys():
            if city in message_lower:
                entities["city"] = city.title()
                entities["annual_rainfall_mm"] = self._city_rainfall[city]
                break
        
        # Extract budget
        budget_match = re.search(r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(lakh|lac|k|thousand)?', message_lower)
        if budget_match:
            amount = float(budget_match.group(1).replace(',', ''))
            multiplier = budget_match.group(2)
            if multiplier in ['lakh', 'lac']:
                amount *= 100000
            elif multiplier == 'k':
                amount *= 1000
            elif multiplier == 'thousand':
                amount *= 1000
            entities["budget"] = amount
        
        return entities
    
    async def _generate_response(
        self,
        conv: ConversationContext,
        message: str,
        intent: IntentType,
        entities: Dict
    ) -> CopilotResponse:
        """Generate response based on intent and context."""
        
        if intent == IntentType.ASSESSMENT_QUERY:
            return await self._handle_assessment_query(conv, entities)
        
        elif intent == IntentType.SUBSIDY_INFO:
            return self._handle_subsidy_query(conv, entities)
        
        elif intent == IntentType.INSTALLER_SEARCH:
            return self._handle_installer_query(conv, entities)
        
        elif intent == IntentType.MAINTENANCE_HELP:
            return self._handle_maintenance_query(conv, entities)
        
        elif intent == IntentType.PROJECT_STATUS:
            return self._handle_status_query(conv)
        
        elif intent == IntentType.COMPLAINT:
            return self._handle_complaint(conv, message)
        
        else:
            return self._handle_general_query(conv, message)
    
    async def _handle_assessment_query(
        self,
        conv: ConversationContext,
        entities: Dict
    ) -> CopilotResponse:
        """Handle rainwater harvesting assessment queries."""
        
        roof_area = entities.get("roof_area_sqft") or conv.extracted_entities.get("roof_area_sqft")
        city = entities.get("city") or conv.extracted_entities.get("city")
        rainfall = entities.get("annual_rainfall_mm") or conv.extracted_entities.get("annual_rainfall_mm", 800)
        
        if not roof_area:
            return CopilotResponse(
                message="I'd love to help you estimate your rainwater harvesting potential! 🌧️\n\nCould you please tell me:\n1. What's your roof/terrace area in square feet?\n2. Which city are you in?",
                intent=IntentType.ASSESSMENT_QUERY,
                confidence=0.9,
                suggestions=["My roof is 1000 sqft", "I'm in Mumbai", "Check my property documents"],
                follow_up_questions=["What's your roof area?", "Which city?"]
            )
        
        # Calculate potential
        roof_area_sqm = roof_area * 0.0929  # sqft to sqm
        runoff_coefficient = 0.85
        annual_potential_liters = roof_area_sqm * rainfall * runoff_coefficient
        monthly_potential = annual_potential_liters / 12
        
        # Calculate tank size recommendation
        recommended_tank = min(monthly_potential * 0.3, 20000)  # 30% of monthly, max 20k liters
        
        # Calculate savings
        water_cost_per_kl = 45  # Average municipal rate
        annual_savings = (annual_potential_liters / 1000) * water_cost_per_kl
        
        # Calculate CO2 offset
        co2_per_kl = 0.7  # kg CO2 per kL of water saved
        annual_co2 = (annual_potential_liters / 1000) * co2_per_kl
        
        city_text = f" in {city}" if city else ""
        
        response_message = f"""🌧️ **Your Rainwater Harvesting Potential{city_text}**

Based on your {roof_area:,} sq ft roof:

📊 **Annual Collection Potential**
• **{annual_potential_liters:,.0f} liters/year** ({annual_potential_liters/1000:.1f} kL)
• Monthly average: {monthly_potential:,.0f} liters

💧 **Recommended System**
• Tank Size: **{recommended_tank:,.0f} liters**
• Type: Underground sump or overhead tank
• Estimated Cost: ₹{int(recommended_tank * 2.5):,} - ₹{int(recommended_tank * 4):,}

💰 **Savings & Impact**
• Annual water bill savings: **₹{annual_savings:,.0f}**
• CO₂ offset: {annual_co2:.0f} kg/year
• ROI Period: ~3-4 years

Would you like me to:
1. 🔍 Find verified installers in your area
2. 📋 Check subsidy eligibility
3. 📐 Get a detailed assessment"""
        
        return CopilotResponse(
            message=response_message,
            intent=IntentType.ASSESSMENT_QUERY,
            confidence=0.95,
            suggestions=[
                "Find installers near me",
                "Check subsidy options",
                "Get detailed assessment"
            ],
            actions=[
                {"type": "navigate", "path": "/intake", "label": "Start Full Assessment"},
                {"type": "navigate", "path": "/marketplace", "label": "Browse Installers"}
            ],
            data={
                "roof_area_sqft": roof_area,
                "annual_potential_liters": annual_potential_liters,
                "recommended_tank_liters": recommended_tank,
                "annual_savings_inr": annual_savings,
                "co2_offset_kg": annual_co2
            },
            follow_up_questions=[
                "Would you like subsidy information?",
                "Want me to find installers?",
                "Need a detailed PDF report?"
            ]
        )
    
    def _handle_subsidy_query(
        self,
        conv: ConversationContext,
        entities: Dict
    ) -> CopilotResponse:
        """Handle subsidy-related queries."""
        
        city = entities.get("city") or conv.extracted_entities.get("city", "your city")
        budget = entities.get("budget") or conv.extracted_entities.get("budget", 50000)
        
        response_message = f"""🏛️ **Government Subsidy Options for RWH**

Based on typical eligibility in {city}:

**1. Jal Shakti Abhiyan 2024** 🌊
• Coverage: Up to **50%** of installation cost
• Max Amount: **₹50,000**
• Status: ✅ Applications Open
• Your estimate: ₹{min(budget * 0.5, 50000):,.0f}

**2. State RWH Subsidy** (Rajasthan/your state)
• Coverage: **35%** of cost
• Max Amount: **₹25,000**
• Status: ✅ Available

**3. Municipal Rebate**
• Property tax rebate: **6-10%**
• One-time incentive: ₹5,000 - ₹15,000

📝 **Documents Needed:**
• Aadhaar Card
• Property Tax Receipt
• Bank Passbook
• Installation Quote

Would you like me to:
1. 📋 Check your exact eligibility
2. 🚀 Auto-apply using DigiLocker
3. 📞 Connect with subsidy helpdesk"""
        
        return CopilotResponse(
            message=response_message,
            intent=IntentType.SUBSIDY_INFO,
            confidence=0.92,
            suggestions=[
                "Check my eligibility",
                "Auto-apply for subsidy",
                "What documents do I need?"
            ],
            actions=[
                {"type": "navigate", "path": "/subsidies", "label": "Check Eligibility"},
                {"type": "api_call", "endpoint": "/api/v1/subsidies/check", "label": "Auto-Check"}
            ],
            data={
                "schemes": [
                    {"name": "Jal Shakti Abhiyan", "max": 50000, "coverage": 0.5},
                    {"name": "State RWH Subsidy", "max": 25000, "coverage": 0.35}
                ]
            }
        )
    
    def _handle_installer_query(
        self,
        conv: ConversationContext,
        entities: Dict
    ) -> CopilotResponse:
        """Handle installer search queries."""
        
        city = entities.get("city") or conv.extracted_entities.get("city", "your area")
        
        # Mock installer data
        installers = [
            {"name": "AquaHarvest Solutions", "rating": 4.8, "rpi": 92, "projects": 156},
            {"name": "GreenWater Systems", "rating": 4.6, "rpi": 88, "projects": 98},
            {"name": "RainMaster Pro", "rating": 4.5, "rpi": 85, "projects": 72}
        ]
        
        installer_text = "\n".join([
            f"**{i+1}. {inst['name']}** ⭐ {inst['rating']}\n   • RPI Score: {inst['rpi']}/100 | Projects: {inst['projects']}"
            for i, inst in enumerate(installers)
        ])
        
        response_message = f"""🔧 **Top Verified Installers in {city}**

{installer_text}

All installers are:
✅ RainForge Verified
✅ Background Checked
✅ Escrow Payment Protected

**Smart Allocation** can auto-select the best match based on:
• Your budget & timeline
• Installer capacity & proximity
• Past performance score

Would you like me to:
1. 🎯 Run Smart Allocation
2. 📊 Compare these installers
3. 💬 Get quotes from all three"""
        
        return CopilotResponse(
            message=response_message,
            intent=IntentType.INSTALLER_SEARCH,
            confidence=0.90,
            suggestions=[
                "Run smart allocation",
                "Compare installers",
                "Get quotes"
            ],
            actions=[
                {"type": "navigate", "path": "/marketplace", "label": "View All Installers"},
                {"type": "api_call", "endpoint": "/api/v1/marketplace/allocate", "label": "Smart Allocate"}
            ],
            data={"installers": installers}
        )
    
    def _handle_maintenance_query(
        self,
        conv: ConversationContext,
        entities: Dict
    ) -> CopilotResponse:
        """Handle maintenance and troubleshooting queries."""
        
        response_message = """🔧 **RWH Maintenance Guide**

**Common Issues & Solutions:**

**1. Filter Clogged** 🍂
• Clean filter mesh monthly
• Replace charcoal every 6 months
• Check after heavy rain

**2. Low Water Collection** 💧
• Inspect gutters for debris
• Check for pipe leaks
• Verify first-flush is working

**3. Water Quality Issues** 🧪
• Test pH monthly (ideal: 6.5-8.5)
• Clean tank annually
• Add chlorine if storing >7 days

**Seasonal Checklist:**
☐ Pre-monsoon: Clean all filters, check pipes
☐ During monsoon: Weekly filter check
☐ Post-monsoon: Full system inspection

Would you like:
1. 📅 Schedule a maintenance visit
2. 📖 Detailed troubleshooting guide
3. 🎥 Watch maintenance videos"""
        
        return CopilotResponse(
            message=response_message,
            intent=IntentType.MAINTENANCE_HELP,
            confidence=0.88,
            suggestions=[
                "Schedule maintenance",
                "My filter is clogged",
                "Water quality test"
            ],
            actions=[
                {"type": "navigate", "path": "/maintenance", "label": "Schedule Service"},
                {"type": "navigate", "path": "/tutorials", "label": "Watch Tutorials"}
            ]
        )
    
    def _handle_status_query(self, conv: ConversationContext) -> CopilotResponse:
        """Handle project status queries."""
        
        if conv.project_id:
            response_message = f"""📊 **Project Status: #{conv.project_id}**

**Current Stage:** Installation in Progress (75%)

**Timeline:**
✅ Assessment Complete - Jan 15
✅ Installer Assigned - Jan 20
✅ Materials Delivered - Jan 28
🔄 Installation - In Progress
⏳ Verification - Pending
⏳ Final Payment - Pending

**Next Steps:**
• Installation completion: ~Feb 5
• Photo verification required after
• Final 30% payment after approval

**Your Installer:** AquaHarvest Solutions
📞 Contact: +91 98765 43210"""
        else:
            response_message = """📊 **Check Your Project Status**

I couldn't find an active project linked to your account.

Would you like to:
1. 🔍 Search by project ID
2. 📋 View all your projects
3. 🆕 Start a new assessment"""
        
        return CopilotResponse(
            message=response_message,
            intent=IntentType.PROJECT_STATUS,
            confidence=0.85,
            suggestions=[
                "Show all my projects",
                "Contact installer",
                "Start new project"
            ],
            actions=[
                {"type": "navigate", "path": "/portfolio", "label": "View Projects"}
            ]
        )
    
    def _handle_complaint(
        self,
        conv: ConversationContext,
        message: str
    ) -> CopilotResponse:
        """Handle complaint/grievance queries."""
        
        response_message = """📝 **File a Complaint**

I'm sorry to hear you're facing an issue. Let me help you resolve it quickly.

**Complaint Categories:**
1. 🔧 Installation Quality Issue
2. ⏰ Installer Delay
3. 💰 Payment/Refund Issue
4. 📱 App/Platform Issue
5. 📋 Other

**Fast Track Options:**
• For urgent issues: Call **1800-XXX-XXXX** (toll-free)
• WhatsApp: Send "HELP" to +91 98765 00000

**What would you like to report?**

Note: All complaints are tracked and must be resolved within 7 working days as per our SLA."""
        
        return CopilotResponse(
            message=response_message,
            intent=IntentType.COMPLAINT,
            confidence=0.85,
            suggestions=[
                "Installation quality issue",
                "Installer is delayed",
                "Payment problem",
                "Talk to human agent"
            ],
            actions=[
                {"type": "navigate", "path": "/grievance", "label": "File Formal Complaint"},
                {"type": "call", "number": "1800XXXXXXX", "label": "Call Helpline"}
            ]
        )
    
    def _handle_general_query(
        self,
        conv: ConversationContext,
        message: str
    ) -> CopilotResponse:
        """Handle general/fallback queries."""
        
        response_message = """👋 **Hello! I'm your RainForge AI Assistant**

I can help you with:

🌧️ **Rainwater Harvesting**
• Calculate your roof's water potential
• Find the best system for your home
• Estimate costs and savings

💰 **Subsidies & Payments**
• Check government scheme eligibility
• Auto-apply using DigiLocker
• Track payment status

🔧 **Installation & Maintenance**
• Find verified installers
• Schedule maintenance
• Troubleshoot issues

**Try asking me:**
• "What's my water potential for a 2000 sqft roof in Jaipur?"
• "What subsidies am I eligible for?"
• "Find installers near me"

How can I help you today?"""
        
        return CopilotResponse(
            message=response_message,
            intent=IntentType.GENERAL_INFO,
            confidence=0.7,
            suggestions=[
                "Calculate my water potential",
                "Check subsidy eligibility",
                "Find installers",
                "Talk to support"
            ]
        )
    
    # ==================== DOCUMENT PARSING ====================
    
    async def parse_document(
        self,
        user_id: str,
        document_content: bytes,
        document_name: str,
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse uploaded document and extract relevant data.
        
        Uses OCR and NLP to extract property/RWH related information.
        """
        # Mock document parsing (in production, use GPT-4 Vision or specialized OCR)
        
        # Detect document type from name if not provided
        if not document_type:
            name_lower = document_name.lower()
            if 'property' in name_lower or 'tax' in name_lower:
                document_type = "property_tax"
            elif 'electric' in name_lower:
                document_type = "electricity_bill"
            elif 'water' in name_lower:
                document_type = "water_bill"
            elif 'quote' in name_lower or 'estimate' in name_lower:
                document_type = "installation_quote"
            else:
                document_type = "unknown"
        
        # Mock extracted data based on document type
        extracted = self._mock_document_extraction(document_type)
        
        logger.info(f"📄 Document parsed: {document_name} -> {document_type}")
        
        return {
            "success": True,
            "document_name": document_name,
            "document_type": document_type,
            "extracted_data": extracted.to_dict(),
            "message": f"Successfully extracted data from {document_type.replace('_', ' ')}"
        }
    
    def _mock_document_extraction(self, doc_type: str) -> ExtractedDocumentData:
        """Generate mock extracted data for demo."""
        
        if doc_type == "property_tax":
            return ExtractedDocumentData(
                document_type="property_tax",
                confidence=0.92,
                extracted_fields={
                    "property_address": "123, Main Road, Sector 5, Jaipur - 302001",
                    "owner_name": "Rajesh Sharma",
                    "built_up_area_sqft": 2500,
                    "plot_area_sqft": 3000,
                    "property_type": "Residential",
                    "floors": 2
                }
            )
        elif doc_type == "installation_quote":
            return ExtractedDocumentData(
                document_type="installation_quote",
                confidence=0.88,
                extracted_fields={
                    "installer_name": "AquaHarvest Solutions",
                    "total_amount": 85000,
                    "tank_capacity_liters": 10000,
                    "filter_type": "Multi-stage",
                    "warranty_years": 5,
                    "completion_days": 7
                }
            )
        else:
            return ExtractedDocumentData(
                document_type=doc_type,
                confidence=0.75,
                extracted_fields={"raw_text_preview": "Document content extracted..."}
            )
    
    # ==================== PROACTIVE RECOMMENDATIONS ====================
    
    async def get_recommendations(
        self,
        user_id: str,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate proactive recommendations for user.
        
        Based on weather, project status, and user behavior.
        """
        recommendations = []
        
        # Weather-based recommendations
        recommendations.append({
            "type": "weather_alert",
            "priority": "high",
            "title": "🌧️ Heavy Rain Expected This Week",
            "message": "IMD predicts 50-80mm rainfall in your area. Make sure your filters are clean!",
            "action": {"type": "navigate", "path": "/maintenance", "label": "Check Maintenance"}
        })
        
        # Project-based recommendations
        if project_id:
            recommendations.append({
                "type": "project_update",
                "priority": "medium",
                "title": "📊 Your System Collected 450L Yesterday",
                "message": "That's 15% above the monthly average! Your ROI is improving.",
                "action": {"type": "navigate", "path": f"/monitoring/{project_id}", "label": "View Dashboard"}
            })
        
        # Subsidy deadline
        recommendations.append({
            "type": "subsidy_deadline",
            "priority": "medium",
            "title": "⏰ Jal Shakti Deadline: Feb 28",
            "message": "Apply now to avail 50% subsidy. Auto-apply takes just 2 minutes.",
            "action": {"type": "navigate", "path": "/subsidies", "label": "Apply Now"}
        })
        
        # Referral opportunity
        recommendations.append({
            "type": "referral",
            "priority": "low",
            "title": "🎁 Earn ₹500 Per Referral",
            "message": "Share RainForge with neighbors and earn water credits.",
            "action": {"type": "share", "label": "Share Referral Link"}
        })
        
        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }


# Singleton instance
_service: Optional[AICopilotService] = None


def get_ai_copilot_service() -> AICopilotService:
    """Get or create the AI Copilot service singleton."""
    global _service
    if _service is None:
        _service = AICopilotService()
    return _service
