import logging
import numpy as np
import skfuzzy as fuzz

class FuzzyRuleMemory:
    def __init__(self):
        self.table = None
        self.logger = logging.getLogger("FuzzyRuleMemory")
        # Real fuzzy membership: temperature and fan_rpm universes
        self.temp_universe = np.arange(0, 121, 1)
        self.fan_universe = np.arange(0, 10001, 1)
        # Memberships
        self.temp_lo = fuzz.trimf(self.temp_universe, [0, 0, 60])
        self.temp_hi = fuzz.trimf(self.temp_universe, [60, 100, 120])
        self.fan_lo = fuzz.trimf(self.fan_universe, [0, 0, 3000])
        self.fan_hi = fuzz.trimf(self.fan_universe, [3000, 10000, 10000])

    def ingest(self, config):
        # Defensive: allow table/list or {rules: [...]}
        if not config:
            self.table = None
            return
        if "rules" in config and isinstance(config["rules"], list):
            self.table = config["rules"]
        elif isinstance(config, list):
            self.table = config
        else:
            self.table = None

    def decide_action(self, state):
        explanations = []
        temp = state.get("temperature") or state.get("cpu_temp") or 0
        fan_rpm = state.get("fan_rpm") or 0
        temp_hi_val = fuzz.interp_membership(self.temp_universe, self.temp_hi, temp)
        fan_hi_val = fuzz.interp_membership(self.fan_universe, self.fan_hi, fan_rpm)
        found = False
        for rule in (self.table or []):
            cond = None
            action = None
            # Flat: {"condition": "...", "action": "..."}
            if "condition" in rule:
                cond = rule["condition"]
                action = rule.get("action")
            # Deep: {"conditions": [...], "actions": [...]}
            elif "conditions" in rule and isinstance(rule["conditions"], list) and rule["conditions"]:
                cond_obj = rule["conditions"][0]
                attr = cond_obj.get("attribute")
                op = cond_obj.get("operator")
                val = cond_obj.get("value")
                cond = f"{attr} {op} {val}"
                if "actions" in rule and isinstance(rule["actions"], list) and rule["actions"]:
                    action = rule["actions"][0].get("type")
            if not cond:
                continue
            is_fuzzy = False
            trace = ""
            # Simple demo: recognize temperature/fan_rpm fuzzy
            if "temperature" in cond and "high" in cond:
                trace = f"Temp={temp}, fuzzy_hi={temp_hi_val:.2f}"
                if temp_hi_val > 0.7:
                    is_fuzzy = True
            if "fan_rpm" in cond and "high" in cond:
                trace = f"FanRPM={fan_rpm}, fuzzy_hi={fan_hi_val:.2f}"
                if fan_hi_val > 0.7:
                    is_fuzzy = True
            explanations.append(
                f"[Fuzzy] Condition '{cond}' {trace} => {is_fuzzy}"
            )
            if is_fuzzy:
                found = True
                return action or "warn", " | ".join(explanations) + f" | [Fuzzy] Action '{action}' matched fuzzy condition '{cond}'"
        if not found:
            explanations.append("[Fuzzy] No fuzzy rule matched.")
        return None, " | ".join(explanations)
