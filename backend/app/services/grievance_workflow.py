"""
RainForge Grievance & Dispute Resolution System
Citizen complaints, escalation ladder, decommissioning workflow
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid


class GrievanceStatus(Enum):
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    UNDER_INVESTIGATION = "under_investigation"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class GrievanceCategory(Enum):
    INSTALLATION_QUALITY = "installation_quality"
    INSTALLER_BEHAVIOR = "installer_behavior"
    PAYMENT_DISPUTE = "payment_dispute"
    SYSTEM_MALFUNCTION = "system_malfunction"
    SUBSIDY_DELAY = "subsidy_delay"
    VERIFICATION_FRAUD = "verification_fraud"
    OTHER = "other"


class EscalationLevel(Enum):
    LEVEL_1_INSTALLER = "installer"
    LEVEL_2_PLATFORM = "platform_support"
    LEVEL_3_DISTRICT = "district_collector"
    LEVEL_4_STATE = "state_department"
    LEVEL_5_MINISTRY = "ministry"


@dataclass
class Grievance:
    """Citizen grievance record."""
    grievance_id: str
    project_id: str
    complainant_name: str
    complainant_phone: str
    complainant_email: Optional[str]
    category: GrievanceCategory
    description: str
    photo_urls: List[str] = field(default_factory=list)
    video_urls: List[str] = field(default_factory=list)
    status: GrievanceStatus = GrievanceStatus.SUBMITTED
    escalation_level: EscalationLevel = EscalationLevel.LEVEL_1_INSTALLER
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    resolution_notes: Optional[str] = None
    resolution_date: Optional[datetime] = None


class GrievanceManager:
    """
    Manage citizen grievances with escalation and resolution tracking.
    """
    
    # SLA for each escalation level (in hours)
    ESCALATION_SLA = {
        EscalationLevel.LEVEL_1_INSTALLER: 48,      # 2 days
        EscalationLevel.LEVEL_2_PLATFORM: 72,       # 3 days
        EscalationLevel.LEVEL_3_DISTRICT: 120,      # 5 days
        EscalationLevel.LEVEL_4_STATE: 240,         # 10 days
        EscalationLevel.LEVEL_5_MINISTRY: 720,      # 30 days
    }
    
    def __init__(self):
        self.grievances: Dict[str, Grievance] = {}
        self.escalation_history: Dict[str, List[Dict]] = {}
    
    def file_grievance(
        self,
        project_id: str,
        complainant_name: str,
        complainant_phone: str,
        category: str,
        description: str,
        complainant_email: Optional[str] = None,
        photo_urls: Optional[List[str]] = None,
        video_urls: Optional[List[str]] = None
    ) -> Dict:
        """
        File a new grievance from citizen.
        """
        
        grievance_id = f"GRV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        try:
            cat = GrievanceCategory(category)
        except:
            cat = GrievanceCategory.OTHER
        
        grievance = Grievance(
            grievance_id=grievance_id,
            project_id=project_id,
            complainant_name=complainant_name,
            complainant_phone=complainant_phone,
            complainant_email=complainant_email,
            category=cat,
            description=description,
            photo_urls=photo_urls or [],
            video_urls=video_urls or []
        )
        
        self.grievances[grievance_id] = grievance
        self.escalation_history[grievance_id] = [{
            "level": EscalationLevel.LEVEL_1_INSTALLER.value,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "grievance_filed"
        }]
        
        return {
            "grievance_id": grievance_id,
            "status": "submitted",
            "escalation_level": "installer",
            "expected_resolution_hours": self.ESCALATION_SLA[EscalationLevel.LEVEL_1_INSTALLER],
            "tracking_url": f"/grievance/{grievance_id}",
            "acknowledgement": f"Your grievance has been registered. Reference: {grievance_id}"
        }
    
    def check_and_escalate(self, grievance_id: str) -> Optional[Dict]:
        """
        Check if grievance should be auto-escalated based on SLA breach.
        """
        
        if grievance_id not in self.grievances:
            return None
        
        grievance = self.grievances[grievance_id]
        
        if grievance.status in [GrievanceStatus.RESOLVED, GrievanceStatus.CLOSED]:
            return None
        
        current_level = grievance.escalation_level
        sla_hours = self.ESCALATION_SLA[current_level]
        time_elapsed = (datetime.utcnow() - grievance.last_updated).total_seconds() / 3600
        
        if time_elapsed > sla_hours:
            return self.escalate_grievance(grievance_id, "SLA breach - auto-escalation")
        
        return {
            "grievance_id": grievance_id,
            "escalation_needed": False,
            "hours_elapsed": round(time_elapsed, 1),
            "hours_remaining": round(sla_hours - time_elapsed, 1)
        }
    
    def escalate_grievance(self, grievance_id: str, reason: str) -> Dict:
        """
        Escalate grievance to next level.
        """
        
        if grievance_id not in self.grievances:
            return {"error": "Grievance not found"}
        
        grievance = self.grievances[grievance_id]
        
        # Determine next level
        level_order = list(EscalationLevel)
        current_idx = level_order.index(grievance.escalation_level)
        
        if current_idx >= len(level_order) - 1:
            return {
                "grievance_id": grievance_id,
                "escalation": "already_at_highest_level",
                "current_level": grievance.escalation_level.value
            }
        
        new_level = level_order[current_idx + 1]
        grievance.escalation_level = new_level
        grievance.status = GrievanceStatus.ESCALATED
        grievance.last_updated = datetime.utcnow()
        
        self.escalation_history[grievance_id].append({
            "level": new_level.value,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "action": "escalated"
        })
        
        return {
            "grievance_id": grievance_id,
            "previous_level": level_order[current_idx].value,
            "new_level": new_level.value,
            "reason": reason,
            "new_sla_hours": self.ESCALATION_SLA[new_level],
            "notification_sent_to": self._get_escalation_contact(new_level)
        }
    
    def resolve_grievance(
        self,
        grievance_id: str,
        resolution_notes: str,
        resolved_by: str
    ) -> Dict:
        """
        Mark grievance as resolved.
        """
        
        if grievance_id not in self.grievances:
            return {"error": "Grievance not found"}
        
        grievance = self.grievances[grievance_id]
        grievance.status = GrievanceStatus.RESOLVED
        grievance.resolution_notes = resolution_notes
        grievance.resolution_date = datetime.utcnow()
        grievance.last_updated = datetime.utcnow()
        
        # Calculate resolution time
        resolution_time_hours = (grievance.resolution_date - grievance.created_at).total_seconds() / 3600
        
        self.escalation_history[grievance_id].append({
            "level": grievance.escalation_level.value,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "resolved",
            "resolved_by": resolved_by,
            "notes": resolution_notes
        })
        
        return {
            "grievance_id": grievance_id,
            "status": "resolved",
            "resolution_time_hours": round(resolution_time_hours, 1),
            "resolved_by": resolved_by,
            "escalation_history": self.escalation_history[grievance_id]
        }
    
    def _get_escalation_contact(self, level: EscalationLevel) -> str:
        contacts = {
            EscalationLevel.LEVEL_1_INSTALLER: "installer@assigned.com",
            EscalationLevel.LEVEL_2_PLATFORM: "support@rainforge.in",
            EscalationLevel.LEVEL_3_DISTRICT: "dc-office@district.gov.in",
            EscalationLevel.LEVEL_4_STATE: "jalshakti@state.gov.in",
            EscalationLevel.LEVEL_5_MINISTRY: "grievance@jalshakti.gov.in"
        }
        return contacts.get(level, "support@rainforge.in")
    
    def get_grievance_status(self, grievance_id: str) -> Optional[Dict]:
        """Get current status of a grievance."""
        
        if grievance_id not in self.grievances:
            return None
        
        grievance = self.grievances[grievance_id]
        
        return {
            "grievance_id": grievance_id,
            "project_id": grievance.project_id,
            "category": grievance.category.value,
            "status": grievance.status.value,
            "escalation_level": grievance.escalation_level.value,
            "created_at": grievance.created_at.isoformat(),
            "last_updated": grievance.last_updated.isoformat(),
            "resolution_notes": grievance.resolution_notes,
            "history": self.escalation_history.get(grievance_id, [])
        }


class InstallerAccountability:
    """
    Track installer accountability metrics.
    SLA breaches, blacklist management, performance analytics.
    """
    
    def __init__(self):
        self.breach_records: Dict[int, List[Dict]] = {}
        self.blacklist: Dict[int, Dict] = {}
    
    def record_sla_breach(
        self,
        installer_id: int,
        job_id: str,
        breach_type: str,
        delay_days: int,
        penalty_amount: float
    ) -> Dict:
        """
        Record an SLA breach for an installer.
        """
        
        if installer_id not in self.breach_records:
            self.breach_records[installer_id] = []
        
        breach = {
            "job_id": job_id,
            "breach_type": breach_type,
            "delay_days": delay_days,
            "penalty_amount": penalty_amount,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.breach_records[installer_id].append(breach)
        
        # Check for repeat offender
        recent_breaches = [
            b for b in self.breach_records[installer_id]
            if datetime.fromisoformat(b["timestamp"]) > datetime.utcnow() - timedelta(days=90)
        ]
        
        return {
            "breach_recorded": True,
            "installer_id": installer_id,
            "total_breaches": len(self.breach_records[installer_id]),
            "recent_breaches_90d": len(recent_breaches),
            "repeat_offender": len(recent_breaches) >= 3,
            "auto_blacklist_warning": len(recent_breaches) >= 5
        }
    
    def get_installer_report(self, installer_id: int) -> Dict:
        """
        Generate accountability report for an installer.
        """
        
        breaches = self.breach_records.get(installer_id, [])
        
        total_penalties = sum(b["penalty_amount"] for b in breaches)
        total_delays = sum(b["delay_days"] for b in breaches)
        
        return {
            "installer_id": installer_id,
            "total_breaches": len(breaches),
            "total_penalties_inr": total_penalties,
            "total_delay_days": total_delays,
            "avg_delay_days": round(total_delays / max(1, len(breaches)), 1),
            "is_blacklisted": installer_id in self.blacklist,
            "blacklist_reason": self.blacklist.get(installer_id, {}).get("reason"),
            "breach_history": breaches[-10:]  # Last 10
        }
    
    def blacklist_installer(
        self,
        installer_id: int,
        reason: str,
        blacklisted_by: str,
        duration_days: Optional[int] = None
    ) -> Dict:
        """
        Blacklist an installer.
        """
        
        self.blacklist[installer_id] = {
            "reason": reason,
            "blacklisted_by": blacklisted_by,
            "blacklisted_at": datetime.utcnow().isoformat(),
            "duration_days": duration_days,
            "expires_at": (datetime.utcnow() + timedelta(days=duration_days)).isoformat() if duration_days else None
        }
        
        return {
            "installer_id": installer_id,
            "status": "blacklisted",
            "reason": reason,
            "duration_days": duration_days or "permanent",
            "appeal_available": True
        }


class DecommissioningWorkflow:
    """
    Handle system decommissioning, failure, and subsidy clawback.
    """
    
    CLAWBACK_RULES = {
        0: 1.0,    # Within 1 year: 100% clawback
        1: 0.8,    # 1-2 years: 80%
        2: 0.6,    # 2-3 years: 60%
        3: 0.4,    # 3-4 years: 40%
        4: 0.2,    # 4-5 years: 20%
        5: 0.0,    # After 5 years: no clawback
    }
    
    def initiate_decommission(
        self,
        project_id: str,
        reason: str,
        initiated_by: str,
        subsidy_amount: float,
        installation_date: datetime
    ) -> Dict:
        """
        Initiate decommissioning workflow.
        """
        
        # Calculate clawback
        years_since_install = (datetime.utcnow() - installation_date).days / 365
        
        clawback_pct = 0.0
        for year_threshold, pct in sorted(self.CLAWBACK_RULES.items()):
            if years_since_install <= year_threshold + 1:
                clawback_pct = pct
                break
        
        clawback_amount = subsidy_amount * clawback_pct
        
        # Determine installer penalty
        installer_penalty = 0
        if reason in ["installer_fault", "poor_quality", "fraud"]:
            installer_penalty = clawback_amount * 0.5  # 50% penalty on installer
        
        return {
            "project_id": project_id,
            "decommission_initiated": True,
            "reason": reason,
            "initiated_by": initiated_by,
            "years_since_installation": round(years_since_install, 1),
            "subsidy_received": subsidy_amount,
            "clawback_calculation": {
                "clawback_pct": clawback_pct * 100,
                "clawback_amount_inr": round(clawback_amount, 0),
                "installer_penalty_inr": round(installer_penalty, 0)
            },
            "next_steps": [
                "Site inspection by authorized officer",
                "Photographic documentation",
                "Clawback notice to beneficiary" if clawback_amount > 0 else None,
                "Penalty notice to installer" if installer_penalty > 0 else None,
                "Update public dashboard"
            ],
            "status": "pending_inspection"
        }
    
    def record_abandonment(
        self,
        project_id: str,
        last_telemetry_date: Optional[datetime],
        last_maintenance_date: Optional[datetime]
    ) -> Dict:
        """
        Detect and record system abandonment.
        """
        
        now = datetime.utcnow()
        
        # Check telemetry gap
        if last_telemetry_date:
            telemetry_gap_days = (now - last_telemetry_date).days
        else:
            telemetry_gap_days = 999
        
        # Check maintenance gap
        if last_maintenance_date:
            maintenance_gap_days = (now - last_maintenance_date).days
        else:
            maintenance_gap_days = 999
        
        # Abandonment classification
        if telemetry_gap_days > 180 and maintenance_gap_days > 365:
            status = "abandoned"
            action = "initiate_clawback_review"
        elif telemetry_gap_days > 90 or maintenance_gap_days > 180:
            status = "neglected"
            action = "send_warning_notice"
        elif telemetry_gap_days > 30 or maintenance_gap_days > 90:
            status = "at_risk"
            action = "send_reminder"
        else:
            status = "active"
            action = "none"
        
        return {
            "project_id": project_id,
            "abandonment_status": status,
            "telemetry_gap_days": telemetry_gap_days if telemetry_gap_days < 999 else "no_data",
            "maintenance_gap_days": maintenance_gap_days if maintenance_gap_days < 999 else "no_data",
            "recommended_action": action,
            "clawback_eligible": status == "abandoned"
        }


class OfficerDecisionLog:
    """
    Immutable audit log for officer decisions.
    Anti-corruption and accountability.
    """
    
    def __init__(self):
        self.logs: List[Dict] = []
    
    def log_decision(
        self,
        officer_id: str,
        officer_name: str,
        officer_designation: str,
        entity_type: str,
        entity_id: str,
        decision: str,
        reason: str,
        ip_address: Optional[str] = None
    ) -> Dict:
        """
        Log an officer's decision (immutable).
        """
        
        log_entry = {
            "log_id": f"LOG-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.utcnow().isoformat(),
            "officer": {
                "id": officer_id,
                "name": officer_name,
                "designation": officer_designation
            },
            "entity_type": entity_type,
            "entity_id": entity_id,
            "decision": decision,
            "reason": reason,
            "ip_address": ip_address,
            "audit_hash": self._compute_hash(officer_id, entity_id, decision)
        }
        
        self.logs.append(log_entry)
        
        return log_entry
    
    def _compute_hash(self, *args) -> str:
        import hashlib
        data = "|".join(str(a) for a in args) + datetime.utcnow().isoformat()
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get_audit_trail(
        self,
        entity_id: Optional[str] = None,
        officer_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get audit trail with optional filters.
        """
        
        filtered = self.logs
        
        if entity_id:
            filtered = [l for l in filtered if l["entity_id"] == entity_id]
        
        if officer_id:
            filtered = [l for l in filtered if l["officer"]["id"] == officer_id]
        
        return filtered[-limit:]
    
    def get_audit_readiness_score(self, project_id: str) -> Dict:
        """
        Calculate audit readiness score for a project.
        """
        
        project_logs = [l for l in self.logs if l["entity_id"] == project_id]
        
        required_checkpoints = [
            "assessment_created",
            "installer_allocated",
            "escrow_created",
            "verification_submitted",
            "verification_approved",
            "payment_released"
        ]
        
        found_checkpoints = set(l["decision"] for l in project_logs)
        covered = len(found_checkpoints.intersection(required_checkpoints))
        
        score = (covered / len(required_checkpoints)) * 100
        
        return {
            "project_id": project_id,
            "audit_readiness_score": round(score, 1),
            "checkpoints_covered": covered,
            "checkpoints_required": len(required_checkpoints),
            "missing_checkpoints": list(set(required_checkpoints) - found_checkpoints),
            "total_decisions_logged": len(project_logs),
            "ready_for_audit": score >= 80
        }
