def dichte_wasser(temperatur):
    dichte = -0.0051 * temperatur**2 + 0.0125 * temperatur + 999.98
    return dichte


def spezif_waermekapazitaet_wasser(temperatur):
    swk = (
        10**-8 * temperatur**4
        - 2 * 10**-6 * temperatur**3
        + 0.0001 * temperatur**2
        - 0.0037 * temperatur
        + 4.2182
    )
    return swk
