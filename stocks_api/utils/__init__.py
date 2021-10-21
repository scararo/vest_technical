from django.db.models.fields import related
from django.http import response
import requests
import json
import pytz
from datetime import datetime
from ..models import Share, Stock, StockRealTime
from django.db.utils import OperationalError
from ..models import models 

utc = pytz.utc

session = requests.Session()
session.headers.update({
                'User-Agent':'test-agent',
                'Connection':'keep-alive',
                })

def create_if_not_exists_stock(**kwargs):

    try:
        element = Stock.objects.get(**kwargs)
    except Stock.DoesNotExist as e:
        element = Stock.objects.create(**kwargs)

    return element


def check_symbol(**kwargs):
    """
    input: {"symbol": type(str) }
    
    output: {
            "symbol": type(str),
            "status": options({'exists', 'does not exists'})},
            "realTime_price": type(float)
    """

    symbol = kwargs["code"]
    url = "https://api.nasdaq.com/api/quote/{}/info?assetclass=stocks".format(symbol)

    r_raw = session.get(url)
    response_json = json.loads(r_raw.text)
    status = response_json["status"]["rCode"]

    if status==200:
        return response_json
    else:
        return None
    

def create_stock_realtime(**kwargs):
    """
    input: {"symbol": type(str),
            "price": type(float)
            }
    """

    stock = create_if_not_exists_stock(symbol = kwargs["symbol"])
    stock_realtime = StockRealTime.objects.create( 
                                            stock = stock,
                                            price = kwargs["price"])

            


def buy_sell_share(**kwargs):
    """
    input: {"symbol": type(str),
            "amount" : type(int),
            "action": options {'buy', 'sell'}
            }
    """

    try:
        symbol = kwargs["symbol"] 
        amount = int(kwargs["amount"])
        action = kwargs["action"] 
    except KeyError as e:
        return {"errors" : "{} is required".format(e.args)}
    except ValueError as e:
        return {"errors": e.args}

    if not action in ('buy', 'sell'):
        return {"errors": "invalid action <{}>".format(action)}
    if amount < 0:
        return {"errors": "amount should not be less 0"}

    info_from_symbol = check_symbol(code=symbol)

    if not info_from_symbol:
        return {"errors": "{} does not exists".format(symbol)}

    str_real_price = info_from_symbol["data"]["primaryData"]["lastSalePrice"]
    real_price = float(str_real_price[1:])



    if action=='sell' and not validate_how_many_share_can_be_sold(
                                            symbol=symbol,
                                            amount=amount):
        return {"errors" : "not enough shares to sell"}

    try:
        share = add_share(symbol = symbol, 
                        action=action,price = real_price,
                        amount = amount)
    except Stock.DoesNotExist:
        return {"errors" : "{} invalid code".format(symbol)}

    return {"symbol": symbol, 
            "price": real_price, 
            "time": share.time_transaction}


def add_share(**kwargs):
    """
    input : {symbol: type(str),
             action: option {'buy', 'sell'},
             price: type(float),
             amount: type(int)
             }
    """
    stock = Stock.objects.get(symbol=kwargs["symbol"])
    kwargs.pop('symbol')
    kwargs["stock"] = stock
    share = Share.objects.create(**kwargs)
    return share

#
def validate_how_many_share_can_be_sold(**kwargs):
    """
    input : {
        "symbol": type(str),
        "amount": type(int)
    }
    """

    all_shares_buy = Share.objects.filter(
                            stock__symbol=kwargs["symbol"],
                            action="buy")

    all_shares_sell = Share.objects.filter(
                            stock__symbol=kwargs["symbol"],
                            action="sell")


    quantity_buy = 0
    for share in all_shares_buy.all():
        quantity_buy += share.amount

    quantity_sell = 0
    for share in all_shares_sell.all():
        quantity_sell += share.amount

    return kwargs["amount"] <= (quantity_buy - quantity_sell)
    