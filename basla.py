# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from AYAR import BinanceAPIKey, BinanceAPISecret, TELEGRAM_BOT_TOKEN, TELEGRAM_ID, SEMBOL, KALDIRAC, PARA_YUZDE, TAKE_PROFIT_1, TAKE_PROFIT_2, STOP_LOSS, ZAMAN_ARALIGI, SON_X_MUM, YAVAS_EMA, HIZLI_EMA

from KekikTaban import KekikTaban

taban = KekikTaban(
    baslik   = "Binance SL-TP Örneği",
    aciklama = "Binance SL-TP Örneği Başlatıldı..",
    banner   = "SL - TP",
    girinti  = 7
)

konsol = taban.konsol

from ccxt import binance, BaseError
import pandas as pd
from ta.trend import EMAIndicator

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException

TG_Bot = TeleBot(TELEGRAM_BOT_TOKEN, parse_mode="Markdown")

kesisim         = False
longPozisyonda  = False
shortPozisyonda = False
pozisyondami    = False
takeprofit1     = False
takeprofit2     = False

# Binance AĞI Bağlantısı
binance_api = binance({
    "apiKey"    : BinanceAPIKey,
    "secret"    : BinanceAPISecret,
    'options'   : {
        'defaultType' : 'future'
    },
    'enableRateLimit' : True
})


def long_giris(alinacak_miktar):
    konsol.log(f"Long İşleme Giriliyor | {alinacak_miktar}")
    taban.bildirim("Long İşleme Giriliyor", alinacak_miktar)
    try:
        TG_Bot.send_message(TELEGRAM_ID, f"Long İşleme Giriliyor | {alinacak_miktar}")
    except ApiTelegramException as hata:
        taban.hata_salla(hata)
    # return binance_api.create_market_buy_order(f"{SEMBOL}/USDT", alinacak_miktar)

def long_cikis(satilacak_miktar):
    konsol.log(f"Long İşlemden Çıkılıyor | {satilacak_miktar}")
    taban.bildirim("Long İşlemden Çıkılıyor", satilacak_miktar)
    try:
        TG_Bot.send_message(TELEGRAM_ID, f"Long İşlemden Çıkılıyor | {satilacak_miktar}")
    except ApiTelegramException as hata:
        taban.hata_salla(hata)
    # return binance_api.create_market_sell_order(f"{SEMBOL}/USDT", satilacak_miktar, {"reduceOnly": True})

def short_giris(alinacak_miktar):
    konsol.log(f"Short İşleme Giriliyor | {alinacak_miktar}")
    taban.bildirim("Short İşleme Giriliyor", alinacak_miktar)
    try:
        TG_Bot.send_message(TELEGRAM_ID, f"Short İşleme Giriliyor | {alinacak_miktar}")
    except ApiTelegramException as hata:
        taban.hata_salla(hata)
    # return binance_api.create_market_sell_order(f"{SEMBOL}/USDT", alinacak_miktar)

def short_cikis(satilacak_miktar):
    konsol.log(f"Short İşlemden Çıkılıyor | {satilacak_miktar}")
    taban.bildirim("Short İşlemden Çıkılıyor", satilacak_miktar)
    try:
        TG_Bot.send_message(TELEGRAM_ID, f"Short İşlemden Çıkılıyor | {satilacak_miktar}")
    except ApiTelegramException as hata:
        taban.hata_salla(hata)
    # return binance_api.create_market_buy_order(f"{SEMBOL}/USDT", (satilacak_miktar * -1), {"reduceOnly": True})

