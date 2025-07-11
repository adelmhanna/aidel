from datetime import datetime

class RedfishEventProcessor:
    def parse(self, payload):
        events = []
        if "Events" in payload:
            for ev in payload["Events"]:
                event_type = ev.get("EventType", "Unknown")
                msg = ev.get("Message", "")
                server_id = payload.get("Id", "unknown_server")
                ts = ev.get("EventTimestamp")
                details = {
                    "server_id": server_id,
                    "type": event_type.lower(),
                    "timestamp": ts,
                    "severity": ev.get("Severity", "Unknown"),
                    "message": msg
                }
                if "MessageArgs" in ev and len(ev["MessageArgs"]) >= 2:
                    details["component"] = ev["MessageArgs"][0]
                    try:
                        details["value"] = float(ev["MessageArgs"][1])
                    except Exception:
                        details["value"] = ev["MessageArgs"][1]
                events.append(details)
        elif "Telemetry" in payload:
            server_id = payload.get("ChassisId", "unknown_chassis")
            ts = datetime.now().isoformat()
            for temp in payload["Telemetry"].get("Temperatures", []):
                events.append({
                    "server_id": server_id,
                    "type": "temperature",
                    "timestamp": ts,
                    "component": temp.get("Name"),
                    "temperature": temp.get("ReadingCelsius"),
                    "status": temp.get("Status", {}).get("Health")
                })
            for fan in payload["Telemetry"].get("Fans", []):
                events.append({
                    "server_id": server_id,
                    "type": "fan",
                    "timestamp": ts,
                    "component": fan.get("Name"),
                    "fan_rpm": fan.get("ReadingRPM"),
                    "status": fan.get("Status", {}).get("Health")
                })
        return events
