# Vest Technical test using python

## pre-requirements

For this project I used sqlite3 in Debian Buster. I used a virtual
environment

<code>

    > apt-get install sqlite3

    > python3 -m venv venv

    > source ./venv/bin/activate

    > pip install -r requirements
</code>


## how to start 

<code>

    > python manage.py makemigrations
    > python manage.py migrate
    > python manage.py runserver

</code>

## daemon that fill db with stock prices. This run parallel

<code>

    > python daemon_fill_db_with_values_of_stocks.py

</code>

This script could be coded using Celery. With Celery I can
parallelize requests to the server.

I am not comfortable with this solution because we don't have
a constant data rate. For example, a rate 20 seg.
I should prefer requests to official server

## Views

stocks_api/views.py contains project's views. Here I explain
how it works


## Endpoints
Each endpoint answer

* "api/check/"  -> part1.1
* "api/trade/"  -> part1.2
* "api/balance/"  -> part2.1
* "api/held-shares/"  -> part2.2
* "api/current-value-of-shares/"  -> part2.3
* "api/current-day-reference-prices/"  -> part2.4
* "api/historic-price-of-stock/"  -> part3.1


## how to use (package requests of python. You can use curl too)

* "api/check/" 

<code>

    requests.get('<host>/api/check/', params={code:'FB'})

</code>

* "api/trade/"  

<code>

    requests.post('<host>/api/trade/',
                headers={"Content-Type":"application/json"},
                data = json.dumps(
                    {
                        "symbol" : "FB",
                        "action" : "buy",
                        "amount" :  3
                    })
                )

</code>

* "api/balance/" 

<code>

     requests.get("<host>/api/balance/"})
     requests.get("<host>/api/balance/", params={code: 'FB'})

</code>


* "api/held-shares/"

<code>

    requests.get("<host>/api/held-shares/", params={code: 'FB'})

</code>

* "api/current-value-of-shares/

<code>

    requests.get("<host>/api/current-value-of-shares/", params={code:'FB')

</code>

* "api/current-day-reference-prices/" 

<code>

    requests.get("<host>/api/current-day-reference-prices/"}

</code>


* "api/historic-price-of-stock/"

<code>
        
    requests.get("<host>/api/historic-price-of-stock")

</code>


## TESTING

For testing

<code>

    python manage.py test tests/

</code>

