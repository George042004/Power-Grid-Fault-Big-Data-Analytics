"""
========================================================================================
Fault Localization & Maintenance Playbook Module
Module 5: Grid-Level Fault Localization
Academic Project: MARUMUDI GEORGE MULLAR | Guide: Mr. R. SriRamu

DISCLAIMER:
This localization module maps simulated telemetry across logical topological nodes.
It is an educational algorithmic demonstration and must be distinguished from
actual physical telemetry trip-coils, SCADA distance relays, or optical breaker interlocks.
========================================================================================
"""
from datetime import datetime
from typing import Dict, Any, Optional
from config.settings import settings


class FaultLocalizer:
    """
    Localizes detected electrical grid faults across the substation topology:
    Grid Station -> Outgoing Feeder -> Sensor Node.
    Assigns operational severity levels and actionable inspection procedures.
    """

    # Maintenance Action Playbooks per Fault Category
    ACTION_PLAYBOOKS = {
        "Normal": (
            "NORMAL",
            "Routine telemetry within permissible statutory tolerances. Continue automated 24/7 supervisory polling."
        ),
        "Overload": (
            "WARNING",
            "CRITICAL LOAD ADVISORY: Feeder thermal capacity exceeded. Initiate supervisory load balancing or shed non-critical "
            "auxiliary feeders. Dispatch maintenance crew to inspect transformer winding temperatures and busbar contacts."
        ),
        "Short Circuit": (
            "CRITICAL",
            "EMERGENCY TRIP ISOLATION: Severe low-impedance short-circuit fault detected. Verify high-speed circuit breaker lockout. "
            "Isolate faulted feeder segment. Dispatch emergency field crew to survey feeder span for tree contact, line flashover, or insulator breakdown."
        ),
        "Voltage Sag": (
            "WARNING",
            "VOLTAGE SAG NOTIFICATION: Transient/sustained under-voltage detected. Check On-Load Tap Changer (OLTC) position on Main Power Transformer. "
            "Verify transmission intertie voltage and switch on shunt capacitor banks to support line voltage."
        ),
        "Voltage Swell": (
            "WARNING",
            "OVER-VOLTAGE SURGE ALERT: Voltage swell detected. De-energize local capacitor banks immediately. Inspect lightning arresters "
            "and surge suppressors for degradation. Regulate substation step-down transformer tap setting."
        ),
        "Frequency Anomaly": (
            "WARNING",
            "SYNCHRONOUS FREQUENCY ALERT: Grid frequency deviation detected outside safe band (49.8 - 50.2 Hz). Alert regional load dispatch center "
            "(RLDC) for primary governor response and spinning reserve activation."
        ),
        "Overheating": (
            "CRITICAL",
            "THERMAL HAZARD ALERT: Severe transformer/busbar overheating. Check transformer forced-air cooling fan banks and oil circulation pumps. "
            "Perform immediate infrared thermography on cable joints and bushing terminations to prevent thermal runaway."
        )
    }

    def __init__(self):
        # Build fast lookup cache of station metadata
        self.station_lookup = {
            s["station_id"]: s for s in settings.GRID_STATIONS
        }

    def localize(
        self,
        predicted_fault: str,
        confidence: float,
        station_id: str,
        feeder_id: str,
        sensor_id: str,
        telemetry: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Executes hierarchical fault localization and returns detailed maintenance report.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        station_info = self.station_lookup.get(station_id, {
            "name": f"Station {station_id}",
            "region": "Grid Network",
            "nominal_kv": 11.0,
            "lat": 17.4,
            "lon": 78.4
        })

        station_name = station_info.get("name", station_id)
        severity, action_text = self.ACTION_PLAYBOOKS.get(
            predicted_fault,
            ("WARNING", "Unrecognized grid anomaly. Perform immediate comprehensive diagnostic scan.")
        )

        # Dynamic severity escalation for edge conditions
        if telemetry:
            temp = telemetry.get("temperature_c", 0.0)
            nominal_kv = station_info.get("nominal_kv", 11.0) or 11.0
            voltage = telemetry.get("voltage_kv", nominal_kv)
            current = telemetry.get("current_a", 0.0)

            if temp > 105.0 or current > 1500.0 or (voltage / nominal_kv) < 0.36:
                severity = "CRITICAL"

        # Topological Localization Path
        localization_path = f"{station_id} ({station_name}) >> {feeder_id} >> {sensor_id}"

        # Relevant telemetry snippet
        telemetry_summary = {}
        if telemetry:
            telemetry_summary = {
                "voltage_kv": telemetry.get("voltage_kv"),
                "current_a": telemetry.get("current_a"),
                "frequency_hz": telemetry.get("frequency_hz"),
                "temperature_c": telemetry.get("temperature_c"),
                "load_pct": telemetry.get("load_pct"),
                "breaker_status": telemetry.get("breaker_status")
            }

        return {
            "fault_type": predicted_fault,
            "confidence": round(float(confidence), 4),
            "severity": severity,
            "station_id": station_id,
            "station_name": station_name,
            "region": station_info.get("region", "Grid Network"),
            "feeder_id": feeder_id,
            "sensor_id": sensor_id,
            "localization_path": localization_path,
            "latitude": station_info.get("lat"),
            "longitude": station_info.get("lon"),
            "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp),
            "telemetry_summary": telemetry_summary,
            "recommended_action": action_text,
            "localization_type": "SIMULATED_GRID_TOPOLOGY_MAPPING",
            "disclaimer": "Simulated algorithmic grid localization. Requires physical on-site verification."
        }
