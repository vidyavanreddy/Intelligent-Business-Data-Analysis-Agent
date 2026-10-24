import unittest
from app.memory.context_resolver import ContextResolver
from app.memory.conversation_memory import ConversationMemory
from app.memory.conversation_context import ConversationContext
from app.memory.followup_detector import FollowUpDetector


class TestAdvancedMemory(unittest.TestCase):

    def setUp(self):
        self.resolver = ContextResolver()
        self.detector = FollowUpDetector()
        self.memory = ConversationMemory()
        self.context = ConversationContext(self.memory)

    def test_dynamic_metric_switch(self):
        """Test resolving metric not in the original 5 hardcoded names."""
        prev_q = "What is the average Annual_Income by Region?"
        follow_q = "What about Total_Spend?"
        resolved = self.resolver.resolve(follow_q, prev_q, columns=["Region", "Annual_Income", "Total_Spend"])
        self.assertEqual(resolved, "What is the average Total_Spend by Region?")

    def test_groupby_switch(self):
        """Test changing grouping dimension in follow-up."""
        prev_q = "What is total Sales by Category?"
        follow_q = "What about by Region?"
        resolved = self.resolver.resolve(follow_q, prev_q)
        self.assertEqual(resolved, "What is total Sales by Region?")

    def test_operation_switch(self):
        """Test changing operation from total to average in follow-up."""
        prev_q = "What is total Sales by Category?"
        follow_q = "What about the average?"
        resolved = self.resolver.resolve(follow_q, prev_q)
        self.assertEqual(resolved, "What is average Sales by Category?")

    def test_filter_followup(self):
        """Test adding filter in follow-up."""
        prev_q = "What is total Sales by Category?"
        follow_q = "What about for East?"
        resolved = self.resolver.resolve(follow_q, prev_q)
        self.assertEqual(resolved, "What is total Sales by Category for East?")

    def test_memory_structured_storage_and_summary(self):
        """Test structured metadata storage and multi-turn session summary."""
        self.memory.add(
            question="What is total Sales?",
            result=125000,
            interpretation="The total Sales is 125,000.00.",
            analysis_plan={"analysis_type": "aggregation", "target_column": "Sales"}
        )
        self.memory.add(
            question="What about Quantity?",
            result=82,
            interpretation="The total Quantity is 82.00.",
            is_follow_up=True,
            original_question="What about Quantity?",
            analysis_plan={"analysis_type": "aggregation", "target_column": "Quantity"}
        )

        last_plan = self.memory.get_last_plan()
        self.assertIsNotNone(last_plan)
        self.assertEqual(last_plan["target_column"], "Quantity")

        summary = self.memory.get_summary()
        self.assertIn("Turn 1:", summary)
        self.assertIn("Turn 2:", summary)
        self.assertIn("125,000.00", summary)

    def test_followup_detector_expanded_patterns(self):
        """Test expanded conversational connectors."""
        self.assertTrue(self.detector.is_follow_up("What about by Department?", "Total Revenue by Region"))
        self.assertTrue(self.detector.is_follow_up("now by Segment", "Total Revenue by Region"))
        self.assertTrue(self.detector.is_follow_up("by Department?", "Total Revenue by Region"))
        self.assertTrue(self.detector.is_follow_up("break down by Department", "Total Revenue"))


if __name__ == "__main__":
    unittest.main()
