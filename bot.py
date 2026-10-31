import os
import telebot
import requests
from google import genai
from PIL import Image
import io
from flask import Flask, request

# Credenciais integradas
TELEGRAM_TOKEN = "9140335855:AAGjj8Mu18YyA4HJ7_DiL-IT1D7_LVCJdJA"
GEMINI_API_KEY = "AQ.Ab8RN6I2_L9IUIvKm597mC8Vj4PL5Oq1n4VcYJzPQSsn93UPkA"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

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

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt]
        )
        
        bot.reply_to(message, response.text, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erro na análise visual: {str(e)}")

# Rota do Webhook para receber as mensagens do Telegram
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().astype(str) if hasattr(request.get_data(), 'astype') else request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "Trading Office Bot está online via Webhook!", 200

if __name__ == "__main__":
    # Configurar o Webhook automaticamente no Telegram
    webhook_url = f"https://sala-do-trade.onrender.com/{TELEGRAM_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    
    # O Render atribui uma porta dinâmica através da variável PORT (por defeito 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
