import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# Aşamaları tanımla
X, Y, Z, FIYAT, KAR = range(5)

# Sabit fiyat listesi
fiyatlar = [
    {"cinsi": "T/S/S/S/S", "kalite": "C – İRİ", "fiyat": 14.60},
    {"cinsi": "MK/S/S/STT", "kalite": "B+C DOPEL", "fiyat": 15.28},
    {"cinsi": "MK/S/S/S/MK", "kalite": "B+C DOPEL", "fiyat": 16.17},
    {"cinsi": "MK/S/S/STT 2S*125 GR", "kalite": "B+C DOPEL", "fiyat": 18.42},
    {"cinsi": "MK/S/S/S/MK 2S*135 GR", "kalite": "B+C DOPEL", "fiyat": 19.31}
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
    except:
        await update.message.reply_text("Lütfen geçerli bir sayı girin.")
        return X

async def al_y(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["y"] = float(update.message.text)
        await update.message.reply_text("Şimdi YÜKSEKLİK değerini (cm) girin:")
        return Z
    except:
        await update.message.reply_text("Lütfen geçerli bir sayı girin.")
        return Y

async def al_z(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["z"] = float(update.message.text)
        x = context.user_data["x"]
        y = context.user_data["y"]
        z = context.user_data["z"]

        ilk_islem = (x + y) * 2 + 0.04
        boyut = (y + z) * ilk_islem  # cm²
        context.user_data["boyut"] = boyut

        mesaj = f"Hesaplanan boyut: {boyut:.2f} cm²\n\nFiyat seçenekleri:\n"
        for i, f in enumerate(fiyatlar, 1):
            mesaj += f"{i}. {f['cinsi']} | {f['kalite']} | {f['fiyat']} TL/m²\n"

        await update.message.reply_text(mesaj + "\nLütfen 1-5 arasında bir fiyat seçin:")
        return FIYAT
    except:
        await update.message.reply_text("Lütfen geçerli bir sayı girin.")
        return Z

async def al_fiyat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        secim = int(update.message.text) - 1
        if not (0 <= secim < len(fiyatlar)):
            raise ValueError

        secilen_fiyat = fiyatlar[secim]["fiyat"]
        context.user_data["secilen_fiyat"] = secilen_fiyat
        boyut = context.user_data["boyut"]
        maliyet = boyut * secilen_fiyat / 10000  # TL (cm² → m²)

        context.user_data["maliyet"] = maliyet

        await update.message.reply_text(f"Toplam maliyet: {maliyet:.2f} TL\nŞimdi kar yüzdesini girin (örneğin: 20):")
        return KAR
    except:
        await update.message.reply_text("Lütfen geçerli bir seçim yapın (1-5):")
        return FIYAT

async def al_kar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        kar = float(update.message.text)
        maliyet = context.user_data["maliyet"]
        karli = maliyet * (1 + kar / 100)
        await update.message.reply_text(
            f"📈 Kar eklendikten sonraki satış fiyatı: {karli:.2f} TL\n(%{kar} kar ile)"
        )
        return ConversationHandler.END
    except:
        await update.message.reply_text("Lütfen geçerli bir yüzde değeri girin:")
        return KAR

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("İşlem iptal edildi.")
    return ConversationHandler.END

# Ana bot fonksiyonu
def main():
    import os
    TOKEN = "7815418417:AAEZ3I2lBBE1bhkAqTlX2d64yYo9hDTctCk"  # ← Telegram Bot Token'ınızı buraya yazın
    logging.basicConfig(level=logging.INFO)

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
