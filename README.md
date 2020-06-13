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
# ASYNC BUNQ API CLIENT FOR PYTHON 3+

### THIS IS A WORK IN PROGRESS. BESIDES SOME BASICS THERE IS NO DOCUMENTATION CURRENTLY 




<br>
<br>


# Quickstart #

```python
from aiobunq import createClient
client = createClient(None)   # sandbox mode
```

```python
from aiobunq import createClient
client = createClient('SOME_API_KEY') # production mode
```

# Create a session to Bunq
```ipython
In [1]: from aiobunq import createClient

In [2]: client = createClient()
Using sandbox environment

In [3]: await client.logon()

In [4]: client.monetary_accounts
Out[4]: [<[MonetaryAccountBank](id=58598, status=ACTIVE, iban=NL26BUNQ2205534769, balance=0.00, 166a5624-307c-4449-82f6-3c572171489f)>]

In [5]: client.user
Out[5]: 
{'id': 58385,
 'created': '2020-06-13 09:04:54.787067',
 'updated': '2020-06-13 09:04:54.794507',
 'alias': [{'type': 'PHONE_NUMBER',
   'value': '+31619094108',
   'name': '+31619094108'},
  {'type': 'EMAIL',
   'value': 'test+97120116-dfbe-4692-94ea-6a78aeed146a@bunq.com',
   'name': 'test+97120116-dfbe-4692-94ea-6a78aeed146a@bunq.com'}],
 'avatar': {'uuid': '9debf55b-70b1-4d43-8d51-d6e7bd42fb5b',
  'image': [{'attachment_public_uuid': '4b7e0d1d-9167-48ac-990a-70e342c87812',
    'height': 126,
    'width': 200,
    'content_type': 'image/jpeg'}],
  'anchor_uuid': '3180005f-4bc3-489a-b757-f825c32277ad'},
 'status': 'ACTIVE',
 'sub_status': 'NONE',
 'public_uuid': '3180005f-4bc3-489a-b757-f825c32277ad',
 'display_name': 'N. Lawrence-Storm',
 'public_nick_name': 'Nancee',
 'language': 'fr_FR',
 'region': 'fr_FR',
 'session_timeout': 604800,
 'daily_limit_without_confirmation_login': {'currency': 'EUR',
  'value': '250.00'},
 'relations': [],
 'notification_filters': [{'notification_delivery_method': 'PUSH',
   'category': 'BANK_SWITCH_SERVICE'},
  {'notification_delivery_method': 'PUSH',
   'category': 'BANK_SWITCH_SERVICE_PAYMENT'},
  {'notification_delivery_method': 'PUSH', 'category': 'BUNQME_TAB'},
  {'notification_delivery_method': 'PUSH', 'category': 'BUNQME_FUNDRAISER'},
  {'notification_delivery_method': 'PUSH',
   'category': 'CARD_TRANSACTION_FAILED'},
  {'notification_delivery_method': 'PUSH',
   'category': 'CARD_TRANSACTION_SUCCESSFUL'},
  {'notification_delivery_method': 'PUSH', 'category': 'CO_OWNER_INVITE'},
  {'notification_delivery_method': 'PUSH', 'category': 'DRAFT_PAYMENT'},
  {'notification_delivery_method': 'PUSH', 'category': 'FEATURE_ANNOUNCEMENT'},
  {'notification_delivery_method': 'PUSH', 'category': 'PACK'},
  {'notification_delivery_method': 'PUSH', 'category': 'IDEAL'},
  {'notification_delivery_method': 'PUSH', 'category': 'SOFORT'},
  {'notification_delivery_method': 'PUSH', 'category': 'INVITE_USER'},
  {'notification_delivery_method': 'PUSH',
   'category': 'MONETARY_ACCOUNT_JOINT'},
  {'notification_delivery_method': 'PUSH',
   'category': 'MONETARY_ACCOUNT_PROFILE'},
  {'notification_delivery_method': 'PUSH', 'category': 'PAYMENT'},
  {'notification_delivery_method': 'PUSH', 'category': 'PROMOTION'},
  {'notification_delivery_method': 'PUSH', 'category': 'REQUEST'},
  {'notification_delivery_method': 'PUSH', 'category': 'SCHEDULE_RESULT'},
  {'notification_delivery_method': 'PUSH', 'category': 'SCHEDULE_STATUS'},
  {'notification_delivery_method': 'PUSH', 'category': 'SHARE'},
  {'notification_delivery_method': 'PUSH', 'category': 'SUPPORT'},
  {'notification_delivery_method': 'PUSH', 'category': 'TAB_RESULT'},
  {'notification_delivery_method': 'PUSH',
   'category': 'TAX_IDENTIFICATION_NUMBER_WARNING'},
  {'notification_delivery_method': 'PUSH', 'category': 'USER_APPROVAL'},
  {'notification_delivery_method': 'PUSH', 'category': 'WHITELIST'},
  {'notification_delivery_method': 'PUSH', 'category': 'WHITELIST_RESULT'},
  {'notification_delivery_method': 'PUSH', 'category': 'SLICE_BADGE'},
  {'notification_delivery_method': 'PUSH', 'category': 'SLICE_CHAT'},
  {'notification_delivery_method': 'PUSH', 'category': 'SLICE_REGISTRY_ENTRY'},
  {'notification_delivery_method': 'PUSH',
   'category': 'SLICE_REGISTRY_MEMBERSHIP'},
  {'notification_delivery_method': 'PUSH',
   'category': 'SLICE_REGISTRY_SETTLEMENT'},
  {'notification_delivery_method': 'PUSH', 'category': 'ACHIEVEMENT'},
  {'notification_delivery_method': 'PUSH', 'category': 'DIRECTOR'},
  {'notification_delivery_method': 'PUSH', 'category': 'POPUP_NOTIFICATION'},
  {'notification_delivery_method': 'PUSH', 'category': 'SUBSCRIPTION_TRIAL'},
  {'notification_delivery_method': 'PUSH', 'category': 'CARD'},
  {'notification_delivery_method': 'PUSH', 'category': 'FLARUM'},
  {'notification_delivery_method': 'PUSH', 'category': 'REMINDER_REQUEST'},
  {'notification_delivery_method': 'PUSH', 'category': 'PREMIUM_LIMITED'},
  {'notification_delivery_method': 'PUSH',
   'category': 'CARD_TRANSACTION_UPDATED'},
  {'notification_delivery_method': 'PUSH', 'category': 'REFERRAL'},
  {'notification_delivery_method': 'PUSH', 'category': 'REWARD'},
  {'notification_delivery_method': 'PUSH', 'category': 'SELECT_USER'},
  {'notification_delivery_method': 'PUSH', 'category': 'INTEREST'},
  {'notification_delivery_method': 'PUSH',
   'category': 'REMINDER_USER_IDENTIFICATION_VERIFICATION'},
  {'notification_delivery_method': 'PUSH', 'category': 'JOINT_MEMBERSHIP'},
  {'notification_delivery_method': 'PUSH', 'category': 'RISK_INFORMATION'},
  {'notification_delivery_method': 'PUSH', 'category': 'CHECKOUT_MERCHANT'},
  {'notification_delivery_method': 'PUSH', 'category': 'BARZAHLEN'},
  {'notification_delivery_method': 'PUSH', 'category': 'LOCATION_EVENT'},
  {'notification_delivery_method': 'PUSH', 'category': 'TREE'},
  {'notification_delivery_method': 'PUSH',
   'category': 'CARD_TRANSACTION_REFUND'},
  {'notification_delivery_method': 'PUSH', 'category': 'USER_REVIEW'},
  {'notification_delivery_method': 'PUSH',
   'category': 'CARD_DYNAMIC_CURRENCY_CONVERSION_WARNING'},
  {'notification_delivery_method': 'PUSH', 'category': 'BANCONTACT_MERCHANT'},
  {'notification_delivery_method': 'PUSH', 'category': 'TRIBE_GREEN'},
  {'notification_delivery_method': 'PUSH', 'category': 'TRIBE_RANK_GREEN'},
  {'notification_delivery_method': 'PUSH', 'category': 'GREEN_O_METER'},
  {'notification_delivery_method': 'PUSH',
   'category': 'CARD_TRANSACTION_TOKENIZED'},
  {'notification_delivery_method': 'PUSH',
   'category': 'MONETARY_ACCOUNT_BALANCE'},
  {'notification_delivery_method': 'PUSH', 'category': 'SUPPORT_ANNOUNCEMENT'},
  {'notification_delivery_method': 'PUSH', 'category': 'GIROPAY_MERCHANT'},
  {'notification_delivery_method': 'PUSH', 'category': 'OAUTH'},
  {'notification_delivery_method': 'PUSH',
   'category': 'RELATION_USER_REQUEST'},
  {'notification_delivery_method': 'PUSH', 'category': 'TRIBE_COMMON_GOAL'},
  {'notification_delivery_method': 'PUSH', 'category': 'FULFILLMENT'}],
 'address_main': {'street': 'Mason Turnpike',
  'house_number': '717',
  'postal_code': '1562 LU',
  'city': 'Den Haag',
  'country': 'NL',
  'province': None,
  'extra': None,
  'mailbox_name': None},
 'address_postal': {'street': 'Mason Turnpike',
  'house_number': '717',
  'postal_code': '1562 LU',
  'city': 'Den Haag',
  'country': 'NL',
  'province': None,
  'extra': None,
  'mailbox_name': 'Nancee Lawrence-Storm'},
 'first_name': 'Nancee',
 'middle_name': '',
 'last_name': 'Lawrence-Storm',
 'legal_name': 'Nancee Lawrence-Storm',
 'tax_resident': None,
 'date_of_birth': '1995-07-17',
 'place_of_birth': 'Den Haag',
 'country_of_birth': None,
 'nationality': 'NL',
 'gender': 'FEMALE',
 'version_terms_of_service': '1',
 'deny_reason': None,
 'document_status': 'ACTIVE',
 'is_primary_document': True,
 'customer': {'id': 27459,
  'created': '2020-06-13 09:04:55.593463',
  'updated': '2020-06-13 09:04:55.593463',
  'billing_account_id': 58598,
  'invoice_notification_preference': 'NONE'},
 'customer_limit': {'limit_monetary_account': 25,
  'limit_monetary_account_remaining': 25,
  'limit_card_debit_maestro': 1,
  'limit_card_debit_mastercard': 2,
  'limit_card_wildcard': 3,
  'limit_card_debit_wildcard': 3,
  'limit_card_debit_maestro_virtual_subscription': 5,
  'limit_card_debit_maestro_virtual_total': 20,
  'limit_card_debit_mastercard_virtual_subscription': 5,
  'limit_card_debit_mastercard_virtual_total': 20,
  'limit_card_replacement': 1,
  'limit_amount_monthly': None,
  'spent_amount_monthly': None,
  'limit_card_credit_mastercard': 1},
 'billing_contract': [{'BillingContractSubscription': {'id': 497373,
    'created': '2020-06-13 09:04:54.867028',
    'updated': '2020-06-13 09:04:54.867028',
    'contract_date_start': '2020-06-13',
    'contract_date_end': None,
    'contract_version': 1,
    'subscription_type': 'PERSON_PREMIUM_V1',
    'subscription_type_downgrade': 'PERSON_TRAVEL_V1',
    'status': 'ACTIVE',
    'sub_status': 'NONE'}}],
 'pack_membership': None,
 'premium_trial': None,
 'joint_membership': None}

```


## To maintain state accross usages. Use Client.save() method
```
client.save()
```

## And to restore
```
from aiobunq import Client
client = Client.restore()
```

## Currently supports createing payment requests for iDeal, Sofort, Bancontact & Creditcard

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
        "uuid": "SOME-UUID-STRING",
        "status": "PAYMENT_CREATED",
        "issuer_authentication_url": "https://r.girogate.de/pi/bunqideal?tx=loooooongstring-and-random-numbers",
        "bunqme_type": "TAB",
        "bunqme_uuid": "SOME-OTHER-UUID-STRING"
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
        "currency": "EUR",
        "description": "Mydescription",
        "amount_paid": 3.0,
        "amount_inquired": 3.0,
        "bunqme_tab_id": 1445}
      ,
      {
        "currency": "EUR",
        "description": "1234",
        "amount_paid": 0.0,
        "amount_inquired": 10.0,
        "bunqme_tab_id": 1433
      }
]
```


