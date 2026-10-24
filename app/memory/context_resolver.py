import re


class ContextResolver:
    """Intelligently reconstructs elliptical follow-up queries using prior conversational context."""

    DEFAULT_METRIC_WORDS = [
        "sales", "quantity", "profit", "revenue", "cost", "amount",
        "expenses", "income", "discount", "price", "spend", "score",
        "rating", "age", "headcount", "orders", "salary", "margin", "units"
    ]

    OPERATIONS = {
        "average": ["average", "mean", "avg"],
        "total": ["total", "sum"],
        "maximum": ["maximum", "highest", "max", "largest"],
        "minimum": ["minimum", "lowest", "min", "smallest"],
        "count": ["count", "number of"],
        "distribution": ["distribution", "spread"]
    }

    def resolve(self, question, previous_question, columns=None):
        if previous_question is None:
            return question

        question = question.strip()
        previous_question = previous_question.strip()
        lower_question = question.lower()

        is_group_prefix = False
        extracted_val = None
        for prefix in [
            "what about by ", "how about by ", "now by ", "break down by ",
            "what about the ", "how about the ",
            "what about ", "how about ", "and what about ", "and how about ",
            "and ", "also ", "now show ", "show also "
        ]:
            if lower_question.startswith(prefix):
                if "by " in prefix:
                    is_group_prefix = True
                extracted_val = question[len(prefix):].strip().rstrip("?")
                break

        if extracted_val is None:
            return question

        lower_val = extracted_val.lower()

        # 1. Changing group_by (e.g., 'by Region' or 'Category')
        if is_group_prefix or lower_val.startswith(("by ", "per ", "each ")):
            new_group = re.sub(r"^(by|per|each)\s+", "", extracted_val, flags=re.IGNORECASE).strip()
            return self._replace_or_add_group(previous_question, new_group)

        # 2. Changing operation (e.g., 'average', 'mean', 'max', 'sum')
        for op_canonical, op_synonyms in self.OPERATIONS.items():
            if lower_val in op_synonyms:
                return self._replace_operation(previous_question, op_canonical)

        # 3. Changing filter (e.g., 'for East', 'in Furniture')
        if lower_val.startswith(("for ", "in ", "where ")):
            return self._replace_or_add_filter(previous_question, extracted_val)

        # 4. Changing metric (default behavior)
        return self._replace_metric(previous_question, extracted_val, columns)

    def _replace_or_add_group(self, previous_question, new_group):
        match = re.search(r"\b(by|per|each)\s+([A-Za-z0-9_]+)", previous_question, re.IGNORECASE)
        if match:
            return previous_question[:match.start(2)] + new_group + previous_question[match.end(2):]
        cleaned_prev = previous_question.rstrip("?")
        return f"{cleaned_prev} by {new_group}?"

    def _replace_operation(self, previous_question, new_op):
        for op_canonical, op_synonyms in self.OPERATIONS.items():
            for syn in op_synonyms:
                pattern = r"\b" + re.escape(syn) + r"\b"
                if re.search(pattern, previous_question, re.IGNORECASE):
                    return re.sub(pattern, new_op, previous_question, count=1, flags=re.IGNORECASE)
        return previous_question

    def _replace_or_add_filter(self, previous_question, filter_clause):
        cleaned_prev = previous_question.rstrip("?")
        return f"{cleaned_prev} {filter_clause}?"

    def _replace_metric(self, previous_question, new_value, columns=None):
        # Target metric appears before grouping preposition (by, per, each)
        metric_part = previous_question
        group_match = re.search(r"\b(by|per|each)\b", previous_question, re.IGNORECASE)
        if group_match:
            metric_part = previous_question[:group_match.start()]

        candidates = list(self.DEFAULT_METRIC_WORDS)
        if columns:
            candidates = [c.lower() for c in columns] + candidates

        # 1. Search in pre-group metric section
        prev_lower_metric = metric_part.lower()
        for metric in candidates:
            pattern = r"\b" + re.escape(metric) + r"\b"
            match = re.search(pattern, prev_lower_metric)
            if match:
                start, end = match.span()
                return previous_question[:start] + new_value + previous_question[end:]

        # 2. Fallback to whole question
        prev_lower = previous_question.lower()
        for metric in candidates:
            pattern = r"\b" + re.escape(metric) + r"\b"
            match = re.search(pattern, prev_lower)
            if match:
                start, end = match.span()
                return previous_question[:start] + new_value + previous_question[end:]

        return previous_question