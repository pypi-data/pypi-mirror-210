class MassDamperSpringAnalyticalSolution:
    def __init__(self, mass: float, b: float, k: float) -> None: ...
    def SetInitialValue(self, x0: float, xDt0: float) -> None: ...
    def get_x(self, t: float) -> float: ...
    def get_xDt(self, t: float) -> float: ...
    def get_xDtDt(self, t: float) -> float: ...
