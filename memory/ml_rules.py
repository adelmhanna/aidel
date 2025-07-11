import logging
import numpy as np
from sklearn.linear_model import LogisticRegression

class MLRuleMemory:
    def __init__(self):
        self.logger = logging.getLogger("MLRuleMemory")
        # Fake: ML model trained for demo
        self.temp_clf = LogisticRegression()
        # Fit on simple synthetic data (threshold 90 for critical)
        X = np.array([[80], [85], [90], [95], [100]])
        y = np.array([0, 0, 1, 1, 1])  # 1=critical
        try:
            self.temp_clf.fit(X, y)
        except Exception:
            pass
        self.table = None

    def ingest(self, config):
        # Can optionally use config["models"] for more advanced real-world
        self.table = config.get("models") if isinstance(config, dict) and "models" in config else None

    def decide_action(self, state):
        explanations = []
        temp = state.get("temperature") or state.get("cpu_temp")
        if temp is None:
            explanations.append("[ML] No temperature value in state.")
            return None, " | ".join(explanations)
        # Predict with trained model
        try:
            pred_proba = self.temp_clf.predict_proba(np.array([[temp]]))[0, 1]
            prediction = self.temp_clf.predict(np.array([[temp]]))[0]
            explanations.append(f"[ML] LogisticRegression: Temp={temp}, prob={pred_proba:.2f}, pred={'critical' if prediction else 'normal'}")
            if prediction == 1 and pred_proba > 0.8:
                return "raise_critical", " | ".join(explanations)
            elif prediction == 1:
                return "raise_warning", " | ".join(explanations)
        except Exception as e:
            explanations.append(f"[ML] Model error: {e}")
        return None, " | ".join(explanations)
