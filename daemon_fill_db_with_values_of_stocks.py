import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "technical_test.settings")
application = get_wsgi_application()
from time import sleep

from stocks_api.utils import check_symbol
from stocks_api.utils import create_stock_realtime

_NASQAD_SYMBOLS_ = {'AAPL', 'MSFT', 'AMZN', 'FB',
                    'GOOG', 'TSLA', 'NVDA', 'PYPL',
                    'CMCSA', 'ADBE'}


def main():

    for symbol in _NASQAD_SYMBOLS_:
        response = check_symbol(code = symbol)
        company_name = response["data"]["companyName"]
        str_realtime_price = response["data"]["primaryData"]["lastSalePrice"]
        realtime_price = float(str_realtime_price[1:])
        delta_indicator = response["data"]["primaryData"]["deltaIndicator"]
        
        create_stock_realtime(symbol = symbol,
                                company_name = company_name,
                                price = realtime_price)

if __name__ == '__main__':

    while True:
        try:
            main()
            sleep(20)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            pass
