import unittest
import pandas as pd
from app.agents.agent import AnalysisAgent

class TestNLPQueries(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "Department": ["Sales", "Engineering", "Marketing"],
            "Net_Profit": [120000, 250000, 95000],
            "Revenue": [400000, 600000, 300000]
        })
        self.columns = self.df.columns.tolist()
        self.agent = AnalysisAgent()

    def test_bare_column_query(self):
        """Test bare column name resolves to summary statistics."""
        state = self.agent.run("net_profit", self.df, self.columns)
        self.assertIsNone(state.error)
        self.assertEqual(state.analysis_plan.analysis_type, "summary")
        self.assertIsNotNone(state.execution_result)
        self.assertIn("Net_Profit", state.interpretation)

    def test_bare_column_case_insensitive(self):
        """Test lowercase/uppercase matching."""
        state = self.agent.run("Net_Profit", self.df, self.columns)
        self.assertIsNone(state.error)
        self.assertEqual(state.analysis_plan.analysis_type, "summary")

    def test_column_with_group_by(self):
        """Test metric by category without explicit aggregation defaults to sum."""
        state = self.agent.run("net_profit by Department", self.df, self.columns)
        self.assertIsNone(state.error)
        self.assertEqual(state.analysis_plan.analysis_type, "grouped_aggregation")
        self.assertIn("Engineering", state.interpretation)

    def test_natural_phrasing(self):
        """Test natural phrasing like 'what is net profit'."""
        state = self.agent.run("what is net profit", self.df, self.columns)
        self.assertIsNone(state.error)
        self.assertEqual(state.analysis_plan.analysis_type, "summary")

    def test_unknown_query_guidance(self):
        """Test that completely unrecognizable query returns helpful guidance instead of crashing."""
        state = self.agent.run("completely_random_unknown_words", self.df, self.columns)
        self.assertIsNotNone(state.error)
        self.assertIn("Could not identify a valid column or operation", state.error)
        self.assertIn("Available dataset columns", state.error)

if __name__ == "__main__":
    unittest.main()
