# Telegram shop bot
This bot allows you to create your own shop in Telegram with crypto payments support.

## Installation with Docker
Before running you need to have installed [Docker](https://docs.docker.com/get-started/get-docker/) first, then run the following command:<br/>
```
docker run -e BOT_TOKEN='your bot token' -e CRYPTOPAY_TOKEN='your cryptopay token' -e MAIN_ADMIN_ID='your telegram id' emptx0/tg_shop
```

## Manual installation
To run this bot you need to install [Python version 3.12](https://www.python.org/downloads/) or higher.</br>
### Installation:
```
pip install -r requirements.txt
```
### Run installer:
Before running the bot, you need to get [your Telegram ID](https://t.me/getmyid_bot), create a telegram bot [api-token](https://t.me/BotFather) and cryptopay [api-token](https://t.me/send)
(<i>or cryptopay testnet [api-token](https://t.me/CryptoTestnetBot)</i>):
```
python installer.py
```
### Run bot:
```
pyrhon main.py
```
## !
As default bot use cryptopay test network. To switch to main network you need to change `network=Networks.TEST_NET` to `network=Networks.MAIN_NET` in line 9 `cryptopay.py` file.