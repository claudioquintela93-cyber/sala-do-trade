import os
import telebot
import requests
import google.generativeai as genai
from PIL import Image
import io

# Insere os teus dados diretamente aqui para evitar erros no Render
TELEGRAM_TOKEN = "9191290675:AAGgYmfFxaeXw3PQfcfOEiYi5obMhF0TNwo"
GEMINI_API_KEY = "AQ.Ab8RN6I2_L9IUIvKm597mC8Vj4PL5Oq1n4VcYJzPQSsn93UPkA"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5)
        if r.status_code == 200:
            return float(r.json().get("price", 3876.40))
    except:
        pass
    return 3876.40

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 
        "🏆 *Escritório do Ouro · Bot SMC com Visão IA Ativo*\n\n"
        "Envia o teu screenshot do MetaTrader/TradingView. Vou analisar os gráficos com IA visual, cruzar com o preço real e devolver o setup cirúrgico!"
    )

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "🔍 A aceder ao motor de Visão SMC e cotação Spot...")
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = Image.open(io.BytesIO(downloaded_file))
        
        current_price = get_gold_price()
        caption = message.caption if message.caption else "Análise H4 / Intraday XAU/USD"

        prompt = (
            f"És um analista institucional sénior de SMC (Smart Money Concepts) e ICT especializado em XAU/USD. "
            f"O preço spot atual de mercado é ${current_price:.2f}. "
            f"Analisa este gráfico enviado pelo trader (notas: {caption}). "
            f"Fornece um relatório técnico detalhado e direto com:\n"
            f"1. **Estrutura & POI:** Identifica a tendência macro/intraday, zonas de Order Block ou FVG visíveis.\n"
            f"2. **Setup Sugerido (Entrada, SL, TP):** Calcula os valores exatos com base no preço atual e na estrutura do gráfico.\n"
            f"3. **Gestão de Risco & R:R:** Indica o rácio risco-retorno.\n"
            f"Formata a resposta de forma limpa e profissional para Telegram em Markdown."
        )

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, image])
        
        bot.reply_to(message, response.text, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erro na análise visual: {str(e)}")

print("Bot Avançado a correr...")
bot.infinity_polling()
