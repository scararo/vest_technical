from datetime import datetime, timedelta
from ..models import Share, Stock
from ..models import StockRealTime
from django.db.models import Avg, Max, Min

def get_last_price_for_all_stocks(**kwargs):
    '''
    input : optional { code : type(str)}
    '''

    output = {}
    if kwargs.get('code'):
        stock = Stock.objects.get(symbol = kwargs['code'])
        all_data_from_stock = StockRealTime.objects.filter(stock=stock)
        stock_realtime = all_data_from_stock.order_by('-time').first()
        output[stock.symbol] = stock_realtime.price

    else:
        all_stocks = Stock.objects.all()
        for stock in all_stocks:
            all_data_from_stock = StockRealTime.objects.filter(stock=stock)
            stock_realtime = all_data_from_stock.order_by('-time').first()
            output[stock.symbol] = stock_realtime.price
        
    return output


def get_shares(args):
    '''
    input : optional <code>
    '''
    code = None
    if args: 
        if 'code' in args:
            code = args['code']
        else:
            return {"errors" : "'code' missing field in query"}

    try:
        all_last_prices = get_last_price_for_all_stocks(code = code)
    except Stock.DoesNotExist:
        return {"errors" : "invalid code {}".format(code)}

    all_shares = Share.objects.all()
    shares_buy=[]
    shares_sell=[]
    
    for share in all_shares:

        symbol = share.stock.symbol
        try:
            actual_price_share = all_last_prices[symbol]
        except KeyError:
            continue

        if share.action == 'buy':
            shares_buy.append(share.to_dict(actual_price=actual_price_share))

        if share.action == 'sell':
            shares_sell.append(share.to_dict(actual_price=actual_price_share))

    output = {
            'buy': shares_buy,
            'sell': shares_sell
            }

    return output


def get_held_shares(**kwargs):
    """
    input: {
            code: type(str)
            }
    """

    try:
        stock = Stock.objects.get(symbol = kwargs["code"])
    except Stock.DoesNotExist:
        return {"errors" :  "invalid code {}".format(kwargs["code"])}

    all_shares_by_code = Share.objects.filter(stock = stock)
   
    total_held_share = 0

    for share in all_shares_by_code.all():

        if share.action == 'buy':
            total_held_share += share.amount
        
        elif share.action == 'sell':
            total_held_share -= share.amount

    return {'total_held_share' : total_held_share}



def get_current_value_of_shares(**kwargs):

    all_last_prices = get_last_price_for_all_stocks()

    all_shares = Share.objects.all()

    output = []     
    for share in all_shares:
        
        shares_buy_total = 0
        shares_sell_total = 0
        symbol = share.stock.symbol
        actual_price_share = all_last_prices[symbol]

        if share.action == 'buy':
            shares_buy_total += share.amount

        if share.action == 'sell':
            shares_sell_total += share.amount

        total_shares_available = shares_buy_total - shares_sell_total

        if total_shares_available > 0:
            output.append({'symbol' : symbol,
                            'total shares' : total_shares_available,
                            'realtime price' : total_shares_available*actual_price_share })

    return output


def reference_prices_of_stocks():

    all_stocks = Stock.objects.all()
    today = datetime.today()

    output = []

    for stock in all_stocks:
        
        stocks_real_time = StockRealTime.objects.filter(stock=stock)
        stocks_today = stocks_real_time.filter(time__year = today.year,
                                            time__month = today.month,
                                            time__day = today.day)
        min_price = stocks_today.aggregate(Min('price'))
        max_price = stocks_today.aggregate(Max('price'))
        avg_price = stocks_today.aggregate(Avg('price'))

        output.append({stock.symbol : {
                            'min' : min_price['price__min'],
                            'max' : max_price['price__max'],
                            'avg' : avg_price['price__avg'],
                        }})

    return output


def get_historic_shares_interval():

    all_stocks = Stock.objects.all()

    with_shares = set()

    for stock in all_stocks:
        
        held_shares = get_held_shares(code=stock.symbol)

        if held_shares["total_held_share"] > 0:

            with_shares.add(stock.symbol)

    today = datetime.today()

    output = {}

    for symbol in with_shares:

        output[symbol] = []

        hour_to_filter = today.replace(minute=0, second=0, microsecond=0) 
        stock = Stock.objects.get(symbol = symbol)
        all_data_from_stock = StockRealTime.objects.filter(stock=stock)
        
        data_ordered_by_time = all_data_from_stock.order_by('-time')

        while True:

            hour_to_filter_less_1 = hour_to_filter - timedelta(hours=1)
            
            data_filtered_by_hour = data_ordered_by_time.filter(
                        time__year=hour_to_filter.year,
                        time__month=hour_to_filter.month,
                        time__day=hour_to_filter.day,
                        time__hour=hour_to_filter.hour,
                        )

            try:
                output[symbol].append([data_filtered_by_hour.first().time,
                                data_filtered_by_hour.first().price])
            except AttributeError:
                pass

            data_ordered_by_time = data_ordered_by_time.filter(time__lte = hour_to_filter)
            hour_to_filter -= timedelta(hours=1)

            if not data_ordered_by_time:
                break

    return output
