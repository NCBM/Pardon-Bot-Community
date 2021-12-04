"""
Trig protection lib
"""


def trig_protect(kws: tuple[str, ...], det: str):
    for kw in kws:
        if kw in det:
            raise Exception(f"Trigged a Protector from '{det}' with '{kw}'.")
