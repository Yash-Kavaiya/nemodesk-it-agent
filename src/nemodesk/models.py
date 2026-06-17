# SPDX-License-Identifier: Apache-2.0
"""Shared data models and enterprise reference data for NemoDesk tools."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    P1 = "P1"  # Critical - business down
    P2 = "P2"  # High - major degradation
    P3 = "P3"  # Medium - single user / workaround exists
    P4 = "P4"  # Low - request / informational


class Category(str, Enum):
    ACCESS = "access_management"
    NETWORK = "network"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    EMAIL = "email_collaboration"
    SECURITY = "security_incident"
    CLOUD = "cloud_infra"
    DATABASE = "database"
    OTHER = "other"


# Routing table: which fulfilment team owns each category.
ROUTING_TABLE: dict[str, str] = {
    Category.ACCESS.value: "IAM-Team",
    Category.NETWORK.value: "Network-Operations",
    Category.HARDWARE.value: "Field-Support",
    Category.SOFTWARE.value: "App-Support",
    Category.EMAIL.value: "Messaging-Team",
    Category.SECURITY.value: "SecOps-CSIRT",
    Category.CLOUD.value: "Cloud-Platform",
    Category.DATABASE.value: "DBA-Team",
    Category.OTHER.value: "Service-Desk-L1",
}

# SLA response targets in minutes, keyed by priority.
SLA_MINUTES: dict[str, int] = {
    Priority.P1.value: 15,
    Priority.P2.value: 60,
    Priority.P3.value: 480,
    Priority.P4.value: 1440,
}


class TicketClassification(BaseModel):
    category: str = Field(description="One of the Category enum values")
    priority: str = Field(description="One of P1..P4")
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = ""


class ResolutionResult(BaseModel):
    resolved: bool
    steps: list[str] = []
    summary: str = ""
    needs_human: bool = False
