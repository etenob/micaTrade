# send_signals.py
from Telegram.telegram_helper import send_telegram_message
from services.enhanced_analysis_service import enhanced_analysis_service
from config import Config  # Para tomar la lista de símbolos

def main():
    for symbol in Config.TRADING_SYMBOLS:
        result = enhanced_analysis_service.analyze_symbol_merino(symbol)
        
        if result and result['signal_type'] in ['LONG', 'SHORT']:
            # Armar mensaje combinando análisis y recomendación
            message = (
                f"{result['analysis_text']}\n\n"
                f"{enhanced_analysis_service._generate_merino_recommendation(symbol, result['current_price'], result['signal'], result['capital_allocation'])}"
            )
            Telegram.alert_manager.send_alert(symbol, message)
            print(f"✅ Señal enviada para {symbol}: {result['signal_type']}")
        else:
            print(f"⚪ Sin señal relevante para {symbol}")

if __name__ == "__main__":
    main()
