from aiocryptopay import AioCryptoPay, Networks, utils

import configuration as c

config = c.Configuration()
crypto = AioCryptoPay(token=config.get_cryptopay_token(), network=Networks.TEST_NET)


class CryptoPay:
    async def get_price(price: float, currency: str):
        rates = await crypto.get_exchange_rates()
        if currency == 'USDT':
            pass
        if currency == 'TON':
            exchange = float((utils.exchange.get_rate('TON', 'USD', rates)).rate)
            price /= exchange
        return price

    async def create_invoice(price: float, currency: str):
        price = await CryptoPay.get_price(price, currency)
        invoice = await crypto.create_invoice(asset=currency, amount=price)
        return invoice.bot_invoice_url, invoice.invoice_id

    async def get_status(invoice_id: int):
        invoices = await crypto.get_invoices(invoice_ids=invoice_id)
        return invoices.status
