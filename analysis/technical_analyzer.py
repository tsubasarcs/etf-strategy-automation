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
