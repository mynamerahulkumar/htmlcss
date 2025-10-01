# Complete Crypto News Trading Signal Generator
# Author: AI Assistant
# Purpose: Generate trading signals based on crypto news sentiment analysis

import requests
import feedparser
from bs4 import BeautifulSoup
import sqlite3
import json
import time
from datetime import datetime, timedelta
import re
from collections import Counter

class CryptoNewsTrader:
    def __init__(self, db_path='crypto_trading_news.db'):
        self.db_path = db_path
        self.setup_database()
        self.trading_keywords = {
            'bullish': ['bullish', 'moon', 'rally', 'surge', 'breakout', 'pump', 'growth', 
                       'adoption', 'partnership', 'approval', 'investment', 'institutional', 
                       'etf', 'buying', 'rocket', 'bull run', 'positive', 'optimistic'],
            'bearish': ['bearish', 'crash', 'dump', 'correction', 'decline', 'sell-off', 
                       'ban', 'regulation', 'hack', 'exploit', 'liquidation', 'fear', 
                       'drop', 'fall', 'plunge', 'red', 'negative', 'pessimistic'],
            'high_impact': ['fed', 'federal reserve', 'interest rate', 'inflation', 'cpi', 
                           'employment', 'gdp', 'tariff', 'trade war', 'government shutdown', 
                           'sec', 'regulatory', 'jerome powell', 'yellen', 'treasury']
        }
        
    def setup_database(self):
        """Setup SQLite database for storing news and signals"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS news_signals (
                id INTEGER PRIMARY KEY,
                title TEXT,
                url TEXT UNIQUE,
                source TEXT,
                published_date TEXT,
                content TEXT,
                sentiment_score REAL,
                trading_signal TEXT,
                confidence REAL,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
    def get_crypto_news_feeds(self):
        """Scrape multiple RSS feeds for crypto news"""
        feeds = {
            'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'cointelegraph': 'https://cointelegraph.com/rss',
            'cryptonews': 'https://cryptonews.com/news/feed/',
            'bitcoin_com': 'https://news.bitcoin.com/feed/',
            'decrypt': 'https://decrypt.co/feed',
            'bitcoinist': 'https://bitcoinist.com/feed/',
            'cryptoslate': 'https://cryptoslate.com/feed/'
        }
        
        all_news = []
        
        for source, feed_url in feeds.items():
            try:
                print(f"Fetching from {source}...")
                feed = feedparser.parse(feed_url)
                
                # Get recent entries
                for entry in feed.entries[:15]:  # Limit per source
                    news_item = {
                        'title': entry.title,
                        'url': entry.link,
                        'source': source,
                        'published': entry.published if hasattr(entry, 'published') else str(datetime.now()),
                        'content': entry.summary if hasattr(entry, 'summary') else entry.title,
                    }
                    all_news.append(news_item)
                    
                print(f"✅ Got {len(feed.entries[:15])} articles from {source}")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error fetching {source}: {e}")
                continue
                
        return all_news
    
    def scrape_economic_calendar_events(self):
        """Scrape or check for major economic events that affect crypto"""
        # This is a placeholder - you can integrate with economic calendar APIs
        # For now, we'll return some example high-impact events
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # These would typically come from an economic calendar API
        mock_events = [
            {
                'event': 'Federal Reserve Interest Rate Decision',
                'impact': 'high',
                'date': current_date,
                'description': 'Fed announces interest rate decision'
            },
            {
                'event': 'US CPI Data Release',
                'impact': 'high', 
                'date': current_date,
                'description': 'Consumer Price Index inflation data'
            }
        ]
        
        return mock_events
    
    def analyze_sentiment(self, text):
        """Advanced sentiment analysis using keyword matching and context"""
        text = text.lower()
        
        # Count bullish vs bearish keywords
        bullish_matches = []
        bearish_matches = []
        
        for keyword in self.trading_keywords['bullish']:
            if keyword in text:
                bullish_matches.append(keyword)
        
        for keyword in self.trading_keywords['bearish']:
            if keyword in text:
                bearish_matches.append(keyword)
        
        # Weight calculation
        bullish_count = len(bullish_matches)
        bearish_count = len(bearish_matches)
        
        # Calculate sentiment score (-1 to 1)
        total_keywords = bullish_count + bearish_count
        if total_keywords == 0:
            return 0, [], []
        
        sentiment_score = (bullish_count - bearish_count) / total_keywords
        return sentiment_score, bullish_matches, bearish_matches
    
    def generate_trading_signal(self, news_item):
        """Generate comprehensive trading signal based on news analysis"""
        title = news_item.get('title', '').lower()
        content = news_item.get('content', '').lower()
        full_text = f"{title} {content}"
        
        # Sentiment analysis
        sentiment_score, bullish_words, bearish_words = self.analyze_sentiment(full_text)
        
        # Check for high-impact keywords (macroeconomic factors)
        high_impact_matches = [keyword for keyword in self.trading_keywords['high_impact'] if keyword in full_text]
        high_impact_score = len(high_impact_matches)
        
        # Check for specific crypto mentions
        crypto_mentions = self.extract_crypto_mentions(full_text)
        
        # Generate base signal
        signal = "NEUTRAL"
        confidence = 0.5
        
        # Signal generation logic
        if sentiment_score > 0.2:
            signal = "BUY"
            confidence = 0.6 + (abs(sentiment_score) * 0.3)
        elif sentiment_score < -0.2:
            signal = "SELL"
            confidence = 0.6 + (abs(sentiment_score) * 0.3)
        
        # Boost confidence for high-impact news
        if high_impact_score > 0:
            confidence = min(0.95, confidence + (high_impact_score * 0.15))
            
        # Boost confidence for specific crypto mentions
        if len(crypto_mentions) > 0:
            confidence = min(0.95, confidence + 0.05)
        
        # Time-based urgency (recent news gets higher weight)
        try:
            if hasattr(news_item, 'published'):
                pub_time = datetime.strptime(news_item['published'][:19], '%Y-%m-%dT%H:%M:%S')
                hours_old = (datetime.now() - pub_time).total_seconds() / 3600
                if hours_old < 2:  # News less than 2 hours old
                    confidence = min(0.95, confidence + 0.05)
        except:
            pass
        
        # Source reliability multiplier
        source_multiplier = {
            'coindesk': 1.0,
            'cointelegraph': 0.95,
            'cryptonews': 0.85,
            'bitcoin_com': 0.9,
            'decrypt': 0.9,
            'bitcoinist': 0.85,
            'cryptoslate': 0.85
        }
        
        source = news_item.get('source', 'unknown')
        confidence *= source_multiplier.get(source, 0.7)
        
        return {
            'signal': signal,
            'confidence': round(confidence, 2),
            'sentiment_score': round(sentiment_score, 2),
            'crypto_mentions': crypto_mentions,
            'high_impact_keywords': high_impact_matches,
            'bullish_words': bullish_words,
            'bearish_words': bearish_words
        }
    
    def extract_crypto_mentions(self, text):
        """Extract cryptocurrency mentions from text"""
        crypto_patterns = {
            'bitcoin': r'\b(bitcoin|btc)\b',
            'ethereum': r'\b(ethereum|eth|ether)\b',
            'solana': r'\b(solana|sol)\b',
            'cardano': r'\b(cardano|ada)\b',
            'polygon': r'\b(polygon|matic)\b',
            'chainlink': r'\b(chainlink|link)\b',
            'avalanche': r'\b(avalanche|avax)\b',
            'dogecoin': r'\b(dogecoin|doge)\b',
            'xrp': r'\b(xrp|ripple)\b',
            'binance': r'\b(binance|bnb)\b',
            'litecoin': r'\b(litecoin|ltc)\b',
            'polkadot': r'\b(polkadot|dot)\b'
        }
        
        mentions = []
        for crypto, pattern in crypto_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                mentions.append(crypto.upper())
        
        return list(set(mentions))
    
    def save_news_signal(self, news_item, signal_data):
        """Save news and trading signal to database"""
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO news_signals 
                (title, url, source, published_date, content, sentiment_score, 
                 trading_signal, confidence, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_item['title'],
                news_item['url'],
                news_item['source'],
                news_item['published'],
                news_item['content'][:500],
                signal_data['sentiment_score'],
                signal_data['signal'],
                signal_data['confidence'],
                json.dumps({
                    'crypto_mentions': signal_data['crypto_mentions'],
                    'high_impact': signal_data['high_impact_keywords'],
                    'bullish': signal_data['bullish_words'],
                    'bearish': signal_data['bearish_words']
                })
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Error saving to database: {e}")
    
    def get_trading_recommendation(self, min_confidence=0.65, hours_back=6):
        """Get overall trading recommendation based on recent high-confidence signals"""
        try:
            cursor = self.conn.execute('''
                SELECT trading_signal, confidence, sentiment_score, source, title, keywords
                FROM news_signals 
                WHERE confidence > ? 
                AND datetime(created_at) > datetime('now', '-{} hours')
                ORDER BY confidence DESC, created_at DESC
            '''.format(hours_back), (min_confidence,))
            
            signals = cursor.fetchall()
            
            if not signals:
                return {
                    "recommendation": "HOLD",
                    "confidence": 0.5,
                    "reason": f"No high-confidence signals (>{min_confidence}) in last {hours_back} hours",
                    "signal_count": 0
                }
            
            # Calculate weighted recommendation
            buy_signals = 0
            sell_signals = 0
            neutral_signals = 0
            total_confidence = 0
            
            for signal in signals:
                trading_signal, confidence = signal[0], signal[1]
                
                if trading_signal == "BUY":
                    buy_signals += 1
                elif trading_signal == "SELL":
                    sell_signals += 1
                else:
                    neutral_signals += 1
                
                total_confidence += confidence
            
            # Generate recommendation with weighted confidence
            total_signals = len(signals)
            avg_confidence = total_confidence / total_signals
            
            if buy_signals > sell_signals * 1.5:  # Need clear buy majority
                recommendation = "BUY"
                overall_confidence = min(0.95, (buy_signals / total_signals) * avg_confidence)
            elif sell_signals > buy_signals * 1.5:  # Need clear sell majority
                recommendation = "SELL" 
                overall_confidence = min(0.95, (sell_signals / total_signals) * avg_confidence)
            else:
                recommendation = "HOLD"
                overall_confidence = 0.5
            
            return {
                'recommendation': recommendation,
                'overall_confidence': round(overall_confidence, 2),
                'signal_breakdown': {
                    'BUY': buy_signals,
                    'SELL': sell_signals,
                    'NEUTRAL': neutral_signals
                },
                'total_signals': total_signals,
                'avg_confidence': round(avg_confidence, 2),
                'analysis_period_hours': hours_back,
                'top_signals': [
                    {
                        'signal': s[0],
                        'confidence': s[1],
                        'sentiment': s[2],
                        'source': s[3],
                        'title': s[4][:100] + '...' if len(s[4]) > 100 else s[4]
                    }
                    for s in signals[:5]
                ]
            }
            
        except Exception as e:
            print(f"Error getting recommendation: {e}")
            return {"error": str(e)}
    
    def get_crypto_specific_signals(self, crypto_symbol, hours_back=24):
        """Get signals specific to a particular cryptocurrency"""
        try:
            cursor = self.conn.execute('''
                SELECT trading_signal, confidence, sentiment_score, source, title, keywords
                FROM news_signals 
                WHERE keywords LIKE ? 
                AND datetime(created_at) > datetime('now', '-{} hours')
                AND confidence > 0.6
                ORDER BY confidence DESC
            '''.format(hours_back), (f'%{crypto_symbol.upper()}%',))
            
            signals = cursor.fetchall()
            
            if not signals:
                return {
                    "crypto": crypto_symbol,
                    "recommendation": "HOLD",
                    "reason": f"No specific signals for {crypto_symbol} in last {hours_back} hours"
                }
            
            # Analyze crypto-specific signals
            buy_count = sum(1 for s in signals if s[0] == 'BUY')
            sell_count = sum(1 for s in signals if s[0] == 'SELL')
            avg_confidence = sum(s[1] for s in signals) / len(signals)
            
            if buy_count > sell_count:
                recommendation = "BUY"
            elif sell_count > buy_count:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"
            
            return {
                'crypto': crypto_symbol,
                'recommendation': recommendation,
                'confidence': round(avg_confidence, 2),
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'total_signals': len(signals),
                'recent_news': [s[4][:100] + '...' for s in signals[:3]]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def run_analysis(self, min_confidence=0.65):
        """Main function to run complete news analysis and generate trading signals"""
        print("🚀 CRYPTO NEWS TRADING SIGNAL GENERATOR")
        print("=" * 60)
        
        # Get news from RSS feeds
        print("\n📰 Fetching crypto news from multiple sources...")
        all_news = self.get_crypto_news_feeds()
        
        if not all_news:
            print("❌ No news articles found!")
            return None
            
        print(f"\n✅ Total news articles collected: {len(all_news)}")
        
        # Analyze each news item
        print(f"\n🔍 Analyzing news for trading signals (min confidence: {min_confidence})...")
        print("-" * 60)
        
        high_confidence_signals = []
        
        for i, news_item in enumerate(all_news, 1):
            try:
                signal_data = self.generate_trading_signal(news_item)
                self.save_news_signal(news_item, signal_data)
                
                # Print high-confidence signals as we find them
                if signal_data['confidence'] >= min_confidence:
                    print(f"🎯 Signal #{len(high_confidence_signals)+1}: {signal_data['signal']} (Confidence: {signal_data['confidence']})")
                    print(f"   📰 {news_item['title'][:80]}...")
                    print(f"   🏷️  Source: {news_item['source']}")
                    if signal_data['crypto_mentions']:
                        print(f"   🪙 Cryptos: {', '.join(signal_data['crypto_mentions'])}")
                    if signal_data['high_impact_keywords']:
                        print(f"   ⚡ Impact Keywords: {', '.join(signal_data['high_impact_keywords'])}")
                    print("-" * 60)
                    
                    high_confidence_signals.append({
                        'news': news_item,
                        'signal': signal_data
                    })
                
            except Exception as e:
                print(f"❌ Error processing news item {i}: {e}")
                continue
        
        # Get overall trading recommendation
        print(f"\n📊 GENERATING OVERALL TRADING RECOMMENDATION...")
        recommendation = self.get_trading_recommendation(min_confidence)
        
        return {
            'total_news': len(all_news),
            'high_confidence_signals': len(high_confidence_signals),
            'recommendation': recommendation,
            'detailed_signals': high_confidence_signals
        }
    
    def export_signals_to_csv(self, filename='crypto_signals.csv'):
        """Export trading signals to CSV for further analysis"""
        try:
            cursor = self.conn.execute('''
                SELECT title, source, trading_signal, confidence, sentiment_score, 
                       published_date, created_at
                FROM news_signals 
                ORDER BY created_at DESC
            ''')
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                import csv
                writer = csv.writer(csvfile)
                writer.writerow(['Title', 'Source', 'Signal', 'Confidence', 'Sentiment', 'Published', 'Analyzed'])
                
                for row in cursor:
                    writer.writerow(row)
            
            print(f"✅ Signals exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")

# Usage Example and Main Execution
if __name__ == "__main__":
    # Initialize the trader
    trader = CryptoNewsTrader()
    
    # Run complete analysis
    results = trader.run_analysis(min_confidence=0.7)
    
    if results:
        print("\n" + "🎯" * 30)
        print("FINAL TRADING RECOMMENDATION")
        print("🎯" * 30)
        
        rec = results['recommendation']
        print(f"\n💡 RECOMMENDATION: {rec['recommendation']}")
        print(f"🎯 CONFIDENCE: {rec['overall_confidence']}")
        print(f"📊 BASED ON: {rec['total_signals']} high-confidence signals")
        print(f"📈 SIGNAL BREAKDOWN: {rec['signal_breakdown']}")
        
        if rec.get('top_signals'):
            print(f"\n🔝 TOP SIGNALS:")
            for i, signal in enumerate(rec['top_signals'][:3], 1):
                print(f"{i}. {signal['signal']} ({signal['confidence']}) - {signal['title']}")
        
        print("\n💰 TRADING ADVICE:")
        if rec['recommendation'] == 'BUY' and rec['overall_confidence'] > 0.75:
            print("✅ Strong BUY signal detected. Consider entering long positions.")
            print("   📊 Monitor entry points and set stop losses.")
        elif rec['recommendation'] == 'SELL' and rec['overall_confidence'] > 0.75:
            print("🔴 Strong SELL signal detected. Consider reducing positions or shorting.")
            print("   📊 Consider taking profits and tightening stop losses.")
        else:
            print("⚠️  Mixed signals or moderate confidence. Consider:")
            print("   📊 Wait for clearer signals")
            print("   📊 Hold current positions")
            print("   📊 Use smaller position sizes")
        
        # Export results for further analysis
        trader.export_signals_to_csv()
        
        # Get Bitcoin-specific analysis
        print(f"\n🪙 BITCOIN-SPECIFIC ANALYSIS:")
        btc_signals = trader.get_crypto_specific_signals('BITCOIN')
        print(f"   Recommendation: {btc_signals.get('recommendation', 'HOLD')}")
        print(f"   Confidence: {btc_signals.get('confidence', 0)}")
        
    else:
        print("❌ Analysis failed to complete.")
    
    # Close database connection
    trader.conn.close()
    print("\n✅ Analysis complete. Database saved.")