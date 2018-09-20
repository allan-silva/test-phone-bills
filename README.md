# Phone Bills API [![Build Status](https://travis-ci.org/allan-silva/test-phone-bills.svg?branch=master)](https://travis-ci.org/allan-silva/test-phone-bills)  [![Coverage Status](https://coveralls.io/repos/github/allan-silva/test-phone-bills/badge.svg?branch=master)](https://coveralls.io/github/allan-silva/test-phone-bills?branch=master)

### Infrastructure components

 - **PostgreSQL:** - Main system database, stores the tariff configuration and call records.
 - **MongoDb:** - Stores the generated bills, once a bill was requested to closing, all generated data will be stored here.
 - **RabbitMQ:** - Delivers the Call and Bill events to client consumers.

### System componens

 - **Web Application:** - Provides endpoints for phone call events, bill close requests and closed bill  queries.
 - **Consumer application:** - Responsible for handle incoming call events and bill close requests.
 - **Common Library:** - Has the common shared classes, configuration features, pricing engine and database access used through the system.

### Architecture overview

![alt text](https://raw.githubusercontent.com/allan-silva/test-phone-bills/master/Billing%20System.png)

This kind of system requires a non blocking and high availability endpoints. To achieve this goal, the call events requests and close bill requests are queued to be processed by a worker process listening RabbitMQ queues, in this way the hard processing work does not block the web api clients.
The choice by PostgreSQL to be the calls repository, was due the consistency, mainly for tariff configurations and relations between calls and applied tariffs.
The MongoDB was introduced to be a repository for closed bills. The main motivation was his high flexibility, if a already closed bill needs be reprocessed, we can replace the entire document in one command, without necessity to take care of relations and delete/update statements. Also, using another database to store closed bills, reduces the work load of the main database. An important point here is that the closed bills are processed once, and not by request in get bill endpoint.

### Pricing Model

![alt text](https://raw.githubusercontent.com/allan-silva/test-phone-bills/master/PricingModel.png)

Although the pricing rules do not indicates anything about call prices, for calls from different source/destination area codes. It makes sense that source/dest area codes are parts of price rules conditions, so area codes are considered when a tariff is applied for a call. E.g.:
- Source area code: 11 - Dest area code: 41 - Between 6:00 and 22:00 - Standard Charge: 0.36 - Call time charge: 0.09
- Source area code: 21 - Dest area code: 41 - Between 6:00 and 22:00 - Standard Charge: 0.10 - Call time charge: 0.20

**Infrastructure Limitation: With this model, the cartesian product between area codes demands a lot of database rows, but HEROKU offers only 10K for the free PostgreSQL instance. Currently the system supports calls between the following area codes: '11', '41', '61', '68' and '99'**

### Rest API:

API documentation is available through the swagger-ui at: https://olist-billing-api-test.herokuapp.com/v1/ui/#/default

The requests should be issued in the following order:

**1 - POST - /v1/call:** Posts a call start/end events. The tariff will be applied when a pair of start/end event for the same call_id were identified by the system.
**2 - POST - /v1/bill/{subscriber}/close:** Closes the given reference period. Post to this endpoint will publish a message requesting the bill to be closed. All calculated charges and the calls summary will be replicated to the MongoDB.
**Test evaluation: I supposed that the evaluation requires the bills already closed. See SAMPLE_DATA for details.**
**3 - GET - /v1/bill/{subscriber}:** Gets the closed bill for the given reference period or the bill for the last closed period.

### Development tools and libs:

- Dell Inspiron - Intel i7, 16gb RAM, with no ssd :( -  OS: Ubuntu 16;
- Docker for local development,  to deal with PostgreSQL, MongoDb and RabbitMQ instances (see docker-compose.yml;
- Sublime Text;
- Virtualenv;
- Flask with Connexion;
- Kombu for the RabbitMQ stuff;
- SqlAlchemy;
- PyMongo;
- Py-time-between: I was looking for a very simple library, to tell me if a given time falls between two other given times. I don't found it, so I create my own: https://github.com/MicroarrayTecnologia/py-time-between.git , https://pypi.org/project/py-time-between/

### Known issues:
All known issues are available at: https://github.com/allan-silva/test-phone-bills/issues with open status.

