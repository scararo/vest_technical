from django.db import models

class Stock(models.Model):

    symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=50)


class StockRealTime(models.Model):

    stock = models.ForeignKey(Stock,
                        null=False,
                        blank=False,
                        on_delete=models.CASCADE)
    time =  models.DateTimeField(auto_now_add=True)
    price = models.FloatField(max_length=10)

    def to_dict(self):
        return {
                'stock': self.stock.symbol,
                'time': self.time,
                'price': self.price
                    }

class Share(models.Model):

    key_choices = (
            ('sell','sell'),
            ('buy','buy')
            )
    time_transaction = models.DateTimeField(auto_now_add=True)
    stock = models.ForeignKey(Stock,
                        null=False,
                        blank=False,
                        on_delete=models.CASCADE)

    price = models.FloatField(max_length=10)
    action = models.CharField(max_length=5, 
                        choices=key_choices) 
    amount = models.IntegerField(default=0)
    

    def to_dict(self, **kwargs):

        time_str = self.time_transaction.strftime("%Y-%m-%d %H:%M:%S")
        output =  {
            'time_transaction' : time_str,
            'symbol': self.stock.symbol,
            'price': self. price,
            'action': self.action,
            'amount': self.amount
          }

        if kwargs.get('actual_price', None):
            actual_price = kwargs['actual_price']
            difference_between_prices = round((self.price - actual_price)*100./self.price,2)
            output["change"] = "{} %".format(difference_between_prices)

        return output
