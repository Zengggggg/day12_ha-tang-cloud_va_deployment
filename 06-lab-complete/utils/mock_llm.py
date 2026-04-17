class MockLLM:
    def chat(self, prompt: str) -> str:
        return (
            "Mock response from LLM. "
            f"Prompt length: {len(prompt)} characters."
        )
