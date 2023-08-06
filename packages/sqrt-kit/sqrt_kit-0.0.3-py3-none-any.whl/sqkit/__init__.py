import numpy as np
import pandas as pd
import datetime
import time
import os
import sys
import pickle
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import itertools
from functools import lru_cache
import hashlib
from easydict import EasyDict


# utilities
def load_pkl(F):
    with open(F, 'rb') as f:
        return pickle.load(f)


def save_pkl(data, F):
    with open(F, 'wb') as f:
        pickle.dump(data, f)


def fts(ts, map=False):
    _fts = lambda x: datetime.datetime.fromtimestamp(x / 1000)
    if map:
        return list(map(_fts, ts))
    else:
        return _fts(ts)


def date_search(arr, start: datetime.date, end: datetime.date):
    """backtest res를 start, end로 절사한다."""
    return [i for i in arr if
            i.exit_time >= time.mktime(start.timetuple()) * 1000 and i.exit_time < time.mktime(end.timetuple()) * 1000]


def aggregate_ray_result(ray_result):
    res = list(itertools.chain(*[i.res for i in ray_result]))
    res.sort(key=lambda x: x.entry_time)
    return res


# parse res
class Parser:
    def __init__(self, res, tc=0.001):
        self.res = res
        self.tc = tc
        self.ret = None

    def get_result(self, hide_res=False):
        results = EasyDict(
            ntrades=len(self.res),
            avgRet=self.calc_avgRet(),
            std=self.calc_std(),
            wr=self.calc_wr(),
            rrr=self.calc_rrr(),
            tstat=self.calc_t(),
            distance=self.calc_distance(),
            kelly=self.calc_kelly(),
            avg_holding_time=self.calc_holding_time().mean(),
            res=self.res
        )
        if hide_res:
            results.pop('res')
        return results

    def _calc_ret(self, res, tc):
        return np.array([i.side * (i['exit_price'] / i['entry_price'] - 1) - tc for i in res])

    def calc_ret(self):
        return self._calc_ret(self.res, self.tc)

    def calc_avgRet(self):
        return self.calc_ret().mean()

    def calc_std(self):
        return self.calc_ret().std()

    def calc_t(self):
        rets = self.calc_ret()
        n = len(rets)
        return rets.mean() / rets.std() * np.sqrt(n)

    def calc_holding_time(self):
        return np.array([fts(i['exit_time']) - fts(i['entry_time']) for i in self.res])

    def calc_wr(self):
        rets = self.calc_ret()
        return (rets > 0).mean()

    def calc_rrr(self):
        rets = self.calc_ret()
        profits = rets[rets > 0]
        losses = rets[rets < 0]
        if len(profits) == 0 or len(losses) == 0:
            return np.nan

        return profits.mean() / abs(losses.mean())

    def calc_kelly(self):
        wr = self.calc_wr()
        rrr = self.calc_rrr()
        if rrr is np.nan:
            return np.nan
        return (wr * rrr - (1 - wr)) / rrr

    def calc_distance(self, n=100000, betsize="Kelly"):
        rrr = self.calc_rrr()
        wr = self.calc_wr()
        if type(betsize) == str:
            if betsize.upper() == 'KELLY':
                betsize = self.calc_kelly()

        if betsize < 0:  # betsize가 음수이면 값이 nan임. 그냥 0인걸로..
            return 0

        # 주어진 rrr과 betsize에 따랴 이퀴브릴리엄 winrate 를 반환
        TW = lambda rrr: np.round(-np.log(1 - betsize) / (np.log(1 + betsize * rrr) - np.log(1 - betsize)), 6)

        rrr_space = np.linspace(0, 10, n)
        y = TW(rrr_space)
        least_distance = 9e+100
        for i in range(n):
            dx = rrr_space[i] - rrr
            dy = y[i] - wr
            distance = np.sqrt(dx ** 2 + dy ** 2)
            if distance < least_distance:
                least_distance = distance

        if wr < TW(rrr):
            least_distance *= -1
        return np.round(least_distance * 100, 4)


