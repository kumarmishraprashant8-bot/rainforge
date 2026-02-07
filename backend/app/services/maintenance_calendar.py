"""
Maintenance Calendar Service
Generate iCal exports and schedule maintenance reminders
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import uuid


class MaintenanceType(str, Enum):
    """Types of maintenance."""
    FILTER_CLEANING = "filter_cleaning"
    TANK_CLEANING = "tank_cleaning"
    GUTTER_CLEANING = "gutter_cleaning"
    PUMP_SERVICE = "pump_service"
    SENSOR_CALIBRATION = "sensor_calibration"
    ANNUAL_INSPECTION = "annual_inspection"
    FIRST_FLUSH_CHECK = "first_flush_check"


@dataclass
class MaintenanceEvent:
    """Maintenance event."""
    id: str
    project_id: int
    project_name: str
    maintenance_type: MaintenanceType
    title: str
    description: str
    scheduled_date: datetime
    reminder_days: int = 7
    is_completed: bool = False
    completed_date: Optional[datetime] = None


class MaintenanceCalendarService:
    """
    Maintenance scheduling and calendar export.
    
    Features:
    - Schedule based on installation date
    - iCal export
    - Reminder generation
    - Smart scheduling based on usage
    """
    
    # Default maintenance intervals (days)
    MAINTENANCE_INTERVALS = {
        MaintenanceType.FILTER_CLEANING: 30,       # Monthly
        MaintenanceType.TANK_CLEANING: 180,        # 6 months
        MaintenanceType.GUTTER_CLEANING: 90,       # Quarterly
        MaintenanceType.PUMP_SERVICE: 365,         # Annual
        MaintenanceType.SENSOR_CALIBRATION: 180,   # 6 months
        MaintenanceType.ANNUAL_INSPECTION: 365,    # Annual
        MaintenanceType.FIRST_FLUSH_CHECK: 90      # Quarterly
    }
    
    MAINTENANCE_TITLES = {
        MaintenanceType.FILTER_CLEANING: "Filter Cleaning",
        MaintenanceType.TANK_CLEANING: "Tank Cleaning & Sanitization",
        MaintenanceType.GUTTER_CLEANING: "Gutter & Downpipe Cleaning",
        MaintenanceType.PUMP_SERVICE: "Pump Servicing",
        MaintenanceType.SENSOR_CALIBRATION: "Sensor Calibration",
        MaintenanceType.ANNUAL_INSPECTION: "Annual System Inspection",
        MaintenanceType.FIRST_FLUSH_CHECK: "First Flush Diverter Check"
    }
    
    def __init__(self):
        pass
    
    def generate_maintenance_schedule(
        self,
        project_id: int,
        project_name: str,
        installation_date: datetime,
        components: List[str] = None,
        years_ahead: int = 2
    ) -> List[MaintenanceEvent]:
        """Generate maintenance schedule from installation date."""
        events = []
        end_date = datetime.now() + timedelta(days=365 * years_ahead)
        
        # Determine which maintenance types apply
        applicable_types = [
            MaintenanceType.FILTER_CLEANING,
            MaintenanceType.TANK_CLEANING,
            MaintenanceType.GUTTER_CLEANING,
            MaintenanceType.ANNUAL_INSPECTION,
            MaintenanceType.FIRST_FLUSH_CHECK
        ]
        
        if components:
            if "pump" in components:
                applicable_types.append(MaintenanceType.PUMP_SERVICE)
            if "sensor" in components or "iot" in components:
                applicable_types.append(MaintenanceType.SENSOR_CALIBRATION)
        
        for maint_type in applicable_types:
            interval = self.MAINTENANCE_INTERVALS[maint_type]
            title = self.MAINTENANCE_TITLES[maint_type]
            
            # Generate events from installation date
            current_date = installation_date + timedelta(days=interval)
            
            while current_date <= end_date:
                if current_date > datetime.now() - timedelta(days=30):  # Skip very old past events
                    events.append(MaintenanceEvent(
                        id=str(uuid.uuid4()),
                        project_id=project_id,
                        project_name=project_name,
                        maintenance_type=maint_type,
                        title=f"{title} - {project_name}",
                        description=self._get_maintenance_description(maint_type),
                        scheduled_date=current_date,
                        reminder_days=7 if interval <= 90 else 14,
                        is_completed=current_date < datetime.now()
                    ))
                
                current_date += timedelta(days=interval)
        
        # Sort by date
        events.sort(key=lambda e: e.scheduled_date)
        
        return events
    
    def get_upcoming_maintenance(
        self,
        events: List[MaintenanceEvent],
        days_ahead: int = 30
    ) -> List[MaintenanceEvent]:
        """Get upcoming maintenance within specified days."""
        now = datetime.now()
        cutoff = now + timedelta(days=days_ahead)
        
        return [
            e for e in events
            if not e.is_completed and now <= e.scheduled_date <= cutoff
        ]
    
    def get_overdue_maintenance(
        self,
        events: List[MaintenanceEvent]
    ) -> List[MaintenanceEvent]:
        """Get overdue maintenance items."""
        now = datetime.now()
        
        return [
            e for e in events
            if not e.is_completed and e.scheduled_date < now
        ]
    
    def export_to_ical(
        self,
        events: List[MaintenanceEvent],
        calendar_name: str = "RainForge Maintenance"
    ) -> str:
        """Export events to iCal format."""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//RainForge//Maintenance Calendar//EN",
            f"X-WR-CALNAME:{calendar_name}",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]
        
        for event in events:
            if event.is_completed:
                continue
            
            event_lines = self._event_to_ical(event)
            lines.extend(event_lines)
        
        lines.append("END:VCALENDAR")
        
        return "\r\n".join(lines)
    
    def _event_to_ical(self, event: MaintenanceEvent) -> List[str]:
        """Convert event to iCal VEVENT lines."""
        dtstart = event.scheduled_date.strftime("%Y%m%dT090000")
        dtend = event.scheduled_date.strftime("%Y%m%dT100000")
        dtstamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        
        # Calculate reminder trigger
        trigger = f"-P{event.reminder_days}D"
        
        lines = [
            "BEGIN:VEVENT",
            f"UID:{event.id}@rainforge.gov.in",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{self._escape_ical(event.title)}",
            f"DESCRIPTION:{self._escape_ical(event.description)}",
            f"LOCATION:{event.project_name}",
            f"CATEGORIES:{event.maintenance_type.value}",
            "STATUS:CONFIRMED",
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"TRIGGER:{trigger}",
            f"DESCRIPTION:Reminder: {event.title}",
            "END:VALARM",
            "END:VEVENT"
        ]
        
        return lines
    
    def _escape_ical(self, text: str) -> str:
        """Escape special characters for iCal."""
        text = text.replace("\\", "\\\\")
        text = text.replace(",", "\\,")
        text = text.replace(";", "\\;")
        text = text.replace("\n", "\\n")
        return text
    
    def _get_maintenance_description(self, maint_type: MaintenanceType) -> str:
        """Get detailed description for maintenance type."""
        descriptions = {
            MaintenanceType.FILTER_CLEANING: (
                "Clean the filter mesh and remove debris. Check for damage. "
                "Rinse thoroughly and reinstall."
            ),
            MaintenanceType.TANK_CLEANING: (
                "Drain tank partially, scrub interior walls, remove sediment. "
                "Check for cracks or leaks. Sanitize if needed."
            ),
            MaintenanceType.GUTTER_CLEANING: (
                "Remove leaves and debris from gutters. Check for proper slope. "
                "Inspect downpipes for blockages."
            ),
            MaintenanceType.PUMP_SERVICE: (
                "Check pump operation, clean intake filter, inspect electrical connections. "
                "Test pressure and flow rate."
            ),
            MaintenanceType.SENSOR_CALIBRATION: (
                "Verify sensor readings against manual measurement. "
                "Recalibrate if deviation exceeds 5%."
            ),
            MaintenanceType.ANNUAL_INSPECTION: (
                "Complete system inspection including tank, pipes, filters, pumps, and sensors. "
                "Document condition and recommend repairs."
            ),
            MaintenanceType.FIRST_FLUSH_CHECK: (
                "Check first flush diverter operation. Clean and adjustball valve. "
                "Ensure proper drainage."
            )
        }
        return descriptions.get(maint_type, "Scheduled maintenance")
    
    def get_maintenance_summary(
        self,
        project_id: int,
        events: List[MaintenanceEvent]
    ) -> Dict[str, Any]:
        """Get maintenance summary for project."""
        project_events = [e for e in events if e.project_id == project_id]
        
        now = datetime.now()
        upcoming = [e for e in project_events if not e.is_completed and e.scheduled_date >= now]
        overdue = [e for e in project_events if not e.is_completed and e.scheduled_date < now]
        completed_this_year = [
            e for e in project_events 
            if e.is_completed and e.scheduled_date.year == now.year
        ]
        
        return {
            "project_id": project_id,
            "total_scheduled": len([e for e in project_events if not e.is_completed]),
            "upcoming_count": len(upcoming),
            "overdue_count": len(overdue),
            "completed_this_year": len(completed_this_year),
            "next_maintenance": upcoming[0].scheduled_date.isoformat() if upcoming else None,
            "next_maintenance_type": upcoming[0].maintenance_type.value if upcoming else None,
            "health_score": self._calculate_health_score(overdue, completed_this_year)
        }
    
    def _calculate_health_score(
        self,
        overdue: List,
        completed: List
    ) -> int:
        """Calculate maintenance health score (0-100)."""
        base_score = 100
        
        # Penalty for overdue items
        base_score -= len(overdue) * 15
        
        # Bonus for completed items
        base_score += min(len(completed) * 5, 20)
        
        return max(0, min(100, base_score))


# Singleton
_calendar_service: Optional[MaintenanceCalendarService] = None

def get_calendar_service() -> MaintenanceCalendarService:
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = MaintenanceCalendarService()
    return _calendar_service
