class ConversationMemory:
    """Manages multi-turn conversation memory, execution results, and analytical context."""

    def __init__(self):
        self.history = []

    def add(
        self,
        question,
        result=None,
        interpretation=None,
        is_follow_up=False,
        original_question=None,
        analysis_plan=None,
        metadata=None
    ):
        """Append an analytical turn with full structured context."""
        entry = {
            "question": question,
            "result": result,
            "interpretation": interpretation,
            "is_follow_up": is_follow_up,
            "original_question": original_question,
            "analysis_plan": analysis_plan,
            "metadata": metadata or {}
        }

        self.history.append(entry)

    def get_last(self):
        """Retrieve the most recent conversation entry."""
        if not self.history:
            return None

        return self.history[-1]

    def get_history(self):
        """Return the entire chronological conversation history."""
        return self.history

    def get_previous_question(self):
        """Retrieve the question from the last turn."""
        last = self.get_last()
        if last is None:
            return None
        return last["question"]

    def get_previous_result(self):
        """Retrieve the execution result from the last turn."""
        last = self.get_last()
        if last is None:
            return None
        return last["result"]

    def get_previous_interpretation(self):
        """Retrieve the natural language interpretation from the last turn."""
        last = self.get_last()
        if last is None:
            return None
        return last["interpretation"]

    def get_last_plan(self):
        """Retrieve the structured analysis plan from the last turn."""
        last = self.get_last()
        if last is None:
            return None
        return last.get("analysis_plan")

    def get_summary(self):
        """Generate a concise narrative summary of the multi-turn session."""
        if not self.history:
            return "No previous conversation history."

        summary_lines = []
        for i, entry in enumerate(self.history, start=1):
            q = entry["question"]
            interp = entry["interpretation"] or "Executed successfully"
            summary_lines.append(f"Turn {i}: Q: '{q}' -> {interp}")

        return "\n".join(summary_lines)

    def clear(self):
        """Reset conversation memory."""
        self.history = []