from math import exp, pow

VAL_MAX = 100


def _util_thres(risk_profile: str, threshold: float,val_max: int = VAL_MAX):
    factors = {
        "adverse": 1/9,
        "neutral": 0.3,
        "prone": 2
    }

    def f(x):
        return 1/(1+exp(factors[risk_profile]*(min(x, val_max)-threshold)))

    def g(x):
        return (f(x)-f(val_max)) / (f(0)-f(val_max))
    return g


def _util_inf(risk_profile : str, val_max: int = VAL_MAX):
    factors = {
        "adverse": 1.5,
        "neutral": 1,
        "prone": 1/1.5
    }

    def f(x):
        return 1 - pow(max(min(val_max, x), 0) / val_max, factors[risk_profile])
    return f


def util(type_util: str, **kwargs):
    if type_util == "thresh":
        return _util_thres(**kwargs)
    elif type_util == "inf":
        return _util_inf(**kwargs)


if __name__ == "__main__":
    bar = util("thresh",threshold=50,risk_profile="adverse")
