def generate_mutations(code):
    return [
        code.replace("<", "<="),
        code.replace(">", ">="),
        code.replace("+ 1", ""),
        code.replace("and", "or"),
        code.replace("return", "return None #")
    ]

