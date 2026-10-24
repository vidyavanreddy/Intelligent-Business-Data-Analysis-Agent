class FollowUpDetector:
    """Detects whether a user prompt is an elliptical follow-up referencing prior conversation context."""

    def is_follow_up(self, question, previous_question=None):
        if previous_question is None:
            return False

        question = question.strip().lower()
        previous_question = previous_question.strip().lower()

        if not question:
            return False

        follow_up_phrases = [
            "what about",
            "how about",
            "and what about",
            "and how about",
            "show me also",
            "show also",
            "and quantity",
            "and sales",
            "and profit",
            "what about the",
            "how about the",
            "what about by",
            "how about by",
            "now by",
            "now show",
            "break down by",
            "break it down by"
        ]

        for phrase in follow_up_phrases:
            if question.startswith(phrase):
                return True

        # Short questions (<= 5 words) starting with conversational connectors or prepositions
        words = question.split()
        if len(words) <= 5:
            if question.startswith(("and ", "also ", "what about ", "how about ", "by ", "per ", "in ", "for ")):
                return True

        return False