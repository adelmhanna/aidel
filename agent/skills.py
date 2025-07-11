class Skills:
    def __init__(self):
        self.skills = {
            "restart_server": [
                "Check server status", "Notify user", "Restart", "Log outcome"
            ],
            "handle_overheating": [
                "Check CPU temperature via Redfish",
                "Increase fan speed",
                "Notify admin if temperature > 80C",
                "Throttle CPU or shutdown if temp > 90C",
                "Log remediation"
            ]
        }

    def list_skills(self):
        return list(self.skills.keys())

    def get_skill_steps(self, skill):
        return self.skills.get(skill, [])