class BacktestData:
    def __init__(self, raw):
        self.COLS = 'OPENTIME O H L C V CLOSETIME QAV NT TBBAV TBQAV IGNORE'.split(" ")
        self.df = pd.DataFrame(raw, columns=self.COLS).astype(float)
        del self.df['IGNORE']

    def __call__(self):
        return self.df

    def RSI(self, window, ewm, shift):
        self.df = RSI(self.df, window, ewm, shift)
        return self

    def MA(self, window, ewm, shift):
        self.df = MA(self.df, window, ewm, shift)
        return self

    def ATR(self, window, ewm, shift):
        self.df = ATR(self.df, window, ewm, shift)
        return self

    def IBS(self):
        self.df = IBS(self.df)
        return self

    def HPR(self, window, side):
        self.df = HPR(self.df, window, side)
        return self

    def MACD(self, w1, w2, ewm):
        self.df = MACD(self.df, w1, w2, ewm)
        return self

    def OHLCV(self, shift):
        self.df = OHLCV(self.df, shift=shift)
        return self

    #########################
    #########################
    #########################
    #####               #####
    ##### tech-analysis #####
    #####               #####
    #########################
    #########################
    #########################


def OHLCV(df, shift=1):
    for i in "OHLCV":
        df[f'{i}_shift{shift}'] = df[f"{i}"].shift(shift)
    return df


def RSI(df, window=14, ewm=False, shift=0):
    df['prev_C'] = df.C.shift(1)
    df['U'] = df['C'] - df['prev_C']
    df['U'] = df.apply(lambda x: x['U'] if x['U'] > 0 else 0, axis=1)
    df['D'] = df['C'] - df['prev_C']
    df['D'] = df.apply(lambda x: abs(x['D']) if x['D'] < 0 else 0, axis=1)
    if ewm:
        df['AU'] = df['U'].ewm(window).mean()
        df['AD'] = df['D'].ewm(window).mean()
    else:
        df['AU'] = df['U'].rolling(window).mean()
        df['AD'] = df['D'].rolling(window).mean()
    df['RS'] = df['AU'] / df['AD']
    df[f'RSI{window}'] = df['RS'] / (1 + df['RS'])
    del df['prev_C']
    del df['U']
    del df['D']
    del df['AU']
    del df['AD']
    del df['RS']

    if shift:
        df[f'RSI{window}_shift{shift}'] = df[f'RSI{window}'].shift(shift)

    return df


def MA(df, window=24 * 5, ewm=True, shift=0):
    if ewm:
        df[f'MA{window}'] = df['C'].ewm(window).mean()
    else:
        df[f'MA{window}'] = df['C'].rolling(window).mean()

    if shift:
        df[f"MA{window}_shift{shift}"] = df[f'MA{window}'].shift(shift)

    return df


def ATR(df, window, ewm, shift):
    df['C1'] = df['C'].shift(1)
    df['TH'] = df[['C1', 'H']].max(axis=1)
    df['TL'] = df[['C1', 'L']].min(axis=1)
    df['TR'] = df['TH'] - df['TL']
    if ewm:
        df[f'ATR{window}'] = df['TR'].ewm(window).mean()
    else:
        df[f'ATR{window}'] = df['TR'].rolling(window).mean()
    df[f'ATR{window}'] = df[f'ATR{window}'] / df['C']  # 백분율로 표현하기.

    if shift:
        df[f"ATR{window}_shift{shift}"] = df[f'ATR{window}'].shift(shift)

    del df['C1']
    del df['TH']
    del df['TL']
    del df['TR']

    return df


def IBS(df):
    df['IBS'] = (df['C'] - df['L']) / (df['H'] - df['L'])
    return df


def HPR(df, window, side):
    # 나중에 ML 의 label값으로 사용
    df['HPR'] = side * df['C'].pct_change(window).shift(-window)
    return df


def MACD(df, w1, w2, ewm):
    if ewm:
        df['MA1'] = df['C'].ewm(w1).mean()
        df['MA2'] = df['C'].ewm(w2).mean()
    else:
        df['MA1'] = df['C'].rolling(w1).mean()
        df['MA2'] = df['C'].rolling(w2).mean()
    df[f'MACD{w1}_{w2}'] = df['MA1'] / df['MA2'] - 1
    del df['MA1']
    del df['MA2']
    return df