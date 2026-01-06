import lightkurve as lk

lc = lk.search_lightcurve("TIC 141914082", mission="TESS").download()
lc = lc.remove_nans()

lc.plot()