from typing import Tuple
import requests
import pandas as pd


def get_ob(url: str):
    resp = requests.get(url)
    return resp.json()


def format_ob(data: dict, key: Tuple):
    ob_cb = pd.DataFrame(data)
    bids = ob_cb['bids'].apply(lambda x: pd.Series(
        [x[key[0]], x[key[1]]], index=['prc', 'amt']))
    bids.set_index([pd.Index(['bids']*len(bids)), 'prc'], inplace=True)
    asks = ob_cb['asks'].apply(lambda x: pd.Series(
        [x[key[0]], x[key[1]]], index=['prc', 'amt']))
    asks.set_index([pd.Index(['asks']*len(asks)), 'prc'], inplace=True)
    return pd.concat([bids, asks])


def merge_ob(ob1: pd.DataFrame, ob2: pd.DataFrame):
    ob = pd.concat([ob1, ob2], axis=1, keys=['ob1', 'ob2']) \
        .astype(float) \
        .fillna(0)
    ob = pd.DataFrame(ob[('ob1', 'amt')] + ob[('ob2', 'amt')],
                      columns=['amt'])
    bids = ob.loc['bids', 'amt':].copy().sort_index(ascending=False)
    bids['cumsum'] = bids.cumsum()
    asks = ob.loc['asks', 'amt':].copy().sort_index(ascending=True)
    asks['cumsum'] = asks.cumsum()
    ob = pd.concat([asks, bids], axis=0, keys=['asks', 'bids'])
    return ob.sort_index(ascending=[True, False])


def find_price(ob: pd.Series, thres: float, side: str):
    assert side.lower() in {'buy', 'sell', 'bids', 'asks'}
    side = 'bids' if side.lower() in {'sell', 'bids'} else 'asks'
    ob_side = ob.loc[side]
    ranger = (0, len(ob_side), 1) if side == 'bids' else (
        len(ob_side)-1, -1, -1)
    for i in range(*ranger):
        if ob_side['cumsum'].iat[i] >= thres: 
            return ob_side.index[i]
    else:
        raise Exception("Orderbook too short, price reached limit")


data_cb = get_ob('https://api.pro.coinbase.com/products/BTC-USD/book?level=2')
ob_cb = format_ob(data_cb, key=(0, 1))

data_gm = get_ob('https://api.gemini.com/v1/book/BTCUSD')
ob_gm = format_ob(data_gm, key=('price', 'amount'))

ob = merge_ob(ob_cb, ob_gm)
ob.to_csv('temp_ob.csv')

amount=10
price = find_price(ob, amount, 'buy')
print("{} executed {} BTC, price: {}".format('buy', amount, price))

price = find_price(ob, amount, 'sell')
print("{} executed {} BTC, price: {}".format('sell', amount, price))