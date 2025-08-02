import os
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify
from bot import TradingBot

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize trading bot
trading_bot = TradingBot()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', 
                         bot_running=trading_bot.is_running(),
                         latest_signal=trading_bot.get_latest_signal(),
                         signal_history=trading_bot.get_signal_history(),
                         settings=trading_bot.get_settings())

@app.route('/settings')
def settings():
    """Settings configuration page"""
    return render_template('settings.html', settings=trading_bot.get_settings())

@app.route('/toggle_bot', methods=['POST'])
def toggle_bot():
    """Start or stop the trading bot"""
    if trading_bot.is_running():
        trading_bot.stop()
        logging.info("Trading bot stopped")
    else:
        trading_bot.start()
        logging.info("Trading bot started")
    return redirect(url_for('index'))

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update bot settings"""
    settings = {
        'telegram_chat_id': request.form.get('telegram_chat_id'),
        'rsi_period': int(request.form.get('rsi_period', 14)),
        'rsi_overbought': int(request.form.get('rsi_overbought', 70)),
        'rsi_oversold': int(request.form.get('rsi_oversold', 30)),
        'stoch_k': int(request.form.get('stoch_k', 14)),
        'stoch_d': int(request.form.get('stoch_d', 3)),
        'stoch_slow': int(request.form.get('stoch_slow', 3)),
        'ema_fast': int(request.form.get('ema_fast', 50)),
        'ema_slow': int(request.form.get('ema_slow', 200)),
        'signal_interval': int(request.form.get('signal_interval', 15)),
        'use_rsi': 'use_rsi' in request.form,
        'use_stoch': 'use_stoch' in request.form,
        'use_ema': 'use_ema' in request.form,
        'selected_pairs': request.form.getlist('pairs')
    }
    
    trading_bot.update_settings(settings)
    logging.info("Settings updated")
    return redirect(url_for('settings'))

@app.route('/api/status')
def api_status():
    """API endpoint for real-time status updates"""
    return jsonify({
        'running': trading_bot.is_running(),
        'latest_signal': trading_bot.get_latest_signal(),
        'signal_count': len(trading_bot.get_signal_history()),
        'winrate': trading_bot.get_winrate()
    })

@app.route('/api/signals')
def api_signals():
    """API endpoint for signal history"""
    return jsonify(trading_bot.get_signal_history())

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear signal history"""
    trading_bot.clear_history()
    logging.info("Signal history cleared")
    return redirect(url_for('index'))
