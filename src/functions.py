from math import exp, pow
from typing import Callable

VAL_MAX = 100


def _util_thres(risk_profile: str, threshold: float,val_max: int = VAL_MAX) -> Callable:
    factors = {
        "adverse_2": 1 / 18,
        "adverse": 1/9,
        "neutral": 0.3,
        "prone": 2,
    }

    def f(x):
        return 1/(1+exp(factors[risk_profile]*(min(x, val_max)-threshold)))

    def g(x):
        return (f(x)-f(val_max)) / (f(0)-f(val_max))
    return g


def _util_inf(risk_profile : str, val_max: int = VAL_MAX) -> Callable:
    factors = {
        "adverse_2": 3,
        "adverse": 1.5,
        "neutral": 1,
        "prone": 1/1.5,
        "prone_2": 1 / 3,
    }

    def f(x):
        return 1 - pow(max(min(val_max, x), 0) / val_max, factors[risk_profile])
    return f


def _util_inf_free(factor: float, val_max: int = VAL_MAX) -> Callable:
    def f(x):
        return 1 - pow(max(min(val_max, x), 0) / val_max, factor)
    return f
    

def util(type_util: str, **kwargs) -> Callable:
    if type_util == "thresh":
        return _util_thres(**kwargs)
    # elif type_util == "inf":
    #     return _util_inf(**kwargs)
    elif type_util == "inf":
        return _util_inf_free(**kwargs)
    else:
        raise Exception


if __name__ == "__main__":
    thresh_10 = util("thresh",threshold=10,risk_profile="adverse")
    thresh_50 = util("thresh",threshold=50,risk_profile="adverse")
    thresh_90 = util("thresh",threshold=90,risk_profile="adverse")
    inf_adverse_2 = util("inf", risk_profile="adverse_2")
    inf_adverse = util("inf", risk_profile="adverse")
    inf_neutral = util("inf", risk_profile="neutral")
    inf_prone = util("inf", risk_profile="prone")
    inf_prone_2 = util("inf", risk_profile="prone_2")
    data = []
    for i in range(100):
        data.append({
            "x": i,
            "thresh_10": thresh_10(i),
            "thresh_50": thresh_50(i),
            "thresh_90": thresh_90(i),
            "inf_adverse": inf_adverse(i),
            "inf_neutral": inf_neutral(i),
            "inf_prone": inf_prone(i),
            "inf_prone_2": inf_prone_2(i),
            "inf_adverse_2": inf_adverse_2(i),
        })
    import pandas as pd
    pd.DataFrame(data).to_clipboard()
    import pdb;pdb.set_trace()
