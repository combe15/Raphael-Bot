# Raphael - A discord Bot

![Docker](https://github.com/SuperstalkerX/Raphael-Bot/workflows/Docker/badge.svg?branch=main)

This bot was not intended to become open-sourced but was so under request. This bot was merely a tool for me to learn from, so there will be errors or dumb implementations. If you come here to help, it will be greatly appreciated, but if you are here to make fun of my silly mistakes, then leave.

This project currently uses Python 3.8

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
DATABASE_VIEW_PORT=
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
Start docker-compose stack
```SHELL
docker-compose -f "docker-compose.yml" up -d --build
```

---

## Building from source code

### Docker Compose

Docker-Compose source code setup is the exact same as the normal setup but use 
[`docker-compose.test.yml`](https://github.com/SuperstalkerX/Raphael-Bot/blob/main/docker-compose.test.yml)
instead.

Be sure you have downloaded the entire repo if using this method, else it may not work.

---

## Dev Environment

**STEP 1**
Git Pull this repo.

**STEP 2**
Make a `.env` file with the text below as the template. Then insert the corresponding data.

``` ENV
DATABASE_PASSWORD=
DATABASE_VIEW_PORT=
```
A full `.env` file, like `Docker Compose`'s setup in this README, is preferred but not required for Dev work.

**STEP 3**
Start docker-compose stack
```SHELL
docker-compose -f "docker-compose.debug.yml" up -d --build
```

**STEP 4**
Make a `config.yml` file with below as the template.

Be sure you replace with your own tokens and addresses.

```yaml
bot:
  prefix:     "$"
  token:      "ODA4ODUxOTg1NzMzMjU1MTk5.YCMkHQ.LuFw9zNYYYrAh2nAZwXZcWSy60A"
  id:         "757736089732513875"
  log_level:  "TRACE" # NOTSET | TRACE | DEBUG | INFO | WARN | ERROR | CRITICAL

db:
  host:       "localhost:5432"
  user:       "raphael"
  password:   "raphael-password"

subby_api:
  address:    "http://400.563.1.1:4545"
  api_key:    "umturvymonitoryS10w1ymynahcomp1ete"

emby:
  api_key:    "829c405b5d6c468a9c9c4f8f910d614a"

finnhub:
    token:    "bu53f6n22v6sjdfq7sbe"
    url:      "https://finnhub.io"

```

Be sure the `config.yml` is next to the 
[`config-default.yml`](https://github.com/SuperstalkerX/Raphael-Bot/blob/main/config-default.yml)
file in the directory.

**STEP 5**
Install bot requirements.

> Note: Project is written in python 3.8

> Optional: Make a virtual environment and install requirements there.
```SHELL
pip3 install -r requirements.txt
```
Now debug the bot like a normal python program in your favorite IDE or text editor.

# FAQ

## Where can I make a Discord bot token?

* You can find a helpful guide on where and how to make one [HERE](https://www.writebots.com/discord-bot-token/).
* Be sure you set the correct Intents permissions, or your bot might not work correctly.

