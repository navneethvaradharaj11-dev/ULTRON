import math


def safe_calculator(expression: str) -> str:
    """Safe math evaluator supporting basic arithmetic and math functions."""
    allowed_names = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan, "sqrt": math.sqrt,
        "log": math.log, "pi": math.pi, "e": math.e, "abs": abs, "pow": math.pow
    }
    clean_expr = expression.replace("^", "**")
    # Verify no illegal characters or dangerous attributes
    for token in ["__", "import", "exec", "eval", "open", "os", "sys", "subprocess"]:
        if token in clean_expr:
            raise ValueError(f"Prohibited expression element: '{token}'")

    compiled = compile(clean_expr, "<string>", "eval")
    for name in compiled.co_names:
        if name not in allowed_names:
            raise NameError(f"Use of name {name!r} is not allowed")

    result = eval(compiled, {"__builtins__": {}}, allowed_names)
    return str(result)
