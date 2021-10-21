import datetime
from typing import Dict
from django.test import TestCase
from django.test import Client
from django.urls import reverse

from stocks_api.models import Stock
from stocks_api.models import StockRealTime
from stocks_api.models import Share


class BaseTest(TestCase):

    content_type = "application/json"
    def setUp(self):
        self.client = Client()


class CheckTest(BaseTest):

    def test_check(self):
        good_params  = {"code": "FB"}
        response = self.client.get("/api/check/", 
                    good_params, content_type = self.content_type)

        print("checking with a good code")
        self.assertEqual(response.status_code, 200)

        bad_params = {"code" : "FX"}
        response = self.client.get("/api/check/", 
                    bad_params, content_type = self.content_type)

        print("checking with a bad code")
        self.assertEqual(response.status_code, 400)

 
class TradeShare(BaseTest):

    def test_trade(self):

        #adding FB stock
        stock = Stock.objects.create(symbol="FB")

        good_params_buy = {"symbol": "FB",
                            "action": "buy",
                            "amount": 3
                            }
        response = self.client.post("/api/trade/", good_params_buy, 
                            content_type=self.content_type)
        
        print('trading FB shares')
        self.assertEqual(response.status_code, 200)
        info = response.json()
        self.assertEqual(info["data"]["symbol"], "FB")
        self.assertContains(response, "data")


        params_sell_more_buy = {"symbol": "FB",
                                "action": "sell",
                                "amount": 5
                                }
        response = self.client.post("/api/trade/", params_sell_more_buy, 
                            content_type=self.content_type)

        info = response.json()
        print('trading FB shares sell more buy')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(info["errors"], "not enough shares to sell")


        bad_symbol = {"symbol": "A1",
                            "action": "buy",
                            "amount": 3
                            }
        bad_response = self.client.post("/api/trade/", bad_symbol, 
                            content_type=self.content_type)

        print('trying to trade A1 shares. A1 does not exists')
        self.assertEqual(bad_response.status_code, 400)
        info = bad_response.json()
        self.assertEqual(info["errors"], "A1 does not exists")


        bad_action = {"symbol": "FB",
                            "action": "bu",
                            "amount": 3
                            }
        bad_response = self.client.post("/api/trade/", bad_action, 
                            content_type=self.content_type)

        print("using a bad action <bu>. We have 2 choices: buy and sell")
        self.assertEqual(bad_response.status_code, 400)
        info = bad_response.json()
        self.assertEqual(info["errors"], "invalid action <bu>")
        

class HeldSharesTest(BaseTest):

    def test_held_share(self):

        #add Stock
        stock = Stock.objects.create(symbol="FB")
        share = Share.objects.create(stock=stock,
                                price=100,
                                action='buy',
                                amount=3)

        good_params  = {"code": "FB"}
        response = self.client.get("/api/held-shares/", 
                    good_params, content_type = self.content_type)

        print("getting total shares of FB")
        info = response.json()
        self.assertTrue(info["data"]["total_held_share"] == 3) 
        self.assertEqual(response.status_code, 200)


        print("trying get shares of FBXXX")
        bad_params  = {"code": "FBXXX"}
        response = self.client.get("/api/held-shares/", 
                    bad_params, content_type = self.content_type)

        info = response.json()
        self.assertTrue('errors' in info)
        self.assertEqual(response.status_code, 400)


class CurrentValueOfTheSharesTest(BaseTest):


    def test_current_value_of_the_shares(self):

        #add stock FB
        stock = Stock.objects.create(symbol="FB")
        share = Share.objects.create(stock=stock,
                                price=100,
                                action='buy',
                                amount=3)
        some_price = StockRealTime.objects.create(
                                    stock=stock,
                                    price=100.0
                                    )

        good_params  = {"code": "FB"}
        response = self.client.get("/api/current-value-of-shares/",
                            good_params, content_type=self.content_type)

        info = response.json()
        self.assertEqual(info["data"][0]["realtime price"], 300)
        self.assertEqual(response.status_code, 200)




class CurrentDayReferencePriceTest(BaseTest):

    def test_current_day_reference_price(self):
        #add stock FB
        stock = Stock.objects.create(symbol="FB")
        min_price = StockRealTime.objects.create(
                                    stock=stock,
                                    price=100.0
                                    )

        max_price = StockRealTime.objects.create(
                                    stock=stock,
                                    price=120.0
                                    )

        good_params  = {"code": "FB"}
        response = self.client.get("/api/current-day-reference-prices/",
                            good_params, content_type=self.content_type)

        info = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(info['data'][0]['FB']['avg'], 110)
        

class GetHistoricPriceIntervalTest(BaseTest):

    def test_get_historic_price_interval(self):

        time1 = datetime.datetime(2021,10,20,10,0,0)
        time2 = datetime.datetime(2021,10,20,11,0,0)
        time3 = datetime.datetime(2021,10,20,12,0,0)
        time4 = datetime.datetime(2021,10,20,13,0,0)

        stock = Stock.objects.create(symbol='FB')
        price1 = StockRealTime(stock=stock,
                                price=100,
                                time=time1)
        price2 = StockRealTime(stock=stock,
                                price=120,
                                time=time2)
        price3 = StockRealTime(stock=stock,
                                price=140,
                                time=time3)
        price4 = StockRealTime(stock=stock,
                                price=160,
                                time=time4)
        share = Share.objects.create(stock=stock,
                                price=100,
                                action='buy',
                                amount=3)
        
        response = self.client.get("/api/historic-price-of-stock/") 
        info = response.json()
        self.assertTrue(type(info["data"]["FB"]) == list )
