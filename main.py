from agent.core import AgentCore
import httpx

if __name__ == "__main__":
    agent = AgentCore(http_client=httpx.Client(verify=False))
    poweredge_redfish_event = {
        "@odata.type": "#Event.v1_2_0.Event",
        "Id": "PE_server1",
        "Name": "PowerEdge Event",
        "Events": [
            {
                "EventId": "E1001",
                "EventType": "Alert",
                "EventTimestamp": "2025-07-10T14:21:00Z",
                "Severity": "Critical",
                "Message": "Temperature threshold exceeded",
                "MessageArgs": ["CPU1", "88"],
                "OriginOfCondition": {
                    "@odata.id": "/redfish/v1/Chassis/System.Embedded.1/Thermal"
                }
            }
        ]
    }
    poweredge_redfish_telemetry = {
        "ChassisId": "System.Embedded.1",
        "Telemetry": {
            "Temperatures": [
                {
                    "Name": "CPU1 Temp",
                    "ReadingCelsius": 91,
                    "Status": {"Health": "Warning"}
                }
            ],
            "Fans": [
                {
                    "Name": "Fan1",
                    "ReadingRPM": 1800,
                    "Status": {"Health": "OK"}
                }
            ]
        }
    }
    print("\n--- Ingesting PowerEdge Redfish Event ---")
    agent.process_event("redfish", poweredge_redfish_event)
    print("\n--- Ingesting PowerEdge Redfish Telemetry ---")
    agent.process_event("redfish", poweredge_redfish_telemetry)
