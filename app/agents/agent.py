import pandas as pd

try:
    from .agent_state import AgentState
    from ..nlu.question_parser import parse_question
    from .planner import create_analysis_plan
    from .code_generator import generate_code
    from .code_validator import validate_code
    from ..analysis.executor import execute_code
    from ..visualization.visualizer import create_visualization
    from .interpreter import ResultInterpreter

except ImportError:
    from agents.agent_state import AgentState
    from nlu.question_parser import parse_question
    from agents.planner import create_analysis_plan
    from agents.code_generator import generate_code
    from agents.code_validator import validate_code
    from analysis.executor import execute_code
    from visualization.visualizer import create_visualization
    from agents.interpreter import ResultInterpreter

class AnalysisAgent:
    def __init__(self):
        self.state = AgentState()
        self.interpreter = ResultInterpreter()

    def reset(self):
        self.state = AgentState()

    def recover(self, execution):
        self.state.recovery_attempted = True

        if execution["error_type"] == "MissingResult":
            self.state.error = (
                "Analysis failed because the generated code "
                "did not produce a result."
            )
        elif execution["error_type"] == "KeyError":

            columns = self.state.dataset.columns.tolist()

            self.state.error = (
                "Analysis failed because the generated code "
                "used a column that does not exist. "
                f"Available columns: {', '.join(columns)}."
            )
        else:
            self.state.error = execution["error"]

        return False

    def run(self, question, dataset, columns):
        self.reset()

        self.state.question = question
        self.state.dataset = dataset

        self.state.nlu_result = parse_question(question, columns)

        self.state.analysis_plan = create_analysis_plan(
            self.state.nlu_result
        )

        if self.state.analysis_plan.analysis_type == "unknown" or (
            self.state.analysis_plan.target_column is None and self.state.analysis_plan.group_by is None
        ):
            first_col = columns[0] if columns else "Sales"
            second_col = columns[1] if len(columns) > 1 else first_col
            self.state.error = (
                f"Could not identify a valid column or operation in '{question}'.\n\n"
                f"Available dataset columns: {', '.join(columns)}.\n\n"
                "Suggested question formats:\n"
                f"• '{first_col}' (overview/summary)\n"
                f"• 'Total {first_col}' or 'Average {first_col}'\n"
                f"• '{first_col} by {second_col}'\n"
                f"• 'Show distribution of {first_col}'\n"
                f"• 'Relationship between {first_col} and {second_col}'"
            )
            self.state.error_type = "unrecognized_query"
            return self.state

        try:
            self.state.generated_code = generate_code(
                self.state.analysis_plan.to_dict()
            )
        except Exception as e:
            self.state.error = str(e)
            self.state.error_type = "generation_error"
            self.state.recovery_attempted = True
            return self.state
        
        if not validate_code(self.state.generated_code):
            self.state.error = "Generated code failed validation."
            self.state.error_type = "validation_error"
            return self.state

        execution = execute_code(
            self.state.generated_code,
            self.state.dataset
        )

        self.state.execution_result = execution

        if not execution["success"]:
            self.state.error_type = "execution_error"
            self.state.specific_error_type = execution["error_type"]

            self.recover(execution)

            retry_execution = execute_code(
                self.state.generated_code,
                self.state.dataset
            )

            self.state.execution_result = retry_execution

            if not retry_execution["success"]:
                self.state.specific_error_type = retry_execution["error_type"]
                self.recover(retry_execution)
                return self.state

            execution = retry_execution
        
        plan_dict = self.state.analysis_plan.to_dict()
        analysis_type = self.state.analysis_plan.analysis_type
        target_col = self.state.analysis_plan.target_column
        group_col = self.state.analysis_plan.group_by
        operation = self.state.analysis_plan.operation
        filter_cond = self.state.analysis_plan.filter
        result_val = execution["result"]

        if analysis_type == "grouped_aggregation":
            self.state.interpretation = self.interpreter.interpret_grouped(
                result_val,
                operation,
                group_col,
                target_col
            )
            insight = self.interpreter.generate_grouped_insight(
                result_val,
                operation,
                group_col,
                target_col
            )
            self.state.business_insight = (
                self.interpreter.combine_interpretation_and_insight(
                    self.state.interpretation,
                    insight
                )
            )

            try:
                if isinstance(result_val, pd.Series):
                    visualization_data = result_val.reset_index()
                    if len(visualization_data.columns) >= 2:
                        visualization_data.columns = [group_col, target_col]
                elif isinstance(result_val, pd.DataFrame):
                    visualization_data = result_val.reset_index() if result_val.index.name else result_val.copy()
                else:
                    visualization_data = pd.DataFrame(result_val)

                self.state.visualization = create_visualization(
                    visualization_data,
                    "comparison",
                    group_col,
                    target_col
                )
            except Exception:
                self.state.visualization = None

        elif analysis_type == "trend":
            self.state.interpretation = self.interpreter.interpret_trend(
                result_val,
                target_col
            )
            insight = self.interpreter.generate_trend_insight(
                result_val,
                target_col
            )
            self.state.business_insight = (
                self.interpreter.combine_interpretation_and_insight(
                    self.state.interpretation,
                    insight
                )
            )

            try:
                visualization_data = result_val.reset_index() if hasattr(result_val, "reset_index") else pd.DataFrame(result_val)
                self.state.visualization = create_visualization(
                    visualization_data,
                    "trend",
                    self.state.analysis_plan.time,
                    target_col
                )
            except Exception:
                self.state.visualization = None

        elif analysis_type == "relationship":
            self.state.interpretation = self.interpreter.interpret_relationship(
                result_val,
                target_col,
                group_col
            )
            corr_val = None
            if hasattr(result_val, "loc") and target_col in result_val.index and group_col in result_val.columns:
                corr_val = result_val.loc[target_col, group_col]

            insight = self.interpreter.generate_relationship_insight(
                corr_val,
                target_col,
                group_col
            )
            self.state.business_insight = (
                self.interpreter.combine_interpretation_and_insight(
                    self.state.interpretation,
                    insight
                )
            )

            try:
                visualization_data = self.state.dataset[[group_col, target_col]]
                self.state.visualization = create_visualization(
                    visualization_data,
                    "relationship",
                    group_col,
                    target_col
                )
            except Exception:
                self.state.visualization = None

        else:
            self.state.interpretation = self.interpreter.interpret_from_plan(
                result_val,
                plan_dict
            )
            insight = self.interpreter.generate_business_insight(
                self.state.interpretation,
                operation,
                target_col,
                analysis_type,
                group_col,
                filter_cond
            )
            self.state.business_insight = (
                self.interpreter.combine_interpretation_and_insight(
                    self.state.interpretation,
                    insight
                )
            )

            if analysis_type == "distribution":
                try:
                    visualization_data = self.state.dataset[[target_col]]
                    self.state.visualization = create_visualization(
                        visualization_data,
                        "distribution",
                        y_column=target_col
                    )
                except Exception:
                    self.state.visualization = None

        return self.state