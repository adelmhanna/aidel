import logging
import openai
import httpx
import os
from dotenv import load_dotenv
import re
import json

from memory.raw_text import RawTextMemory
from memory.knowledge_graph import KnowledgeGraphMemory
from memory.vector_store import VectorStoreMemory
from memory.classic_rules import ClassicRuleMemory
from memory.fuzzy_rules import FuzzyRuleMemory
from memory.ml_rules import MLRuleMemory
from memory.procedural import ProceduralMemory
from memory.working_mem import WorkingMemory
from memory.policy import PolicyMemory
from memory.meta import MetaMemory
from memory.audit import AuditMemory

from agent.persona import Persona
from agent.skills import Skills

from events.redfish import RedfishEventProcessor
from tools.external import ExternalTool

class AgentCore:
    def __init__(self, llm_server_url=None, api_key=None, http_client=None):
        load_dotenv()
        self.llm_server_url = llm_server_url or os.getenv("LLM_SERVER_URL", "https://genai-api-dev.dell.com/v1")
        self.api_key = api_key or os.getenv("API_KEY", "no-key")
        self.openai_client = openai.OpenAI(
            base_url=self.llm_server_url,
            api_key=self.api_key,
            http_client=http_client or httpx.Client()
        )
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
        self.logger = logging.getLogger("AgentCore")

        # Memory modules
        self.raw_text = RawTextMemory()
        self.knowledge_graph = KnowledgeGraphMemory()
        self.vector_store = VectorStoreMemory()
        self.classic_rules = ClassicRuleMemory()
        self.fuzzy_rules = FuzzyRuleMemory()
        self.ml_rules = MLRuleMemory()
        self.procedural = ProceduralMemory()
        self.working_mem = WorkingMemory()
        self.policy = PolicyMemory()
        self.meta = MetaMemory()
        self.audit = AuditMemory()
        # Tools
        self.external = ExternalTool()
        # Persona/Skills
        self.persona = Persona()
        self.skills = Skills()
        # Event Processors
        self.event_processors = {
            "redfish": RedfishEventProcessor()
        }

    def process_event(self, event_type, payload):
        processor = self.event_processors.get(event_type)
        if not processor:
            raise ValueError(f"No processor for event type: {event_type}")
        normalized_events = processor.parse(payload)
        for event in normalized_events:
            action, explanation = self.handle_event(event)
            print(f"Processed: {event}")
            print(f"Action: {action}, Explanation: {explanation}")

    def handle_event(self, event):
        # Use LLM to create/update memory modules & get rules
        component_configs = self.query_llm(event)
        for component, config in component_configs.items():
            self._route_to_memory(component, config, event)
        # Hybrid/hierarchical logic
        action, explanation = self.hybrid_decide_action(event)
        self.audit.log_decision(action, explanation, event)
        return action, explanation

    def query_llm(self, event):
        persona_context = json.dumps(self.persona.to_dict(), indent=2)
        prompt = f"""
Persona context for this agent (use to guide all logic and recommendations):
{persona_context}

Return only a valid JSON object for the server event below. No explanations, comments, or code fences. Each component’s configuration must be a dictionary, not a string or other type. The event is:
{json.dumps(event, indent=2)}

The JSON object must have these keys (dicts or lists): 
- raw_text, knowledge_graph, vector_store, classic_rules, fuzzy_rules, ml_rules, procedural, working_mem, meta, audit, external, persona, policy.
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="llama-3-3-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            content = response.choices[0].message.content
            if not content.strip():
                raise ValueError("Empty response from LLM")
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            parsed_content = json.loads(content)
            if not isinstance(parsed_content, dict):
                raise ValueError("Response is not a JSON object")
            self.logger.info(f"LLM response: {json.dumps(parsed_content, indent=2)}")
            return parsed_content
        except Exception as e:
            self.logger.error(f"LLM query failed: {e}")
            return {}

    def _route_to_memory(self, component, config, event):
        try:
            # Route to the correct module; each module handles ingest and structure.
            if component == "raw_text":
                self.raw_text.log(config.get("value") or config.get("text") or str(config))
            elif component == "knowledge_graph":
                self.knowledge_graph.ingest(config)
            elif component == "vector_store":
                self.vector_store.ingest(config)
            elif component == "classic_rules":
                self.classic_rules.ingest(config)
            elif component == "fuzzy_rules":
                self.fuzzy_rules.ingest(config)
            elif component == "ml_rules":
                self.ml_rules.ingest(config)
            elif component == "procedural":
                self.procedural.ingest(config)
            elif component == "working_mem":
                self.working_mem.ingest(config, event)
            elif component == "policy":
                self.policy.ingest(config)
            elif component == "meta":
                self.meta.ingest(config)
            elif component == "audit":
                self.audit.ingest(config)
            elif component == "external":
                self.external.ingest(config)
            elif component == "persona":
                self.persona.update(config)
        except Exception as e:
            self.logger.warning(f"Error routing {component}: {e}")

    def hybrid_decide_action(self, event):
        explanations = []
        matches = []
        state = self.working_mem.get_state(event)
        # Classic rules
        classic_action, classic_expl = self.classic_rules.decide_action(state)
        explanations.append(classic_expl)
        if classic_action != "monitor":
            matches.append(("classic", classic_action, classic_expl))
        # Fuzzy rules
        fuzzy_action, fuzzy_expl = self.fuzzy_rules.decide_action(state)
        explanations.append(fuzzy_expl)
        if fuzzy_action and fuzzy_action != "monitor":
            matches.append(("fuzzy", fuzzy_action, fuzzy_expl))
        # ML rules
        ml_action, ml_expl = self.ml_rules.decide_action(state)
        explanations.append(ml_expl)
        if ml_action and ml_action != "monitor":
            matches.append(("ml", ml_action, ml_expl))
        # Priority
        for rule_type in ["classic", "fuzzy", "ml"]:
            for mtype, action, expl in matches:
                if mtype == rule_type:
                    explanations.append(f"[Decision] Chose action '{action}' from {mtype} rules")
                    return action, " | ".join(explanations)
        # Default
        persona = self.persona
        explanation = (
            f"Default action 'monitor' selected for event {event.get('type','?')} with state {state}. "
            f"No rule match. (Persona: {persona.name}, style: {persona.style}) | " + " | ".join(explanations)
        )
        return "monitor", explanation
