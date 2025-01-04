import pprint


class Equipment(object):
    def __init__(self):
        pass

def generate_equipments():
    pass

def _weibull(y0, xi, scale):
    def f(t):
        return math.pow(t/xi, scale-1) * math.exp(-math.pow(t/xi, scale))
    g = lambda t: y0 * f(t) / f(1)
    return g

def _exp(k, x0, scale_exp, scale_scalar):
    def f(t):
        return math.pow(t - x0, scale_exp)
    g = lambda t: max(0, scale_scalar * (t - x0)/x0)
    return g

def _failrate_bathtub(infant_xi: float,
                      infant_y0: float,
                      infant_scale: float,
                      wearout_xi: float,
                      wearout_scale_scalar: float,
                      wearout_scale_exp: float,
                      base_y0: float):
    fail_const = base_y0
    fail_early = _weibull(y0=infant_y0, xi=infant_xi, scale=infant_scale)
    fail_wearout = _exp(k=0.001, x0=wearout_xi, scale_exp=wearout_scale_exp, scale_scalar=wearout_scale_scalar)

    def f(t):
        return fail_const + fail_early(t) + fail_wearout(t)
    return f

params = {
    ('infant', 'low', 'infant_y0'): 0.05,
    ('infant', 'low', 'infant_scale'): 0.7,
    ('base', 'low', 'base_y0'): 0.01,
    ('wearout', 'low', 'wearout_scale_scalar'): 0.01,
    ('wearout', 'low', 'wearout_scale_exp'): 1,
    ('infant', 'medium', 'infant_y0'): 0.1,
    ('infant', 'medium', 'infant_scale'): 0.9,
    ('base', 'medium', 'base_y0'): 0.05,
    ('wearout', 'medium', 'wearout_scale_scalar'): 0.05,
    ('wearout', 'medium', 'wearout_scale_exp'): 1,
    ('infant', 'high', 'infant_y0'): 0.15,
    ('infant', 'high', 'infant_scale'): 0.95,
    ('base', 'high', 'base_y0'): 0.1,
    ('wearout', 'high', 'wearout_scale_scalar'): 0.1,
    ('wearout', 'high', 'wearout_scale_exp'): 1,
}


def failrate_bathtub(end_infant: float, start_wearout: float, profile_base: str, profile_infant: str, profile_wearout: str):
    mask = [('infant', profile_infant), ('base', profile_base), ('wearout', profile_wearout)]
    kwargs = {k[-1]: v for (k,v) in params.items() if tuple(k[0:2]) in mask}
    kwargs['infant_xi'] = end_infant
    kwargs['wearout_xi'] = start_wearout
    pprint.pprint(kwargs)
    return _failrate_bathtub(**kwargs)

def _build_linear(x1,x2,y1,y2):
    alpha = (y2 - y1) / (x2 - x1)
    beta = y1 - alpha * x1

    def f(x):
        return alpha * x + beta
    return f

def _build_composed_linear(points:[]):
    xs = list(set([x for (x, y) in points]))
    xs.sort()
    if len(xs) != len(points):
        raise Exception("Non-unique points - Impossible to define multi-linear profile")
    partition = []
    for i in range(1, len(xs)):
        partition.append((xs[i-1], xs[i]))
    indexer = [x for (x, y) in points]
    joints = {(k1, k2): (points[indexer.index(k1)][1], points[indexer.index(k2)][1]) for (k1, k2) in partition}
    functions = {}
    for x1, x2 in joints:
        functions[(x1, x2)] = _build_linear(x1, x2, joints[(x1, x2)][0], joints[(x1, x2)][1])

    def f(x):
        if x < list(functions.keys())[0][0]: return list(functions.values())[0](x)
        if x > list(functions.keys())[-1][1]: return list(functions.values())[-1](x)
        for x1, x2 in functions:
            if x >= x1 and x <= x2:
                return functions[(x1,x2)](x)
    return f


profiles = {
    ('infant', 'low'): 2,
    ('infant', 'medium'): 5,
    ('infant', 'high'): 10,
    ('base', 'low'): 0,
    ('base', 'medium'): 1,
    ('base', 'high'): 2,
    ('wearout', 'low'): 2,
    ('wearout', 'medium'): 5,
    ('wearout', 'high'): 10,
}


def failure_rate(scaler:float, life_expect:int, prof_infant:str,prof_base:str,prof_wearout:str):
    scal_infant = profiles[('infant',prof_infant)]
    scal_base = profiles[('base',prof_base)]
    scal_wearout = profiles[('wearout',prof_wearout)]
    points = [
        (0, scal_infant),
        (life_expect/20, scal_base),
        (life_expect, scal_base),
        (life_expect*2, scal_wearout),
    ]
    print(points)
    f = lambda t: scaler * _build_composed_linear(points)(t)
    return f


if __name__ == "__main__":
    import math
    import plotly.express as px
    import pandas as pd

    foo = ['low', 'medium', 'high']
    bar = []
    for elt1 in foo:
        for elt2 in foo:
            for elt3 in foo:
                bar.append((elt1,elt2,elt3))
    bar = set(bar)

    index = [i for i in range(1, 1000)]
    df = pd.DataFrame(index=index)
    df['x'] = index
    failures = [failure_rate(scaler=1, life_expect=500, prof_infant=x, prof_base=y, prof_wearout=z) for (x, y, z) in bar]
    count = 1
    for rate in failures:
        df['fail. rate {0}'.format(count)] = [rate(x) for x in index]
        count += 1

    df_plot = pd.melt(df,id_vars=['x'], value_vars=[col for col in df.columns if col != "x"])
    fig = px.line(df_plot,x='x',y='value',color='variable')
    fig.show()

