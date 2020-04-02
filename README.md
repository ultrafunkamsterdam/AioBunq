```text

 █████╗ ██╗ ██████╗     ██████╗ ██╗   ██╗███╗   ██╗ ██████╗          
██╔══██╗██║██╔═══██╗    ██╔══██╗██║   ██║████╗  ██║██╔═══██╗         
███████║██║██║   ██║    ██████╔╝██║   ██║██╔██╗ ██║██║   ██║         
██╔══██║██║██║   ██║    ██╔══██╗██║   ██║██║╚██╗██║██║▄▄ ██║         
██║  ██║██║╚██████╔╝    ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝         
╚═╝  ╚═╝╚═╝ ╚═════╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚══▀▀═╝          
                                                                     
 █████╗ ██████╗ ██╗     ██████╗██╗     ██╗███████╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██║    ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝
███████║██████╔╝██║    ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   
██╔══██║██╔═══╝ ██║    ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   
██║  ██║██║     ██║    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║   
╚═╝  ╚═╝╚═╝     ╚═╝     ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   
                                                                     


```

###THIS IS A WORK IN PROGRESS SO NO REAL DOCS OR SETUP AVAILABLE. 


####features:

**To start**
```python
# multiple ways to init, whether a api_key is specified decides 
# whether you are using sandbox or production

from aiobunq.bunq import Bunq
bunq = Bunq()   # sandbox mode
bunq = Bunq(api_key='xxxxxxxxxx') # production mode
bunq = Bunq(debug=True) # sandbox with debug logging

# should always be made first, before using any other methods
await bunq.install()

response = await bunq.post("/user/{userID}/monetary-account/{monetary-accountID}/notification-filter-url", {"some": "data"})
```   
    
**To select a different monetary account**, use bunq.setActiveMonetaryAccount(N) where N is either the index of the local bunq.monetary_accounts list 
OR the real id of the monetary account. It will find out automatically
```python
bunq.setActiveMonetaryAccount(id)
```

**Create a payment request with value, currency, description, redirect_url, and issuer_bic and
returns a dict containing the the Bunqme-Tab and direct iDeal payment link.**

This also triggers notifications for category BUNQME_TAB so you can receive webhook/ipn
responses from Bunq when subscribed.**

```python
await bunq.createBunqMeIdealRequest(
        value, 
        currency="EUR", 
        description="", 
        redirect_url="", 
        ideal_issuer_bic="",
    )
```
example response:
```json
    {
        'uuid': 'SOME-UUID-STRING',
        'status': 'PAYMENT_CREATED',
        'issuer_authentication_url': 'https://r.girogate.de/pi/bunqideal?tx=loooooongstring-and-random-numbers',
        'bunqme_type': 'TAB',
        'bunqme_uuid': 'SOME-OTHER-UUID-STRING'
    }


```

**You can also manually check the status of open requests:**
```python

response = await bunq.checkOpenBunqMeIdealRequests()
```
example response:
```json
[
      { 
        'currency': 'EUR',
        'description': 'Mydescription',
        'amount_paid': 3.0,
        'amount_inquired': 3.0,
        'bunqme_tab_id': 1445}
      ,
      {
        'currency': 'EUR',
        'description': '1234',
        'amount_paid': 0.0,
        'amount_inquired': 10.0,
        'bunqme_tab_id': 1433
      }
]
```


```