# analysis/basic_analyzer.py
"""基礎除息分析器"""

from datetime import datetime, date
from typing import List, Dict, Any
from config import DIVIDEND_CALENDAR, ETF_INFO

class BasicDividendAnalyzer:
    """基礎除息分析器"""
    
    def __init__(self):
        self.dividend_calendar = DIVIDEND_CALENDAR
        self.etf_info = ETF_INFO
    
    def find_dividend_opportunities(self) -> List[Dict[str, Any]]:
        """尋找配息機會"""
        today = date.today()
        opportunities = []
        
        for etf, dividend_dates in self.dividend_calendar.items():
            for div_date_str in dividend_dates:
                try:
                    div_date = datetime.strptime(div_date_str, '%Y-%m-%d').date()
                    
                    # 買進機會
                    days_after = (today - div_date).days
                    if 1 <= days_after <= 7:
                        opportunities.append({
                            'etf': etf,
                            'action': 'BUY',
                            'dividend_date': div_date_str,
                            'days_after': days_after,
                            'priority': self.etf_info[etf]['priority'],
                            'reason': f'除息後第{days_after}天，建議買進',
                            'confidence': 'high' if days_after <= 3 else 'medium'
                        })
                    
                    # 清倉提醒
                    days_to = (div_date - today).days
                    if 0 <= days_to <= 3:
                        opportunities.append({
                            'etf': etf,
                            'action': 'PREPARE',
                            'dividend_date': div_date_str,
                            'days_to_dividend': days_to,
                            'priority': self.etf_info[etf]['priority'],
                            'reason': f'{days_to}天後除息，準備清倉',
                            'confidence': 'high'
                        })
                        
                except ValueError:
                    continue
        
        return sorted(opportunities, key=lambda x: x['priority'])

# analysis/technical_analyzer.py
"""技術分析器"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from config import TECHNICAL_PARAMS

class TechnicalAnalyzer:
    """技術分析器"""
    
    def __init__(self):
        self.params = TECHNICAL_PARAMS
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標"""
        if df is None or len(df) < 30:
            return df
        
        df = df.copy()
        
        # 移動平均線
        df['MA5'] = df['close'].rolling(window=self.params['ma_short']).mean()
        df['MA10'] = df['close'].rolling(window=self.params['ma_medium']).mean()  
        df['MA20'] = df['close'].rolling(window=self.params['ma_long']).mean()
        
        # RSI
        df = self._calculate_rsi(df)
        
        # 布林帶
        df = self._calculate_bollinger_bands(df)
        
        # 成交量指標
        df['Volume_MA'] = df['volume'].rolling(window=10).mean()
        df['Volume_Ratio'] = df['volume'] / df['Volume_MA']
        
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params['rsi_period']).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算布林帶"""
        period = self.params['bb_period']
        std_dev = self.params['bb_std_dev']
        
        df['BB_Middle'] = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        df['BB_Upper'] = df['BB_Middle'] + (std * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (std * std_dev)
        df['BB_Position'] = (df['close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """生成技術信號"""
        if df is None or len(df) < 30:
            return []
        
        latest = df.iloc[-1]
        signals = []
        
        # RSI信號
        if latest['RSI'] < self.params['rsi_oversold']:
            signals.append({
                'type': 'RSI',
                'signal': 'STRONG_BUY',
                'strength': 90,
                'description': f'RSI超賣({latest["RSI"]:.1f})，強烈買進信號'
            })
        elif latest['RSI'] > self.params['rsi_overbought']:
            signals.append({
                'type': 'RSI',
                'signal': 'SELL',
                'strength': 60,
                'description': f'RSI超買({latest["RSI"]:.1f})，賣出信號'
            })
        
        # 布林帶信號
        if latest['BB_Position'] < 0.1:
            signals.append({
                'type': 'Bollinger',
                'signal': 'STRONG_BUY',
                'strength': 85,
                'description': '價格接近布林下軌，反彈機會大'
            })
        elif latest['BB_Position'] > 0.9:
            signals.append({
                'type': 'Bollinger',
                'signal': 'SELL',
                'strength': 70,
                'description': '價格接近布林上軌，回調風險高'
            })
        
        # 移動平均信號
        if latest['close'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
            signals.append({
                'type': 'MA_Trend',
                'signal': 'BUY',
                'strength': 75,
                'description': '多頭排列，趨勢向上'
            })
        
        return signals
    
    def calculate_score(self, df: pd.DataFrame) -> float:
        """計算技術分析綜合評分"""
        if df is None or len(df) < 30:
            return 50
        
        latest = df.iloc[-1]
        score = 50
        
        # RSI評分
        if 30 <= latest['RSI'] <= 70:
            score += 10
        elif latest['RSI'] < 30:
            score += 20
        elif latest['RSI'] > 70:
            score -= 15
        
        # 布林帶評分
        bb_pos = latest['BB_Position']
        if 0.2 <= bb_pos <= 0.8:
            score += 10
        elif bb_pos < 0.2:
            score += 20
        else:
            score -= 15
        
        # 移動平均評分
        if latest['close'] > latest['MA20']:
            score += 15
        if latest['MA5'] > latest['MA20']:
            score += 10
        
        return max(0, min(100, score))

# analysis/risk_analyzer.py
"""風險分析器"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from config import RISK_WEIGHTS, RISK_LEVELS

