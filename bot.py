import os
import io
import base64
import requests
import telebot
from PIL import Image
from flask import Flask, request

# Credenciais oficiais integradas
TELEGRAM_TOKEN = "9140335855:AAGSfHodtC7AXbOa38Kzbop6wH8fqeWCp5g"
GEMINI_API_KEY = "AQ.Ab8RN6KCPYZ_nltW9vaKJsVKN_YUcx2bJ0wyZ9VbyX-5-s-vkQ"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5)
        if r.status_code == 200:
            return float(r.json().get("price", 3876.40))
    except Exception:
        pass
    return 3876.40

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "🏆 *Escritório do Ouro · Bot SMC com Visão IA Ativo*\n\n"
        "Envia o teu screenshot do MetaTrader/TradingView. Vou analisar os gráficos com IA visual, cruzar com o preço real e devolver o setup cirúrgico!"
    )

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "🔍 A aceder ao motor de Visão SMC e cotação Spot...")
        
        # Obter e descarregar a imagem enviada
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Converter para Base64 para envio via REST API
        image_b64 = base64.b64encode(downloaded_file).decode('utf-8')
        
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

        # URL limpo sem o parâmetro ?key=
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        # Passar o token AQ. como Bearer Token no Header
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_b64
                        }
                    }
                ]
            }]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_json = response.json()

        if response.status_code == 200:
            analysis_text = res_json['candidates'][0]['content']['parts'][0]['text']
            bot.reply_to(message, analysis_text, parse_mode='Markdown')
        else:
            error_msg = res_json.get('error', {}).get('message', 'Erro desconhecido na API da Google')
            bot.reply_to(message, f"❌ Erro da API Gemini ({response.status_code}): {error_msg}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erro no processamento: {str(e)}")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "Trading Office Bot está online via Webhook!", 200

if __name__ == "__main__":
    webhook_url = f"https://sala-do-trade.onrender.com/{TELEGRAM_TOKEN}"
    try:
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
    except Exception:
        pass
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
