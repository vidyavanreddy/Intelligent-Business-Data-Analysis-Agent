from .intent_detector import detect_intent
from .entity_extractor import (
    extract_metric,
    extract_group_by,
    extract_operation,
    extract_filter,
    extract_time
)


def parse_question(question, columns):
    intent = detect_intent(question)
    metric = extract_metric(question, columns)
    group_by = extract_group_by(question, columns)
    operation = extract_operation(question)
    filter_condition = extract_filter(question, columns)
    time = extract_time(question, columns)

    # Intelligent intent resolution for natural phrasing and bare column queries
    if intent == "unknown":
        if time and ("trend" in question.lower() or "over" in question.lower() or "growth" in question.lower()):
            intent = "trend"
        elif group_by and metric:
            intent = "aggregation"
            if operation is None:
                operation = "sum"
        elif metric:
            if operation:
                intent = "aggregation"
            else:
                intent = "summary"
        elif group_by:
            intent = "aggregation"
            if operation is None:
                operation = "count"

    # Default operation if aggregation has no explicit operator
    if intent == "aggregation" and operation is None:
        operation = "sum"

    return {
        "question": question,
        "intent": intent,
        "metric": metric,
        "operation": operation,
        "group_by": group_by,
        "filters": filter_condition,
        "time": time
    }
