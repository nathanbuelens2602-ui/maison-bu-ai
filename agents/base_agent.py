"""
Maison BU — Base Agent
Shared logic for all marketing agents.
"""
import os
import anthropic
from datetime import datetime
from config.settings import ANTHROPIC_API_KEY, PRIMARY_MODEL, FAST_MODEL, MAX_TOKENS, OUTPUTS
from config.brand_voice import CORE_MANTRAS, PRIME_DIRECTIVE


class BaseAgent:
    def __init__(self, agent_name: str, use_fast_model: bool = False):
        self.agent_name = agent_name
        self.model = FAST_MODEL if use_fast_model else PRIMARY_MODEL
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.output_dir = OUTPUTS.get(agent_name, OUTPUTS["captions"])
        os.makedirs(self.output_dir, exist_ok=True)

    def _call(self, system: str, user_message: str, max_tokens: int | None = None) -> str:
        tokens = max_tokens or MAX_TOKENS.get(self.agent_name, 2048)
        message = self.client.messages.create(
            model=self.model,
            max_tokens=tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text

    def _save(self, content: str, filename: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = filename.replace(" ", "_").lower()
        path = os.path.join(self.output_dir, f"{timestamp}_{safe_name}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def _header(self, title: str) -> str:
        line = "─" * 60
        return f"\n{line}\n  MAISON BU — {title.upper()}\n{line}\n"

    def _soul_test_reminder(self) -> str:
        """Returns the prime directive as a closing reminder in prompts."""
        return f"\n\nREMEMBER — THE PRIME DIRECTIVE:\n{PRIME_DIRECTIVE.strip()}"
