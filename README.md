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

[IMG]

This kind of system requires a non blocking and high availability endpoints. To achieve this goal, the call events requests and close bill requests are queued to be processed by a worker process listening RabbitMQ queues, in this way the hard processing work does not block the web api clients.
The choice by PostgreSQL to be the calls repository, was due the consistency, mainly for tariff configurations and relations between calls and applied tariffs.
The MongoDB was introduced to be a repository for closed bills. The main motivation was his high flexibility, if a already closed bill needs be reprocessed, we can replace the entire document in one command, without necessity to take care of relations and delete/update statements. Also, using another database to store closed bills, reduces the work load of the main database. An important point here is that the closed bills are processed once, and not by request in get bill endpoint.