while True:
    try:

        serbest_bakiye   = binance_api.fetch_free_balance()

        bakiye           = binance_api.fetch_balance()
        pozisyonlar      = bakiye['info']['positions']
        gecerli_pozisyon = [pozisyon for pozisyon in pozisyonlar if float(pozisyon['positionAmt']) != 0 and pozisyon['symbol'] == f"{SEMBOL}USDT"]
        pozisyon_bilgi   = pd.DataFrame(gecerli_pozisyon, columns=["symbol", "entryPrice", "unrealizedProfit", "isolatedWallet", "positionAmt", "positionSide"])

        try:
            son_posizyon_miktari = float(pozisyon_bilgi["positionAmt"][len(pozisyon_bilgi.index) - 1])
        except IndexError:
            son_posizyon_miktari = 0

        # Pozisyonda olup olmadığını kontrol etme
        if not pozisyon_bilgi.empty and son_posizyon_miktari != 0:
            pozisyondami = True
        else: 
            pozisyondami = False

            shortPozisyonda = False
            longPozisyonda  = False

        # Long pozisyonda mı?
        if pozisyondami and son_posizyon_miktari > 0:
            longPozisyonda  = True
            shortPozisyonda = False
        # Short pozisyonda mı?
        if pozisyondami and son_posizyon_miktari < 0:
            shortPozisyonda = True
            longPozisyonda  = False

        # Mumlar
        binance_mumlar = binance_api.fetch_ohlcv(f"{SEMBOL}/USDT", timeframe=ZAMAN_ARALIGI, limit=SON_X_MUM)
        mum_dataframe  = pd.DataFrame(binance_mumlar, columns=["timestamp", "open", "high", "low", "close", "volume"])

        # Yavaş Ema Verisi
        _yavas_ema = EMAIndicator(mum_dataframe["close"], float(YAVAS_EMA))
        mum_dataframe["YAVAS_EMA"] = _yavas_ema.ema_indicator()

        # Hızlı Ema Verisi
        _hizli_ema = EMAIndicator(mum_dataframe["close"], float(HIZLI_EMA))
        mum_dataframe["HIZLI_EMA"] = _hizli_ema.ema_indicator()

        if (mum_dataframe["HIZLI_EMA"][SON_X_MUM - 3] < mum_dataframe["YAVAS_EMA"][SON_X_MUM - 3] and mum_dataframe["HIZLI_EMA"][SON_X_MUM - 2] > mum_dataframe["YAVAS_EMA"][SON_X_MUM - 2]) or (mum_dataframe["HIZLI_EMA"][SON_X_MUM - 3] > mum_dataframe["YAVAS_EMA"][SON_X_MUM - 3] and mum_dataframe["HIZLI_EMA"][SON_X_MUM - 2] < mum_dataframe["YAVAS_EMA"][SON_X_MUM - 2]):
            kesisim = True
        else: 
            kesisim = False

        alinacak_miktar = (((float(serbest_bakiye["USDT"]) / 100 ) * float(PARA_YUZDE)) * float(KALDIRAC)) / float(mum_dataframe["close"][SON_X_MUM - 1])

        # Boğa Durumu
        if kesisim and mum_dataframe["HIZLI_EMA"][SON_X_MUM - 1] > mum_dataframe["YAVAS_EMA"][SON_X_MUM - 1] and not longPozisyonda:
            if shortPozisyonda:
                short_cikis(son_posizyon_miktari)

            long_giris(alinacak_miktar)
            takeprofit1 = False
            takeprofit1 = False

        # Ayı Durumu
        if kesisim and mum_dataframe["HIZLI_EMA"][SON_X_MUM - 1] < mum_dataframe["YAVAS_EMA"][SON_X_MUM - 1] and not shortPozisyonda:
            if longPozisyonda:
                long_cikis(son_posizyon_miktari)

            short_giris(alinacak_miktar)
            takeprofit1 = False
            takeprofit1 = False

        # Long için Stop Loss
        if longPozisyonda and ((float(mum_dataframe["close"][SON_X_MUM - 1]) - float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) / float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) * 100 * -1 >= float(STOP_LOSS):
            konsol.log("[bold red]STOP LOSS")
            long_cikis(son_posizyon_miktari)
            takeprofit1 = False
            takeprofit1 = False

        # Short için Stop Loss
        if shortPozisyonda and ((float(mum_dataframe["close"][SON_X_MUM - 1]) - float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) / float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) * 100 >= float(STOP_LOSS):
            konsol.log("[bold red]STOP LOSS")
            short_cikis(son_posizyon_miktari)
            takeprofit1 = False
            takeprofit1 = False

        # Long için Take Profit
        # Take Profit 1
        if longPozisyonda and not takeprofit1 and ((float(mum_dataframe["close"][SON_X_MUM - 1]) - float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) / float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) * 100 >= float(TAKE_PROFIT_1):
            konsol.log("[green]TAKE PROFIT 1")
            long_cikis(son_posizyon_miktari / 2)
            takeprofit1 = True

        # Take Profit 2
        if longPozisyonda and not takeprofit2 and ((float(mum_dataframe["close"][SON_X_MUM - 1]) - float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) / float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) * 100 >= float(TAKE_PROFIT_2):
            konsol.log("[yellow]TAKE PROFIT 2")
            long_cikis(son_posizyon_miktari)
            takeprofit2 = True

        # Short için Take Profit
        # Take Profit 1
        if shortPozisyonda and not takeprofit1 and ((float(mum_dataframe["close"][SON_X_MUM - 1]) - float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) / float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) * 100 * -1 >= float(TAKE_PROFIT_1):
            konsol.log("[green]TAKE PROFIT 1")
            short_cikis(son_posizyon_miktari / 2)
            takeprofit1 = True

        # Take Profit 2
        if shortPozisyonda and not takeprofit2 and ((float(mum_dataframe["close"][SON_X_MUM - 1]) - float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) / float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])) * 100 * -1 >= float(TAKE_PROFIT_2):
            konsol.log("[yellow]TAKE PROFIT 2")
            short_cikis(son_posizyon_miktari)
            takeprofit2 = True

        if not pozisyondami:
            # taban.temizle
            konsol.log("Pozisyon Aranıyor...")

        if shortPozisyonda:
            mesaj = f"""
    Short Pozisyonda Bekliyor

Anlık Fiyat          : {float(mum_dataframe["close"][SON_X_MUM - 1])}

Kâr Al 1 Fiyatı      : {float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])-(float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])/100) * float(TAKE_PROFIT_1)}
Kâr Al 2 Fiyatı      : {float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])-(float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])/100) * float(TAKE_PROFIT_2)}

Zarar Durdur Fiyatı  : {((float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1]) / 100 ) * float(STOP_LOSS)) + float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])}
"""
            konsol.log(mesaj)

        if longPozisyonda:
            mesaj = f"""
    Long Pozisyonda Bekliyor

Anlık Fiyat          : {float(mum_dataframe["close"][SON_X_MUM - 1])}

Kâr Al 1 Fiyatı      : {((float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1]) / 100 ) * float(TAKE_PROFIT_1)) + float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])}
Kâr Al 2 Fiyatı      : {((float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1]) / 100 ) * float(TAKE_PROFIT_2)) + float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])}

Zarar Durdur Fiyatı  : {float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])-(float(pozisyon_bilgi["entryPrice"][len(pozisyon_bilgi.index) - 1])/100) * float(STOP_LOSS)}
"""
            konsol.log(mesaj)

    except BaseError as hata:
        konsol.print(f"{type(hata).__name__} | {hata}")
        continue