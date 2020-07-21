#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
import os
import datetime

import backtrader as bt
import numpy as np
import pandas as pd
from btreport import PerformanceReport

datadir = './data'
logdir = './log'
reportdir = './report'
datafile = 'BTC_USDT_1h.csv'
from_datetime = '2020-01-01 00:00:00'
to_datetime = '2020-04-01 00:00:00'


class SMACross(bt.Strategy):

    params = (
        ('sma_pfast', 10),
        ('sma_pslow', 20),
    )

    def __init__(self):

        if self.p.sma_pslow - self.p.sma_pfast < 5:
            print(f"Skipping for {self.params.__dict__}")
            raise bt.errors.StrategySkipError

        self.sma_fast = bt.ind.SMA(period=self.p.sma_pfast)
        self.sma_slow = bt.ind.SMA(period=self.p.sma_pslow)
        self.sma_crossup = bt.ind.CrossUp(self.sma_fast, self.sma_slow)
        self.sma_crossdown = bt.ind.CrossDown(self.sma_fast, self.sma_slow)

        self.sma_fast.csv = True
        self.sma_slow.csv = True

    def next(self):
        if not self.position:
            if self.sma_crossup:
                self.buy()
        elif self.position:
            if self.sma_crossdown:
                self.close()

    def stop(self,):
        ev = self.broker.getvalue()
        result = {
            "end_value": round(ev, 2),
        }
        result.update(self.p.__dict__)
        print(result)


cerebro = bt.Cerebro()

data = pd.read_csv(
    os.path.join(datadir, datafile), index_col='datetime', parse_dates=True)
data = data.loc[
    (data.index >= pd.to_datetime(from_datetime)) &
    (data.index <= pd.to_datetime(to_datetime))]
datafeed = bt.feeds.PandasData(dataname=data)
cerebro.adddata(datafeed)

cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
cerebro.broker.set_cash(10000)
cerebro.broker.setcommission(commission=0.001)

if __name__ == "__main__":
    cerebro.addstrategy(SMACross)
    params_lst = [str(v)
                  for k, v in cerebro.strats[0][0][0].params.__dict__.items()
                  if not k.startswith('_')]
    resfile = '_'.join([
        os.path.splitext(datafile)[0],
        cerebro.strats[0][0][0].__name__,
        '_'.join(params_lst), from_datetime.split(" ")[0], to_datetime.split(" ")[0]])
    logfile = resfile + '.csv'
    cerebro.addwriter(bt.WriterFile, out=os.path.join(
        logdir, logfile), csv=True)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio,
                        _name="mySharpe",
                        timeframe=bt.TimeFrame.Months)
    cerebro.addanalyzer(bt.analyzers.DrawDown,
                        _name="myDrawDown")
    cerebro.addanalyzer(bt.analyzers.AnnualReturn,
                        _name="myReturn")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer,
                        _name="myTradeAnalysis")
    cerebro.addanalyzer(bt.analyzers.SQN,
                        _name="mySqn")

    cerebro.run()

    plt.rcParams['figure.figsize'] = [13.8, 10]
    fig = cerebro.plot(style='candlestick', barup='green', bardown='red')
    figfile = resfile + '.png'
    fig[0][0].savefig(os.path.join(reportdir, figfile), dpi=480)

    strat = cerebro.runstrats[0][0]
    PerformanceReport(
        strat, outputdir=reportdir, infilename=datafile).generate_pdf_report(filename=resfile + '.pdf')
