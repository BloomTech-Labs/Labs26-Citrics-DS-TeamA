import pandas as pd 

def get_min(series, rule):
    return series.resample(rule=rule).min()
    
def get_mean(series, rule):
    return series.resample(rule=rule).mean()
    
def get_med(series, rule):
    return series.resample(rule=rule).med()
    
def get_max(series, rule):
    return series.resample(rule=rule).max()