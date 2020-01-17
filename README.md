# Nike-Monitor

## Table of Contents
- [Description](#Description)
- [How it Works](#How-it-Works)
- [Helpful Links](#Helpful-Links)

<br/>

## Description
Sneaker resale has become very saturated, so many resellers are starting to use bots. Whereas a bot finds and purchases the desired sneakers for you, a *monitor* simply notifies a Discord/Slack channel whenever the sneaker is released.

Arguably, this is more ethical \**tries to defend this creation*\*, since the purchasing is still done by a human. This won't compete with a working bot, but it's better than nothing.

<br/>

## How it Works
A typical monitor makes a request to an API endpoint on an online store, retrieves a list of products, and posts them as notifications to Discord/Slack.

The core principle is the same, but this monitor is more advanced.

Under the hood, it is actually *multiple* monitors, each one sending requests through a different proxy. This was done to maximize speed, since network latency and eventual consistency of the API endpoint makes a single monitor fairly inconsistent.

However, duplicating the entire monitor is inefficient, so it is partitioned into independent modules that are separated by pipelines. Each module receives some data, performs a specific task, and sends it to a pipeline without worrying about what happens next. This way, you can scale each portion of the microsystem based on demand, following [scalability principles][6].

Every module in the system exists in it's own [Docker][3] container, allowing simple scalability with [docker compose][4]. Scalability with [Kubernetes][5] was considered, but it was not required for such a small system. 

The following diagram shows the main modules in the system: the [monitor][11], [validator][12], and the [notifier][13].

<br/>

![][21]

<br/>

Each module performs a different task.
- The [monitor][11] sends a request to the Nike API, retrieves a list of products, and sends each product to the first pipeline.
- The [validator][12] reads from the first pipeline and ensures that the product has required information. Next, it checks the product against a local database to remove duplicate notifications. If a notification has not yet been made, it sends the product to the second pipeline.
- The [notifier][13] reads from the second pipeline and sends a formatted notification to Discord.

Since each pipeline may have different loads, the system can be scaled to something like this:

<br/>

![][22]

<br/>

There are a few modules that never scale, namely the [backend][15] and the [management api][14].
- The [backend][15] is responsible for launching the [PostgreSQL][2] database and the [RabbitMQ][1] message broker, or pipeline. Both the database and the pipeline are mounted to local folders on the host machine, meaning no data is lost (even if containers go down).
- The [management api][14] allows dynamic addition of Webhooks to the database, which identify Discord channels to send the notifications to.

Here is the final, all-inclusive diagram of the system:

<br/>

![][23]

<br/>

## Helpful Links
[RabbitMQ][1]

[PostgreSQL][2]

[Docker][3]

[Docker-compose][4]

[Kubernetes][5]

[Scalability Principles][6]

[1]: https://www.rabbitmq.com/
[2]: https://www.postgresql.org/
[3]: https://www.docker.com/
[4]: https://docs.docker.com/compose/
[5]: https://kubernetes.io/
[6]: https://elastisys.com/2015/09/10/scalability-design-principles/
[11]: ./src/monitor
[12]: ./src/validator
[13]: ./src/notifier
[14]: ./src/management_api
[15]: ./src/backend
[21]: ./images/img1.jpg
[22]: ./images/img2.jpg
[23]: ./images/img3.jpg
