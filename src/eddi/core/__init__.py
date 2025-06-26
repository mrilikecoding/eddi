"""Core components for the Eddi interactive lighting system."""

from .engine import EddiEngine
from .types import PoseData, LightingCommand

__all__ = ["EddiEngine", "PoseData", "LightingCommand"]