class PracCiCalculator:

    @staticmethod
    def div(a: float, b: float) -> float | None:
        if b == 0:
            return None
        else:
            return a / b
