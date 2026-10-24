import re

INTENT_KEYWORDS = {
    "aggregation": [
        "total", "sum", "average", "mean", "maximum", "minimum",
        "highest", "lowest", "count", "how many", "how much", "amount",
        "peak", "max", "min", "avg", "median"
    ],
    "comparison": [
        "compare", "comparison", "versus", "vs", "difference", "against"
    ],
    "trend": [
        "trend", "over time", "change", "growth", "decline", "historical", "progression"
    ],
    "distribution": [
        "distribution", "spread", "frequency", "histogram", "range"
    ],
    "relationship": [
        "relationship", "correlation", "related", "association", "impact"
    ],
    "summary": [
        "summary", "overview", "describe", "details", "stats", "statistics",
        "show", "give me", "display", "tell me", "what is", "what are", "what was", "about"
    ]
}


def detect_intent(question):
    question_lower = question.lower().strip()

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", question_lower):
                return intent

    return "unknown"