class RiskAnalyzer:
    """風險分析器"""
    
    def __init__(self):
        self.risk_weights = RISK_WEIGHTS
        self.risk_levels = RISK_LEVELS
    
    def calculate_comprehensive_risk(self, 
                                   opportunity: Dict[str, Any],
                                   technical_signals: List[Dict[str, Any]],
                                   etf_data: pd.DataFrame) -> Dict[str, Any]:
        """計算綜合風險評估"""
        
        # 各項風險計算
        technical_risk = self._calculate_technical_risk(technical_signals)
        timing_risk = self._calculate_timing_risk(opportunity)
        volatility_risk = self._calculate_volatility_risk(etf_data)
        market_risk = self._calculate_market_risk(opportunity.get('etf', ''))
        
        # 綜合風險評分
        comprehensive_risk = (
            technical_risk * self.risk_weights['technical_risk'] +
            timing_risk * self.risk_weights['timing_risk'] +
            volatility_risk * self.risk_weights['volatility_risk'] +
            market_risk * self.risk_weights['market_risk']
        )
        
        return {
            'comprehensive_risk_score': comprehensive_risk,
            'risk_level': self._get_risk_level(comprehensive_risk),
            'risk_breakdown': {
                'technical_risk': technical_risk,
                'timing_risk': timing_risk,
                'volatility_risk': volatility_risk,
                'market_risk': market_risk
            }
        }
    
    def _calculate_technical_risk(self, technical_signals: List[Dict[str, Any]]) -> float:
        """計算技術風險"""
        if not technical_signals:
            return 50
        
        risk_score = 50
        
        for signal in technical_signals:
            signal_type = signal.get('signal', '')
            strength = signal.get('strength', 50)
            
            if signal_type in ['STRONG_SELL', 'SELL']:
                risk_score += strength * 0.3
            elif signal_type in ['STRONG_BUY', 'BUY']:
                risk_score -= strength * 0.2
        
        return max(0, min(100, risk_score))
    
    def _calculate_timing_risk(self, opportunity: Dict[str, Any]) -> float:
        """計算時機風險"""
        risk_score = 50
        
        if 'days_after' in opportunity:
            days_after = opportunity['days_after']
            if days_after <= 3:
                risk_score -= 20
            elif days_after <= 7:
                risk_score -= 10
            else:
                risk_score += 15
        
        if 'days_to_dividend' in opportunity:
            days_to = opportunity['days_to_dividend']
            if days_to <= 3:
                risk_score += 25
        
        return max(0, min(100, risk_score))
    
    def _calculate_volatility_risk(self, etf_data: pd.DataFrame) -> float:
        """計算波動性風險"""
        if etf_data is None or len(etf_data) < 10:
            return 50
        
        try:
            returns = etf_data['close'].pct_change().dropna()
            if len(returns) < 5:
                return 50
            
            volatility = returns.std() * np.sqrt(252)
            
            risk_score = 50
            if volatility > 0.3:
                risk_score += 25
            elif volatility > 0.2:
                risk_score += 10
            elif volatility < 0.1:
                risk_score -= 15
            
            return max(0, min(100, risk_score))
            
        except Exception:
            return 50
    
    def _calculate_market_risk(self, etf_code: str) -> float:
        """計算市場風險"""
        from config import ETF_INFO
        
        beta = ETF_INFO.get(etf_code, {}).get('beta', 0.8)
        base_risk = 50
        
        if beta > 1.0:
            base_risk += (beta - 1.0) * 20
        else:
            base_risk -= (1.0 - beta) * 10
        
        return max(0, min(100, base_risk))
    
    def _get_risk_level(self, risk_score: float) -> str:
        """獲取風險等級"""
        for level, (min_score, max_score) in self.risk_levels.items():
            if min_score <= risk_score < max_score:
                return level
        return 'very_high'

# analysis/__init__.py
"""分析模組初始化"""

from .basic_analyzer import BasicDividendAnalyzer
from .technical_analyzer import TechnicalAnalyzer
from .risk_analyzer import RiskAnalyzer

__all__ = [
    'BasicDividendAnalyzer',
    'TechnicalAnalyzer',
    'RiskAnalyzer'
]
