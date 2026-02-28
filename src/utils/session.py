"""
converstaion memory object 
Stores:
history,summary,action_items,decisions,sentiment_timeline,entities
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Turn:
    """Represents one exchange in the conversation."""
    role: str  # 'user' or 'ai'
    text: str
    timestamp: float  # seconds since call start or absolute epoch
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    action_items: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)


class Session:

    def __init__(self, call_id: str, start_time: Optional[float] = None):
        
        self.call_id = call_id
        self.start_time = start_time or time.time()
        self.history: List[Turn] = []
        self.summary: str = ""
        self.action_items: List[str] = []
        self.decisions: List[str] = []
        self.sentiment_timeline: List[tuple] = []  # (timestamp, sentiment)
        self.entities: Dict[str, Any] = {}  # merged entities
        self.business_state = {
            "customer_name": None,
            "phone_number": None,
            "budget": None,
            "location": None,
            "configuration": None,
            "interested_property_ids": [],
            "site_visit_scheduled": False,
            "visit_date": None,
            "lead_score": 0,
            "call_status": "ongoing"
        }
        self.call_stage = "greeting"
        self.insights = {
            "objections": [],
            "interests": [],
            "properties_discussed": [],
            "last_intent": None,
            "last_sentiment": None
        }

    def add_user_message(self, text: str) -> None:
        turn = Turn(
            role='user',
            text=text,
            timestamp=time.time() - self.start_time
        )
        self.history.append(turn)

    def add_ai_message(self, text: str, metadata: Dict[str, Any]) -> None:
        turn = Turn(
            role='ai',
            text=text,
            timestamp=time.time() - self.start_time,
            intent=metadata.get('intent'),
            sentiment=metadata.get('sentiment'),
            entities=metadata.get('entities', {}),
            action_items=metadata.get('action_items', []),
            decisions=metadata.get('decisions', [])
        )
        self.history.append(turn)

        
        # Update aggregated data
        if metadata.get('sentiment'):
            self.sentiment_timeline.append((turn.timestamp, metadata['sentiment']))
        if metadata.get('action_items'):
            for item in metadata.get('action_items', []):
                if item not in self.action_items:
                    self.action_items.append(item)
        if metadata.get('decisions'):
            for decision in metadata.get('decisions', []):
                if decision not in self.decisions:
                    self.decisions.append(decision)
        if metadata.get('entities'):
            new_entities = metadata.get('entities', {})
            if new_entities:
                self.entities.update(new_entities)

            if 'customer_name' in new_entities:
                self.business_state['customer_name'] = new_entities['customer_name']

            if 'budget' in new_entities:
                self.business_state['budget'] = new_entities['budget']

            if 'location' in new_entities:
                self.business_state['location'] = new_entities['location']

            if 'configuration' in new_entities:
                self.business_state['configuration'] = new_entities['configuration']

            if 'property_id' in new_entities:
                if new_entities['property_id'] not in self.business_state['interested_property_ids']:
                    self.business_state['interested_property_ids'].append(new_entities['property_id'])

        # Only increase once when both captured
        if (
            self.business_state["budget"] and
            self.business_state["location"] and
            self.business_state["lead_score"] < 10
        ):
            self.business_state["lead_score"] += 10

        if (
            self.business_state["site_visit_scheduled"] and
            self.business_state["lead_score"] < 40
        ):
            self.business_state["lead_score"] += 30
        # Track last intent & sentiment
        if metadata.get("intent"):
            self.insights["last_intent"] = metadata["intent"]

        if metadata.get("sentiment"):
            self.insights["last_sentiment"] = metadata["sentiment"]

        # Track objections
        if metadata.get("intent") == "objection":
            if text not in self.insights["objections"]:
                self.insights["objections"].append(text)

        # Track properties discussed
        if metadata.get("entities") and metadata["entities"].get("property_id"):
            pid = metadata["entities"]["property_id"]
            if pid not in self.insights["properties_discussed"]:
                self.insights["properties_discussed"].append(pid)

    def get_recent_history(self, n: int = 5) -> List[Turn]:
        """
        Return the last `n` turns (for prompt context).

        Args:
            n: Number of recent turns to return.

        Returns:
            List of Turn objects.
        """
        return self.history[-n:]

    def get_context_for_prompt(self, max_turns: int = 5) -> str:
        recent = self.get_recent_history(max_turns)
        context = f"Conversation summary: {self.summary}\n\nRecent exchanges:\n"
        for turn in recent:
            speaker = "User" if turn.role == 'user' else "Assistant"
            context += f"{speaker}: {turn.text}\n"
        return context

    def update_summary(self, summarizer_func) -> None:
        """
        Update the running summary by calling an external summarizer (LLM).

        Args:
            summarizer_func: A function that takes the full history and returns
                             a condensed summary string.
        """
        # This method is optional; you may call it periodically (e.g., every 3 turns)
        # The actual summarisation is delegated to an LLM call.
        # For now, we just set a placeholder; you'll implement it in main.
        pass

    def to_dict(self) -> Dict:
        """Export session data as a dictionary (for saving)."""
        return {
            'call_id': self.call_id,
            'start_time': self.start_time,
            'duration': time.time() - self.start_time,
            'history': [asdict(t) for t in self.history],
            'summary': self.summary,
            'action_items': self.action_items,
            'decisions': self.decisions,
            'sentiment_timeline': self.sentiment_timeline,
            'entities': self.entities,
            'business_state': self.business_state,
            'call_stage': self.call_stage
        }
    def get_full_transcript(self) -> str:
        lines = []
        for turn in self.history:
            speaker = "User" if turn.role == "user" else "Assistant"
            lines.append(f"{speaker}: {turn.text}")
        return "\n".join(lines)

    def save_to_file(self, filepath: str) -> None:
        """Save session data as JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Session':
        """Load a session from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        session = cls(data['call_id'], data['start_time'])
        # Reconstruct history (we need to convert dicts back to Turn)
        # This is a bit involved; we'll keep it simple for now.
        # For full implementation, you'd loop over history.
        return session

