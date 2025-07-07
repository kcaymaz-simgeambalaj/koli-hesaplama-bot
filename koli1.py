import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# Aşamaları tanımla
X, Y, Z, FIYAT, KAR = range(5)

# Sabit fiyat listesi (Görseldeki verilere göre güncellendi)
fiyatlar = [
    {"cinsi": "T/S/S/S/S", "kalite": "B+C DOPEL", "fiyat": 14.60},
    {"cinsi": "T/S/S/S/T", "kalite": "B+C DOPEL", "fiyat": 14.70},
    {"cinsi": "B/S/S/ST", "kalite": "B+C DOPEL", "fiyat": 16.62},
    {"cinsi": "B/S/S/S/T 2S*125 GR", "kalite": "B+C DOPEL", "fiyat": 19.76},
    {"cinsi": "B/S/S/S/K", "kalite": "B+C DOPEL", "fiyat": 21.56},
    {"cinsi": "B/S/S/MK", "kalite": "B+C DOPEL", "fiyat": 17.97},
    {"cinsi": "K/S/S/S/T", "kalite": "B+C DOPEL", "fiyat": 17.10},
    {"cinsi": "K/S/S/S/K", "kalite": "B+C DOPEL", "fiyat": 19.76},
    {"cinsi": "KS/S/S/MK", "kalite": "B+C DOPEL", "fiyat": 17.97},
    {"cinsi": "MK/S/S/S/T", "kalite": "B+C DOPEL", "fiyat": 15.28},
    {"cinsi": "MK/S/S/S/MK", "kalite": "B+C DOPEL", "fiyat": 16.17},
    {"cinsi": "B/S/S/SMK 2S*125 GR", "kalite": "B+C DOPEL", "fiyat": 21.56},
    {"cinsi": "K/S/S/S/MK 2S*125 GR", "kalite": "B+C DOPEL", "fiyat": 21.56},
    {"cinsi": "K/S/S/S/MK 2S*135 GR", "kalite": "B+C DOPEL", "fiyat": 22.46},
    {"cinsi": "K/S/S/K 140 GR", "kalite": "B+C DOPEL", "fiyat": 25.16},
    {"cinsi": "MK/S/S/S/T 2S*125 GR", "kalite": "B+C DOPEL", "fiyat": 18.42},
    {"cinsi": "MK/S/S/S/T 2S*135 GR", "kalite": "B+C DOPEL", "fiyat": 19.31},
    {"cinsi": "MK/S/S/S/MK 2S*125 GR", "kalite": "B+C DOPEL", "fiyat": 19.31},
    {"cinsi": "MK/S/S/S/MK 2S*135 GR", "kalite": "B+C DOPEL", "fiyat": 20.22},
    {"cinsi": "MK/S/S/S/MK 140 GR", "kalite": "B+C DOPEL", "fiyat": 22.46}
]


# Başlat
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("📦 Hoş geldiniz! Lütfen EN değerini (cm) girin:")
    return X

async def al_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["x"] = float(update.message.text)
        await update.message.reply_text("Şimdi BOY değerini (cm) girin:")
        return Y
    except (ValueError, TypeError):
        await update.message.reply_text("Lütfen geçerli bir sayı girin.")
        return X

async def al_y(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["y"] = float(update.message.text)
        await update.message.reply_text("Şimdi YÜKSEKLİK değerini (cm) girin:")
        return Z
    except (ValueError, TypeError):
        await update.message.reply_text("Lütfen geçerli bir sayı girin.")
        return Y

async def al_z(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["z"] = float(update.message.text)
        x = context.user_data["x"]
        y = context.user_data["y"]
        z = context.user_data["z"]

        # Koli alanı hesaplama formülü: ((en + boy) * 2 + pay) * (boy + yükseklik)
        # Genellikle 4 cm'lik bir yapıştırma payı eklenir.
        ilk_islem = (x + y) * 2 + 4 # cm cinsinden
        boyut = ((y + z) * ilk_islem) / 10000 # m²'ye çevrilir
        context.user_data["boyut"] = boyut

        mesaj = f"Hesaplanan Koli Alanı: {boyut:.4f} m²\n\nFiyat seçenekleri:\n"
        for i, f in enumerate(fiyatlar, 1):
            mesaj += f"{i}. {f['cinsi']} | {f['kalite']} | {f['fiyat']} TL/m²\n"

        await update.message.reply_text(mesaj + f"\nLütfen 1-{len(fiyatlar)} arasında bir fiyat seçin:")
        return FIYAT
    except (ValueError, TypeError):
        await update.message.reply_text("Lütfen geçerli bir sayı girin.")
        return Z

async def al_fiyat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        secim = int(update.message.text) - 1
        if not (0 <= secim < len(fiyatlar)):
            raise ValueError

        secilen_fiyat = fiyatlar[secim]["fiyat"]
        context.user_data["secilen_fiyat"] = secilen_fiyat
        boyut_m2 = context.user_data["boyut"]
        maliyet = boyut_m2 * secilen_fiyat  # TL

        context.user_data["maliyet"] = maliyet

        await update.message.reply_text(f"Birim Koli Maliyeti: {maliyet:.2f} TL\nŞimdi kar yüzdesini girin (örneğin: 20):")
        return KAR
    except (ValueError, TypeError):
        await update.message.reply_text(f"Lütfen geçerli bir seçim yapın (1-{len(fiyatlar)}):")
        return FIYAT

async def al_kar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        kar = float(update.message.text)
        maliyet = context.user_data["maliyet"]
        karli = maliyet * (1 + kar / 100)
        await update.message.reply_text(
            f"📈 Kar Eklenmiş Satış Fiyatı: {karli:.2f} TL\n(%{kar} kar ile)"
        )
        return ConversationHandler.END
    except (ValueError, TypeError):
        await update.message.reply_text("Lütfen geçerli bir yüzde değeri girin:")
        return KAR

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("İşlem iptal edildi.")
    return ConversationHandler.END

# Ana bot fonksiyonu
def main():
    import os
    # TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" # ← Telegram Bot Token'ınızı buraya yazın
    TOKEN = "7815418417:AAEZ3I2lBBE1bhkAqTlX2d64yYo9hDTctCk" # Mevcut Token
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            X: [MessageHandler(filters.TEXT & ~filters.COMMAND, al_x)],
            Y: [MessageHandler(filters.TEXT & ~filters.COMMAND, al_y)],
            Z: [MessageHandler(filters.TEXT & ~filters.COMMAND, al_z)],
            FIYAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, al_fiyat)],
            KAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, al_kar)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
