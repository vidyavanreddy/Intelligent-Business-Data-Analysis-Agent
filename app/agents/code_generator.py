def generate_code(plan):

    analysis_type = plan["analysis_type"]
    target_column = plan["target_column"]
    group_by = plan.get("group_by")
    operation = plan.get("operation")
    filter_condition = plan.get("filter")
    time = plan.get("time")

    data = "df"

    # Apply filter
    if filter_condition is not None:
        filter_column = filter_condition["column"]
        filter_value = filter_condition["value"]

        data = (
            f'df[df["{filter_column}"].str.lower() '
            f'== "{filter_value.lower()}"]'
        )

    # ---------------------------------
    # Summary
    # ---------------------------------
    if analysis_type == "summary":

        return f'result = {data}["{target_column}"].describe()'

    # ---------------------------------
    # Distribution
    # ---------------------------------
    elif analysis_type == "distribution":

        return f'result = {data}["{target_column}"].describe()'

    # ---------------------------------
    # Simple Aggregation
    # ---------------------------------
    elif analysis_type == "aggregation":

        if operation == "sum" or operation is None:

            return f'result = {data}["{target_column}"].sum()'

        elif operation == "mean":

            return f'result = {data}["{target_column}"].mean()'

        elif operation == "min":

            return f'result = {data}["{target_column}"].min()'

        elif operation == "max":

            return f'result = {data}["{target_column}"].max()'

        elif operation == "count":

            return f'result = {data}["{target_column}"].count()'

        elif operation == "median":

            return f'result = {data}["{target_column}"].median()'

        else:

            return f'result = {data}["{target_column}"].sum()'

    # ---------------------------------
    # Grouped Aggregation
    # ---------------------------------
    elif analysis_type == "grouped_aggregation":

        if group_by is None:

            raise ValueError(
                "Grouped aggregation requires a grouping column."
            )

        if operation == "sum" or operation is None:

            return (
                f'result = {data}.groupby("{group_by}")'
                f'["{target_column}"].sum()'
            )

        elif operation == "mean":

            return (
                f'result = {data}.groupby("{group_by}")'
                f'["{target_column}"].mean()'
            )

        elif operation == "min":

            return (
                f'result = {data}.groupby("{group_by}")'
                f'["{target_column}"].min()'
            )

        elif operation == "max":

            return (
                f'result = {data}.groupby("{group_by}")'
                f'["{target_column}"].max()'
            )

        elif operation == "count":

            return (
                f'result = {data}.groupby("{group_by}")'
                f'["{target_column}"].count()'
            )

        elif operation == "median":

            return (
                f'result = {data}.groupby("{group_by}")'
                f'["{target_column}"].median()'
            )

        else:

            return (
                f'result = {data}.groupby("{group_by}")'
                f'["{target_column}"].sum()'
            )

    # ---------------------------------
    # Comparison
    # ---------------------------------
    elif analysis_type == "comparison":

        if group_by:
            return (
                f'result = {data}.groupby("{group_by}")'
                f'["{target_column}"].sum()'
            )

        return f'result = {data}["{target_column}"].describe()'

    # ---------------------------------
    # Trend
    # ---------------------------------
    elif analysis_type == "trend":

        if time is None:

            raise ValueError(
                "Trend analysis requires a time column."
            )

        return (
            f'result = {data}.groupby("{time}")["{target_column}"].sum()'
        )

    # ---------------------------------
    # Relationship
    # ---------------------------------
    elif analysis_type == "relationship":

        if group_by is None:

            raise ValueError(
                "Relationship analysis requires two columns."
            )

        return (
            f'result = {data}[["{target_column}", "{group_by}"]].corr()'
        )

    # ---------------------------------
    # Fallback / Unsupported Analysis Type
    # ---------------------------------
    else:

        if target_column:
            return f'result = {data}["{target_column}"].describe()'

        raise ValueError(
            f"Unsupported analysis type: {analysis_type}"
        )