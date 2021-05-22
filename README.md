# Raphael - A discord Bot

![Docker](https://github.com/SuperstalkerX/Raphael-Bot/workflows/Docker/badge.svg?branch=main)

This bot was not intended to become open-sourced. This bot was merely a tool for me to learn from, so there will be errors or dumb implementations. If you come here to help, it will be appreciated, but if you are here to make fun of my silly mistakes, then leave.

---

## Getting started

* Scroll to the FAQ portion of this document if you have questions.
* The easiest way to operate the bot, is to use [docker-compose](https://docs.docker.com/compose/reference/up/).

### Docker Compose

> Perquisite: Have Docker-Compose already installed on the host machine.

**STEP 1** 
Download [`docker-compose.yml`](https://github.com/SuperstalkerX/Raphael-Bot/blob/main/docker-compose.yml)

**STEP 2**
Make a `.env` file with the text below as the template. Then insert the corresponding data.

``` ENV
DATABASE_PASSWORD=
BOT_PREFIX=
BOT_TOKEN=
BOT_ID=
SENTRY_DSN=
SUBBY_API_ADDRESS=
SUBBY_API_KEY=
EMBY_API_ADDRESS=
EMBY_API_KEY=
FINNHUB_TOKEN=
```

**STEP 3**
Type `docker-compose -f "docker-compose.yml" up -d --build `

---
### Dockerfile

**Perquisites**
* Have Docker already installed on the host machine.
* Have PostgreSQL database already running.

**Run This Command:**
```Shell
docker run -d \
    --net="bridge" \
    --name=raphael-bot \
    -e BOT_PREFIX=<symbol(s) that you want to begin bot commands with> \
    -e BOT_TOKEN=<Discord bot token> \
    -e LOG_LEVEL=INFO \
    -e SENTRY_DSN=SENTRY_URI_HERE \
    -e SUBBY_API_ADDRESS=SUBBY_URL_HERE \
    -e SUBBY_API_KEY=SUBBY_KEY_HERE \
    -e EMBY_API_KEY=EMBY_KEY_HERE \
    -e EMBY_API_ADDRESS=EMBY_URL_HERE \
    -e FINNHUB_TOKEN=FINNHUB_TOKEN_HERE \
    docker.pkg.github.com/superstalkerX/raphael-bot/raphael-bot:latest
```

* Please replace all user variables in the above command defined by <> with the correct values.

### Example

```Shell
docker run -d \
    --net="bridge" \
    --name=raphael-bot \
    -v /apps/docker/raphael-bot:/app/config.yml \
    -e BOT_PREFIX=$ \
    -e BOT_TOKEN=ODA4ODUxOTg1NzMzMjU1MTk5.YCMkHQ.LuFw9zNYYYrAh2nAZwXZcWSy60A \
    -e LOG_LEVEL=INFO \
    -e SENTRY_DSN=SENTRY_URI_HERE \
    -e SUBBY_API_ADDRESS=SUBBY_URL_HERE \
    -e SUBBY_API_KEY=SUBBY_KEY_HERE \
    -e EMBY_API_KEY=EMBY_KEY_HERE \
    -e EMBY_API_ADDRESS=EMBY_URL_HERE \
    -e FINNHUB_TOKEN=FINNHUB_TOKEN_HERE \
    docker.pkg.github.com/superstalkerX/raphael-bot/raphael-bot:latest
```

---

## Building from source code

### Docker Compose

Docker-Compose source code setup is the exact same as the normal setup but download 
[`docker-compose.debug.yml`](https://github.com/SuperstalkerX/Raphael-Bot/blob/main/docker-compose.yml)
instead.

---

### Dockerfile

**Step 1:**
Download source files to your computer and open up a command-line-interface at that location.

**Step 2:**
Build the [Docker image](https://docs.docker.com/engine/reference/commandline/build/) with the following command:

```Shell
docker build . -t raphael-bot
```

**Step 3:**
Run the container with this command.

```Shell
docker run -d \
    --net="bridge" \
    --name=raphael-bot \
    -v /apps/docker/raphael-bot:/app/DATABASE.db \
    -v /apps/docker/raphael-bot:/app/config.yml \
    -e BOT_PREFIX=PASTE_BOT_PREFIX_HERE \
    -e BOT_TOKEN=PASTE_BOT_TOKEN_HERE \
    -e LOG_LEVEL=INFO \
    -e SENTRY_DSN=SENTRY_URI_HERE \
    -e SUBBY_API_ADDRESS=SUBBY_URL_HERE \
    -e SUBBY_API_KEY=SUBBY_KEY_HERE \
    -e EMBY_API_KEY=EMBY_KEY_HERE \
    -e EMBY_API_ADDRESS=EMBY_URL_HERE \
    -e FINNHUB_TOKEN=FINNHUB_TOKEN_HERE \
    raphael-bot
```

# FAQ

## Where can I make a Discord bot token?

* You can find a helpful guide on where and how to make one [HERE](https://www.writebots.com/discord-bot-token/)
* Be sure you set the correct Intents permissions, or your bot might not work correctly.

## Why is the docker command so long?

* The environmental variables do not have to be in the command but it is simple for them to be located there. If you do not wish for them to be located there because of security or other reasons, you can use the `config.yml` file for that usage instead. You simply follow the syntax of the [`config-default.yml`](https://github.com/SuperstalkerX/Raphael-Bot/blob/main/config-default.yml) and **ONLY** type what you want to change or else you may break future changes.
* Here is an example of what the two files look like compared to each other. Be sure you remove the `!ENV` Infix.
![IMAGE](https://i.imgur.com/z03QMGw.png)
