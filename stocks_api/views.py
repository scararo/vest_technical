from django.views import View
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import check_symbol
from .utils import buy_sell_share

from .utils.filter import get_current_value_of_shares, get_historic_shares_interval, reference_prices_of_stocks
from .utils.filter import get_shares
from .utils.filter import get_held_shares

from .utils.validators import ValidatorView as validator


class ValidateSymbol(View):
    '''
    Part 1.1
    how to use:
    
            requests.get("<host>/api/check/", params={code: <code>})

    output:

        data = {
            "code" : <code>, 
            "status": <"exists" or  "does not exists">
            "realTime_price" :  <price in real time>
            }

        status =  200  -> exists
                  400  -> does not exists
    '''

    def get(self, request, *args, **kwargs):
 
        valid_data = validator(request, 'check_code')

        if not valid_data.is_valid:
            return JsonResponse(valid_data.parser_data, status=400)

        info_after_check_info = check_symbol(**valid_data.parser_data)
        
        response = {}
        if info_after_check_info:
            response["code"] = info_after_check_info["data"]["symbol"]
            response["status"] = "exists"
            response["realTime_price"] = info_after_check_info["data"]["primaryData"]["lastSalePrice"]
            return JsonResponse({"data":response})
        else:
            response["status"] = "does not exists"
            return JsonResponse({"errors" : response}, status=400)


class TradeShare(View):
    '''
    Part 1.2

    how to use:
            requests.post("<host>/api/trade/",
                    headers={"Content-Type":"application/json"},
                    data = json.dumps({ 
                            "symbol": <symbol to -action->,
                            "action": <buy or sell>,
                            "amount": float
                      })

            example:
            requests.post("<host>/api/trade/",
                    headers={"Content-Type":"application/json"},
                    data = json.dumps({ 
                            "symbol": AAPL,
                            "action": "buy",
                            "amount": 3
                      })

    output:
        data : {
                "symbol" : <code of stock>,
                "price" : <when this share was bought>
                "time" :  <time where you bought the share>
        }
 
    with an incorrect code:
        data : {"errors" : "invalid code"} 
        status_code =  400
 
    '''


    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
 
    def post(self, request, *args, **kwargs):

        valid_data = validator(request, 'trade_view')

        if not valid_data.is_valid:
            return JsonResponse(valid_data.parser_data, status=400)

        response = buy_sell_share(**valid_data.parser_data)
        if 'errors' in response:
            return JsonResponse(response, status=400)

        return JsonResponse({'data':response})


class ProfitLoss(View):
    '''
    Part 2.1
    how to use:
            requests.get("<host>/api/balance/", params={code: <code>})
            -params is optional
    
    output:

        data :  {
            "buy" : array with parameters
                        -time_transaction 
                        -symbol
                        -price
                        -action
                        -amount
                        -change in % 
            "sell" : array with parameters
                         -time_transaction 
                        -symbol
                        -price
                        -action
                        -amount
                        -change in %
        status_code = 200


    with an incorrect code:
        data : {"errors" : "invalid code"} 
        status_code =  400
    '''

    def get(self, request, *args, **kwargs):

        response = get_shares(request.GET)

        if 'errors' in response:
            return JsonResponse(response, status=400)

        return JsonResponse({"data" : response})



class HeldShares(View):
    '''
    Part 2.2
    how to use:
            requests.get("<host>/api/held-shares/", params={code: <code>})

    output: 
            data: {"total_held_share"}    
    status_code = 200

    with an incorrect code:
        data : {"errors" : "invalid code"} 
        status_code =  400
 
    '''

    def get(self, request, *args, **kwargs):

        valid_data = validator(request, 'held_shares')

        if not valid_data.is_valid:
            return JsonResponse(valid_data.parser_data, status=400)

        response = get_held_shares(**valid_data.parser_data) 

        if 'errors' in response:
            return JsonResponse(response, status=400)

        return JsonResponse({'data':response})


class CurrentValueOfTheShares(View):
    '''
    Part 2.3
    how to use:
            requests.get("<host>/api/current-value-of-shares/", params={code: <code>})

    output: 
            data: array[] with parameters
                    {
                        "symbol" : <code>,
                        "total shares" :  <quantity of shares you have>,
                        "realtime price" : float()
                        }
    status_code = 200
    '''


    def get(self, request, *args, **kwargs):
        
        response = get_current_value_of_shares()

        return JsonResponse({'data':response})


class CurrentDayReferencePrice(View):
    '''
    Part 2.4
    how to use:
            requests.get("<host>/api/current-day-reference-prices/"}

    output: 
            data: array[] with parameters
                   <code>:  {
                        "min" : "min price of current day",
                        "max" : "max price of current day",
                        "avg" : "average price of current day",
                        }
    status_code = 200
    
    '''

    def get(self, request, *args, **kwargs):
        
        response = reference_prices_of_stocks()

        return JsonResponse({'data': response})


class GetHistoricPriceInterval(View):
    '''
    Part 3
    how to use:
        requests.get("<host>/api/historic-price-of-stock")
    '''
    def get(self, request, *args, **kwargs):
        
        response = get_historic_shares_interval()

        return JsonResponse({'data': response})


    