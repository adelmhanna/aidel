import logging

class ClassicRuleMemory:
    def __init__(self):
        self.table = None
        self.logger = logging.getLogger("ClassicRuleMemory")

    def ingest(self, config):
        # Defensive: handle many LLM output variants
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
        if not self.table:
            return "monitor", "[Classic] No classic rule matched for this demo."
        for rule in self.table:
            expr = None
            action = None
            # Flat: {"condition": "...", "action": "..."}
            if "condition" in rule:
                expr = rule["condition"]
                action = rule.get("action", None)
            # Deep: {"conditions": [ {attr, operator, value} ], "actions": [ {type, message} ]}
            elif "conditions" in rule and isinstance(rule["conditions"], list) and rule["conditions"]:
                cond = rule["conditions"][0]
                attr = cond.get("attribute")
                op = cond.get("operator")
                value = cond.get("value")
                if attr and op and value is not None:
                    # Safe string value formatting
                    if isinstance(value, str):
                        expr = f"{attr} {op} '{value}'"
                    else:
                        expr = f"{attr} {op} {value}"
                if "actions" in rule and isinstance(rule["actions"], list) and rule["actions"]:
                    action = rule["actions"][0].get("type", None)
            if not expr:
                continue
            expr_eval = expr
            # Support state renaming: temperature <-> cpu_temp
            if "temperature" in expr and "temperature" not in state and "cpu_temp" in state:
                expr_eval = expr.replace("temperature", "cpu_temp")
            try:
                result = eval(expr_eval, {}, state)
                explanations.append(
                    f"Classic rule matched: {expr_eval} => {action}" if result else f"Classic rule did not match: {expr_eval}"
                )
                if result:
                    return action or "alert", " | ".join(explanations)
            except Exception as e:
                explanations.append(f"Classic rule eval failed: {expr_eval}: {e}")
        return "monitor", " | ".join(explanations) if explanations else "[Classic] No classic rule matched for this demo."
