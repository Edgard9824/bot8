import threading
import time
import random
import requests
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

class TradingBot:
    """Main trading bot class that handles signal generation and Telegram notifications"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.signal_history = []
        self.latest_signal = {}
        
        # Default settings
        self.settings = {
            'telegram_token': os.getenv('TELEGRAM_TOKEN', '8472684949:AAG9Qd7bHt-7BRhNw-7x4nQp3a1Eq2Uoq8k'),
            'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
            'pairs': [
                'EURUSD-OTC', 'GBPUSD-OTC', 'USDJPY-OTC', 
                'AUDUSD-OTC', 'NZDUSD-OTC', 'EURJPY-OTC',
                'USDCAD-OTC', 'EURGBP-OTC', 'AUDNZD-OTC'
            ],
            'selected_pairs': ['EURUSD-OTC', 'GBPUSD-OTC', 'USDJPY-OTC'],
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'stoch_k': 14,
            'stoch_d': 3,
            'stoch_slow': 3,
            'ema_fast': 50,
            'ema_slow': 200,
            'signal_interval': 15,
            'use_rsi': True,
            'use_stoch': True,
            'use_ema': True
        }
    
    def start(self):
        """Start the trading bot in a separate thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_bot, daemon=True)
            self.thread.start()
            logging.info("Trading bot started")
    
    def stop(self):
        """Stop the trading bot"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logging.info("Trading bot stopped")
    
    def is_running(self) -> bool:
        """Check if bot is currently running"""
        return self.running
    
    def get_settings(self) -> Dict:
        """Get current bot settings"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict):
        """Update bot settings"""
        self.settings.update(new_settings)
    
    def get_signal_history(self) -> List[Dict]:
        """Get signal history (last 50 signals)"""
        return self.signal_history[-50:]
    
    def get_latest_signal(self) -> Dict:
        """Get the latest signal"""
        return self.latest_signal.copy() if self.latest_signal else {}
    
    def clear_history(self):
        """Clear signal history"""
        self.signal_history.clear()
        self.latest_signal = {}
    
    def get_winrate(self) -> float:
        """Calculate winrate from recent signals"""
        if len(self.signal_history) < 10:
            return 0.0
        
        recent_signals = self.signal_history[-20:]
        winning_signals = sum(1 for signal in recent_signals if signal.get('result') == 'win')
        return (winning_signals / len(recent_signals)) * 100 if recent_signals else 0.0
    
    def _run_bot(self):
        """Main bot loop - generates signals based on technical analysis"""
        logging.info("Trading bot main loop started")
        
        while self.running:
            try:
                # Wait for the right timing (every 15 seconds by default)
                current_time = datetime.now()
                if current_time.second % self.settings['signal_interval'] == 0:
                    signal = self._generate_signal()
                    if signal:
                        self._process_signal(signal)
                
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error in bot loop: {e}")
                time.sleep(5)
    
    def _generate_signal(self) -> Optional[Dict]:
        """Generate trading signal based on technical indicators"""
        try:
            # Select random pair from configured pairs
            pair = random.choice(self.settings['selected_pairs'])
            
            # Generate mock technical indicator values
            # In a real implementation, these would come from market data API
            rsi = random.randint(20, 80)
            stoch_k = random.randint(10, 90)
            stoch_d = random.randint(10, 90)
            ema_fast = random.uniform(1.1000, 1.2000)
            ema_slow = random.uniform(1.1000, 1.2000)
            
            # Apply indicator filters
            signal_valid = True
            reasons = []
            
            if self.settings['use_rsi']:
                if not (rsi <= self.settings['rsi_oversold'] or rsi >= self.settings['rsi_overbought']):
                    signal_valid = False
                    reasons.append("RSI not in signal range")
            
            if self.settings['use_stoch']:
                if not ((stoch_k < 20 and stoch_d < 20) or (stoch_k > 80 and stoch_d > 80)):
                    signal_valid = False
                    reasons.append("Stochastic not in signal range")
            
            if self.settings['use_ema']:
                trend = 'bullish' if ema_fast > ema_slow else 'bearish'
                if abs(ema_fast - ema_slow) < 0.0010:  # Too close
                    signal_valid = False
                    reasons.append("EMA too close for clear trend")
            else:
                trend = 'neutral'
            
            # Generate signal direction
            if rsi <= self.settings['rsi_oversold'] or (stoch_k < 20 and stoch_d < 20):
                direction = 'CALL'
                arrow = '🔺'
            else:
                direction = 'PUT'
                arrow = '🔻'
            
            # Only return signal if all conditions are met
            if signal_valid:
                return {
                    'pair': pair,
                    'direction': direction,
                    'arrow': arrow,
                    'rsi': rsi,
                    'stoch_k': stoch_k,
                    'stoch_d': stoch_d,
                    'ema_fast': ema_fast,
                    'ema_slow': ema_slow,
                    'trend': trend,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'confidence': random.randint(75, 95),
                    'entry_time': (datetime.now().timestamp() + 30),  # Entry in 30 seconds
                    'reasons': reasons
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Error generating signal: {e}")
            return None
    
    def _process_signal(self, signal: Dict):
        """Process and distribute a new signal"""
        try:
            # Add result simulation (for winrate calculation)
            signal['result'] = random.choice(['win', 'win', 'win', 'loss'])  # 75% win rate simulation
            
            # Store signal
            self.latest_signal = signal
            self.signal_history.append(signal)
            
            # Keep only last 100 signals
            if len(self.signal_history) > 100:
                self.signal_history = self.signal_history[-100:]
            
            # Send Telegram notification
            self._send_telegram_notification(signal)
            
            logging.info(f"Signal processed: {signal['pair']} {signal['direction']} at {signal['timestamp']}")
            
        except Exception as e:
            logging.error(f"Error processing signal: {e}")
    
    def _send_telegram_notification(self, signal: Dict):
        """Send signal notification to Telegram"""
        if not self.settings['telegram_chat_id']:
            logging.debug("No Telegram chat ID configured, skipping notification")
            return
        
        try:
            winrate = self.get_winrate()
            
            message = (
                f"🚀 <b>POCKET OPTION SIGNAL</b>\n\n"
                f"📊 Pair: <b>{signal['pair']}</b>\n"
                f"📈 Direction: <b>{signal['arrow']} {signal['direction']}</b>\n"
                f"⏰ Time: {signal['timestamp']}\n"
                f"🎯 Confidence: {signal['confidence']}%\n\n"
                f"📋 <b>Technical Analysis:</b>\n"
                f"RSI: {signal['rsi']}\n"
                f"Stochastic: {signal['stoch_k']}/{signal['stoch_d']}\n"
                f"EMA Trend: {signal['trend']}\n\n"
                f"📊 Current Winrate: {winrate:.1f}%\n"
                f"⏳ <b>Enter trade in 30 seconds</b>"
            )
            
            url = f"https://api.telegram.org/bot{self.settings['telegram_token']}/sendMessage"
            data = {
                'chat_id': self.settings['telegram_chat_id'],
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logging.debug("Telegram notification sent successfully")
            else:
                logging.error(f"Failed to send Telegram notification: {response.status_code}")
                
        except Exception as e:
            logging.error(f"Error sending Telegram notification: {e}")
