"""
Gamification & Leaderboard Service
Badges, points, and rankings for installers and users
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import random


class BadgeType(str, Enum):
    """Achievement badge types."""
    # Installer badges
    FIRST_INSTALL = "first_install"
    TEN_INSTALLS = "ten_installs"
    FIFTY_INSTALLS = "fifty_installs"
    HUNDRED_INSTALLS = "hundred_installs"
    FIVE_STAR = "five_star"
    SPEED_DEMON = "speed_demon"
    QUALITY_MASTER = "quality_master"
    ECO_WARRIOR = "eco_warrior"
    
    # User badges
    EARLY_ADOPTER = "early_adopter"
    GREEN_HERO = "green_hero"
    WATER_SAVER = "water_saver"
    REFERRAL_CHAMPION = "referral_champion"
    COMMUNITY_LEADER = "community_leader"
    FULL_VERIFICATION = "full_verification"


@dataclass
class Badge:
    """Badge definition."""
    type: BadgeType
    name: str
    description: str
    icon: str
    points: int
    color: str


@dataclass
class LeaderboardEntry:
    """Leaderboard entry."""
    rank: int
    id: str
    name: str
    avatar: Optional[str]
    score: int
    projects: int
    rating: float
    badges: List[str]
    change: int  # Position change since last period


class GamificationService:
    """
    Gamification system with badges, points, and leaderboards.
    
    Features:
    - Achievement badges
    - Point system
    - Leaderboards (installers, districts, users)
    - Streak tracking
    - Challenges
    """
    
    BADGES = {
        BadgeType.FIRST_INSTALL: Badge(
            type=BadgeType.FIRST_INSTALL,
            name="First Steps",
            description="Completed first installation",
            icon="🎯",
            points=100,
            color="#22c55e"
        ),
        BadgeType.TEN_INSTALLS: Badge(
            type=BadgeType.TEN_INSTALLS,
            name="Rising Star",
            description="Completed 10 installations",
            icon="⭐",
            points=500,
            color="#f59e0b"
        ),
        BadgeType.FIFTY_INSTALLS: Badge(
            type=BadgeType.FIFTY_INSTALLS,
            name="Pro Installer",
            description="Completed 50 installations",
            icon="🏆",
            points=2000,
            color="#7c3aed"
        ),
        BadgeType.HUNDRED_INSTALLS: Badge(
            type=BadgeType.HUNDRED_INSTALLS,
            name="Master Installer",
            description="Completed 100 installations",
            icon="👑",
            points=5000,
            color="#ef4444"
        ),
        BadgeType.FIVE_STAR: Badge(
            type=BadgeType.FIVE_STAR,
            name="Perfect Rating",
            description="Achieved 5-star average rating",
            icon="⭐⭐⭐⭐⭐",
            points=1000,
            color="#fbbf24"
        ),
        BadgeType.SPEED_DEMON: Badge(
            type=BadgeType.SPEED_DEMON,
            name="Speed Demon",
            description="Completed 10 projects ahead of schedule",
            icon="⚡",
            points=800,
            color="#0ea5e9"
        ),
        BadgeType.QUALITY_MASTER: Badge(
            type=BadgeType.QUALITY_MASTER,
            name="Quality Master",
            description="100% verification pass rate (10+ projects)",
            icon="✅",
            points=1500,
            color="#10b981"
        ),
        BadgeType.ECO_WARRIOR: Badge(
            type=BadgeType.ECO_WARRIOR,
            name="Eco Warrior",
            description="Saved 1 million liters of water",
            icon="🌍",
            points=3000,
            color="#22c55e"
        ),
        BadgeType.EARLY_ADOPTER: Badge(
            type=BadgeType.EARLY_ADOPTER,
            name="Early Adopter",
            description="Joined in the first month",
            icon="🚀",
            points=200,
            color="#8b5cf6"
        ),
        BadgeType.GREEN_HERO: Badge(
            type=BadgeType.GREEN_HERO,
            name="Green Hero",
            description="Offset 1 ton of CO₂",
            icon="🌱",
            points=500,
            color="#16a34a"
        ),
        BadgeType.WATER_SAVER: Badge(
            type=BadgeType.WATER_SAVER,
            name="Water Saver",
            description="Collected 10,000 liters of rainwater",
            icon="💧",
            points=300,
            color="#0284c7"
        ),
        BadgeType.REFERRAL_CHAMPION: Badge(
            type=BadgeType.REFERRAL_CHAMPION,
            name="Referral Champion",
            description="Referred 5 successful installations",
            icon="🤝",
            points=1000,
            color="#f97316"
        ),
        BadgeType.COMMUNITY_LEADER: Badge(
            type=BadgeType.COMMUNITY_LEADER,
            name="Community Leader",
            description="Organized a community RWH drive",
            icon="👥",
            points=2000,
            color="#6366f1"
        ),
        BadgeType.FULL_VERIFICATION: Badge(
            type=BadgeType.FULL_VERIFICATION,
            name="Verification Pro",
            description="Completed all verification stages",
            icon="📸",
            points=400,
            color="#14b8a6"
        )
    }
    
    def __init__(self):
        # In-memory stores (would be database in production)
        self._user_points: Dict[str, int] = {}
        self._user_badges: Dict[str, List[BadgeType]] = {}
        self._user_streaks: Dict[str, int] = {}
    
    def get_badge_info(self, badge_type: BadgeType) -> Badge:
        """Get badge information."""
        return self.BADGES.get(badge_type)
    
    def get_all_badges(self) -> List[Dict]:
        """Get all available badges."""
        return [
            {
                "type": b.type.value,
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "points": b.points,
                "color": b.color
            }
            for b in self.BADGES.values()
        ]
    
    async def award_badge(
        self,
        user_id: str,
        badge_type: BadgeType
    ) -> Optional[Badge]:
        """Award badge to user."""
        if user_id not in self._user_badges:
            self._user_badges[user_id] = []
        
        if badge_type in self._user_badges[user_id]:
            return None  # Already has badge
        
        badge = self.BADGES.get(badge_type)
        if not badge:
            return None
        
        self._user_badges[user_id].append(badge_type)
        await self.add_points(user_id, badge.points, f"Badge: {badge.name}")
        
        return badge
    
    async def add_points(
        self,
        user_id: str,
        points: int,
        reason: str = ""
    ) -> int:
        """Add points to user."""
        if user_id not in self._user_points:
            self._user_points[user_id] = 0
        
        self._user_points[user_id] += points
        return self._user_points[user_id]
    
    def get_user_points(self, user_id: str) -> int:
        """Get user's total points."""
        return self._user_points.get(user_id, 0)
    
    def get_user_badges(self, user_id: str) -> List[Badge]:
        """Get user's earned badges."""
        badge_types = self._user_badges.get(user_id, [])
        return [self.BADGES[bt] for bt in badge_types if bt in self.BADGES]
    
    def get_user_level(self, user_id: str) -> Dict:
        """Get user's level based on points."""
        points = self.get_user_points(user_id)
        
        levels = [
            (0, "Beginner", "🌱"),
            (500, "Learner", "📚"),
            (1500, "Contributor", "🔧"),
            (3000, "Expert", "⭐"),
            (6000, "Master", "🏆"),
            (10000, "Champion", "👑"),
            (20000, "Legend", "🌟")
        ]
        
        current_level = levels[0]
        next_level = levels[1] if len(levels) > 1 else None
        
        for i, level in enumerate(levels):
            if points >= level[0]:
                current_level = level
                next_level = levels[i + 1] if i + 1 < len(levels) else None
        
        progress = 0
        if next_level:
            range_size = next_level[0] - current_level[0]
            progress = (points - current_level[0]) / range_size * 100
        
        return {
            "level": current_level[1],
            "icon": current_level[2],
            "points": points,
            "next_level": next_level[1] if next_level else None,
            "points_to_next": next_level[0] - points if next_level else 0,
            "progress_percent": min(progress, 100)
        }
    
    async def get_installer_leaderboard(
        self,
        limit: int = 10,
        period: str = "month"
    ) -> List[LeaderboardEntry]:
        """Get installer leaderboard."""
        # Mock data (would query database in production)
        installers = [
            {"name": "RWH Solutions Pvt Ltd", "projects": 156, "rating": 4.9},
            {"name": "Green Water Systems", "projects": 134, "rating": 4.8},
            {"name": "EcoHarvest India", "projects": 128, "rating": 4.7},
            {"name": "AquaSave Technologies", "projects": 112, "rating": 4.8},
            {"name": "JalSanchay Enterprises", "projects": 98, "rating": 4.6},
            {"name": "RainMasters Co.", "projects": 87, "rating": 4.9},
            {"name": "WaterWise Solutions", "projects": 76, "rating": 4.5},
            {"name": "Monsoon Tech", "projects": 65, "rating": 4.7},
            {"name": "HydroStore Systems", "projects": 54, "rating": 4.4},
            {"name": "VarshaJal Industries", "projects": 43, "rating": 4.6}
        ]
        
        return [
            LeaderboardEntry(
                rank=i + 1,
                id=f"inst_{i}",
                name=inst["name"],
                avatar=None,
                score=inst["projects"] * 100 + int(inst["rating"] * 200),
                projects=inst["projects"],
                rating=inst["rating"],
                badges=["⭐", "🏆"][:random.randint(0, 2)],
                change=random.randint(-2, 3)
            )
            for i, inst in enumerate(installers[:limit])
        ]
    
    async def get_district_leaderboard(
        self,
        state: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get district leaderboard."""
        districts = [
            {"name": "Pune", "state": "Maharashtra", "projects": 234, "water_saved_kl": 12500},
            {"name": "Bengaluru Urban", "state": "Karnataka", "projects": 198, "water_saved_kl": 10800},
            {"name": "Chennai", "state": "Tamil Nadu", "projects": 187, "water_saved_kl": 9500},
            {"name": "Jaipur", "state": "Rajasthan", "projects": 156, "water_saved_kl": 8200},
            {"name": "Ahmedabad", "state": "Gujarat", "projects": 145, "water_saved_kl": 7800},
            {"name": "Hyderabad", "state": "Telangana", "projects": 134, "water_saved_kl": 7200},
            {"name": "Kochi", "state": "Kerala", "projects": 123, "water_saved_kl": 6500},
            {"name": "Thane", "state": "Maharashtra", "projects": 112, "water_saved_kl": 6100},
            {"name": "Coimbatore", "state": "Tamil Nadu", "projects": 98, "water_saved_kl": 5200},
            {"name": "Mysuru", "state": "Karnataka", "projects": 87, "water_saved_kl": 4600}
        ]
        
        if state:
            districts = [d for d in districts if d["state"] == state]
        
        return [
            {
                "rank": i + 1,
                "name": d["name"],
                "state": d["state"],
                "projects": d["projects"],
                "water_saved_kl": d["water_saved_kl"],
                "score": d["projects"] * 100 + d["water_saved_kl"],
                "badge": "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else ""
            }
            for i, d in enumerate(districts[:limit])
        ]
    
    async def get_challenges(self, user_id: str) -> List[Dict]:
        """Get active challenges for user."""
        return [
            {
                "id": "challenge_1",
                "title": "Water Warrior Week",
                "description": "Complete 3 verifications this week",
                "progress": 1,
                "target": 3,
                "reward_points": 500,
                "ends_at": (datetime.now() + timedelta(days=3)).isoformat(),
                "icon": "💧"
            },
            {
                "id": "challenge_2",
                "title": "Referral Rush",
                "description": "Refer 2 friends to RainForge",
                "progress": 0,
                "target": 2,
                "reward_points": 300,
                "ends_at": (datetime.now() + timedelta(days=7)).isoformat(),
                "icon": "🤝"
            },
            {
                "id": "challenge_3",
                "title": "Green Month",
                "description": "Save 500L of water this month",
                "progress": 234,
                "target": 500,
                "reward_points": 1000,
                "ends_at": (datetime.now() + timedelta(days=15)).isoformat(),
                "icon": "🌱"
            }
        ]
    
    async def check_achievements(
        self,
        user_id: str,
        event_type: str,
        event_data: Dict
    ) -> List[Badge]:
        """Check and award achievements based on events."""
        awarded = []
        
        if event_type == "installation_complete":
            projects = event_data.get("total_projects", 0)
            
            if projects >= 1:
                badge = await self.award_badge(user_id, BadgeType.FIRST_INSTALL)
                if badge:
                    awarded.append(badge)
            
            if projects >= 10:
                badge = await self.award_badge(user_id, BadgeType.TEN_INSTALLS)
                if badge:
                    awarded.append(badge)
            
            if projects >= 50:
                badge = await self.award_badge(user_id, BadgeType.FIFTY_INSTALLS)
                if badge:
                    awarded.append(badge)
            
            if projects >= 100:
                badge = await self.award_badge(user_id, BadgeType.HUNDRED_INSTALLS)
                if badge:
                    awarded.append(badge)
        
        elif event_type == "verification_complete":
            await self.add_points(user_id, 50, "Verification completed")
        
        elif event_type == "referral_success":
            referrals = event_data.get("total_referrals", 0)
            if referrals >= 5:
                badge = await self.award_badge(user_id, BadgeType.REFERRAL_CHAMPION)
                if badge:
                    awarded.append(badge)
        
        return awarded


# Singleton
_gamification: Optional[GamificationService] = None

def get_gamification_service() -> GamificationService:
    global _gamification
    if _gamification is None:
        _gamification = GamificationService()
    return _gamification
