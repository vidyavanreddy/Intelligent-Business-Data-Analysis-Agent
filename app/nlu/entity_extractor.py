import re


def extract_metric(question, columns):
    question_lower = question.lower()

    group_words = ["by", "per", "each"]

    metric_search_text = question_lower
    for word in group_words:
        match = re.search(r"\b" + re.escape(word) + r"\b", question_lower)
        if match:
            pre_text = question_lower[:match.start()]
            if any(re.search(r"\b" + re.escape(c.lower()) + r"\b", pre_text) for c in columns):
                metric_search_text = pre_text
            break

    sorted_cols = sorted(columns, key=lambda c: len(c), reverse=True)

    # Handle relationship questions: between X and Y -> first column is metric
    if "between" in question_lower and "and" in question_lower:
        relationship_part = question_lower.split("between", 1)[1]
        first_part, _ = relationship_part.split("and", 1)
        for column in sorted_cols:
            col_clean = column.lower().replace("_", " ")
            col_raw = column.lower()
            if re.search(r"\b" + re.escape(col_clean) + r"\b", first_part.replace("_", " ")) or \
               re.search(r"\b" + re.escape(col_raw) + r"\b", first_part):
                return column

    numeric_hint_words = [
        "sales", "quantity", "revenue", "profit", "amount", "expenses",
        "income", "spend", "cost", "score", "rating", "age", "headcount",
        "orders", "salary", "discount", "price", "margin", "units"
    ]

    # 1. Prefer numeric columns matching hint words
    for column in sorted_cols:
        col_clean = column.lower().replace("_", " ")
        col_raw = column.lower()
        if any(hint in col_clean for hint in numeric_hint_words):
            if re.search(r"\b" + re.escape(col_clean) + r"\b", metric_search_text.replace("_", " ")) or \
               re.search(r"\b" + re.escape(col_raw) + r"\b", metric_search_text):
                return column

    # 2. Match any column in pre-group search text
    for column in sorted_cols:
        col_clean = column.lower().replace("_", " ")
        col_raw = column.lower()
        if re.search(r"\b" + re.escape(col_clean) + r"\b", metric_search_text.replace("_", " ")) or \
           re.search(r"\b" + re.escape(col_raw) + r"\b", metric_search_text):
            return column

    # 3. Fallback: match any column in the complete question
    for column in sorted_cols:
        col_clean = column.lower().replace("_", " ")
        col_raw = column.lower()
        if re.search(r"\b" + re.escape(col_clean) + r"\b", question_lower.replace("_", " ")) or \
           re.search(r"\b" + re.escape(col_raw) + r"\b", question_lower):
            return column

    return None


def extract_group_by(question, columns):
    question_lower = question.lower()
    sorted_cols = sorted(columns, key=lambda c: len(c), reverse=True)

    # Handle relationship questions: between X and Y
    if "between" in question_lower and "and" in question_lower:
        relationship_part = question_lower.split("between", 1)[1]
        first_part, second_part = relationship_part.split("and", 1)

        for column in sorted_cols:
            col_clean = column.lower().replace("_", " ")
            col_raw = column.lower()
            if re.search(r"\b" + re.escape(col_clean) + r"\b", second_part.replace("_", " ")) or \
               re.search(r"\b" + re.escape(col_raw) + r"\b", second_part):
                return column

    # Handle grouped questions: by, per, each, across
    group_words = ["by", "per", "each", "across"]
    for word in group_words:
        match = re.search(r"\b" + re.escape(word) + r"\b", question_lower)
        if match:
            remaining_text = question_lower[match.end():]
            for column in sorted_cols:
                col_clean = column.lower().replace("_", " ")
                col_raw = column.lower()
                if re.search(r"\b" + re.escape(col_clean) + r"\b", remaining_text.replace("_", " ")) or \
                   re.search(r"\b" + re.escape(col_raw) + r"\b", remaining_text):
                    return column

    return None


OPERATION_KEYWORDS = {
    "sum": ["total", "sum"],
    "mean": ["average", "mean", "avg"],
    "max": ["maximum", "highest", "largest", "max", "peak"],
    "min": ["minimum", "lowest", "smallest", "min"],
    "count": ["count", "number of", "how many"],
    "median": ["median", "middle value"]
}


def extract_operation(question):
    question_lower = question.lower()

    for operation, keywords in OPERATION_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", question_lower):
                return operation

    return None


def extract_filter(question, columns):
    question_lower = question.lower()
    filter_words = ["where", "for", "in", "with", "of"]
    sorted_cols = sorted(columns, key=lambda c: len(c), reverse=True)

    for word in filter_words:
        match = re.search(r"\b" + re.escape(word) + r"\b", question_lower)
        if match:
            remaining_text = question_lower[match.end():].strip()
            if not remaining_text:
                continue

            # "of" is treated as filter only when a non-metric filter column follows
            if word == "of":
                metric = extract_metric(question, columns)
                has_filter_column = any(
                    re.search(r"\b" + re.escape(col.lower()) + r"\b", remaining_text)
                    and (metric is None or col.lower() != metric.lower())
                    for col in columns
                )
                if not has_filter_column:
                    continue

            # Case 1: Filter column is explicitly mentioned
            for column in sorted_cols:
                col_name = column.lower()
                col_pattern = r"\b" + re.escape(col_name) + r"\b"
                if re.search(col_pattern, remaining_text):
                    after_col = re.split(col_pattern, remaining_text, maxsplit=1)[1].strip()
                    after_col = re.sub(r"^(is|equals|equal to|:)\s*", "", after_col).strip()
                    words = after_col.split()
                    if words:
                        value = words[0].strip(".,!?;:\"'")
                        if value:
                            return {"column": column, "value": value}

            # Case 2: Implicit filter value after "for" or "in"
            if word in ["for", "in"]:
                metric = extract_metric(question, columns)
                words = remaining_text.split()
                if words:
                    candidate_value = words[0].strip(".,!?;:\"'")
                    if candidate_value:
                        # Prioritize categorical business columns
                        for column in sorted_cols:
                            if metric and column.lower() == metric.lower():
                                continue
                            if column.lower() in [
                                "category", "region", "department", "segment",
                                "status", "country", "churn_status", "product"
                            ]:
                                return {"column": column, "value": candidate_value}

                        for column in sorted_cols:
                            if metric and column.lower() == metric.lower():
                                continue
                            return {"column": column, "value": candidate_value}

    return None


def extract_time(question, columns):
    time_keywords = [
        "date",
        "time",
        "year",
        "month",
        "day",
        "quarter"
    ]

    question_lower = question.lower()

    for column in columns:
        column_lower = column.lower()

        if column_lower in time_keywords:
            return column

        if column_lower in question_lower and any(
            keyword in column_lower for keyword in time_keywords
        ):
            return column

    return None