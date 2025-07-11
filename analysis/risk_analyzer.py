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
