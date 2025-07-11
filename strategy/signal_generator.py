"""信號生成器"""

from typing import Dict, Any, List
from config import POSITION_SIZING

class SignalGenerator:
    """交易信號生成器"""
    
    def __init__(self):
        self.position_sizing = POSITION_SIZING
    
    def generate_final_recommendation(self, 
                                    opportunity: Dict[str, Any],
                                    technical_score: float,
                                    risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """生成最終投資建議"""
        
        action = opportunity.get('action', '')
        risk_level = risk_assessment.get('risk_level', 'medium')
        
        if action == 'BUY':
            return self._generate_buy_recommendation(
                opportunity, technical_score, risk_level
            )
        elif action == 'PREPARE':
            return {
                'action': 'SELL_PREPARE',
                'reasoning': '即將除息，建議準備清倉',
                'urgency': 'high',
                'confidence': 'high'
            }
        
        return {
            'action': 'MONITOR',
            'reasoning': '持續監控中',
            'urgency': 'none',
            'confidence': 'medium'
        }
    
    def _generate_buy_recommendation(self, 
                                   opportunity: Dict[str, Any],
                                   technical_score: float,
                                   risk_level: str) -> Dict[str, Any]:
        """生成買進建議"""
        
        if technical_score >= 80 and risk_level in ['very_low', 'low']:
            return {
                'action': 'STRONG_BUY',
                'reasoning': '技術面強勁，風險可控，強烈建議買進',
                'urgency': 'high',
                'confidence': 'very_high'
            }
        elif technical_score >= 60 and risk_level in ['very_low', 'low', 'medium']:
            return {
                'action': 'BUY',
                'reasoning': '技術面良好，適合買進',
                'urgency': 'medium',
                'confidence': 'high'
            }
        elif risk_level in ['high', 'very_high']:
            return {
                'action': 'CAUTIOUS_BUY',
                'reasoning': '機會存在但風險較高，建議小額試單',
                'urgency': 'low',
                'confidence': 'medium'
            }
        else:
            return {
                'action': 'HOLD',
                'reasoning': '技術面或風險條件不理想，建議觀望',
                'urgency': 'none',
                'confidence': 'low'
            }
    
    def calculate_position_sizing(self, 
                                risk_assessment: Dict[str, Any],
                                opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """計算投資規模建議"""
        
        risk_level = risk_assessment.get('risk_level', 'medium')
        confidence = opportunity.get('confidence', 'medium')
        
        # 基礎配置比例
        base_allocation = self.position_sizing.get(f'{risk_level}_risk', 0.15)
        
        # 信心度調整
        confidence_multipliers = {
            'very_high': 1.3,
            'high': 1.1,
            'medium': 1.0,
            'low': 0.7
        }
        
        final_allocation = base_allocation * confidence_multipliers.get(confidence, 1.0)
        final_allocation = min(final_allocation, self.position_sizing['max_single_position'])
        
        return {
            'suggested_allocation_pct': final_allocation * 100,
            'risk_level': risk_level,
            'confidence_level': confidence,
            'allocation_reasoning': f"基於{risk_level}風險等級和{confidence}信心度"
        }
    
    def calculate_enhanced_confidence(self,
                                    opportunity: Dict[str, Any],
                                    technical_score: float,
                                    risk_assessment: Dict[str, Any]) -> str:
        """計算增強版信心度"""
        
        base_confidence = opportunity.get('confidence', 'medium')
        
        # 信心度分數映射
        confidence_scores = {'low': 25, 'medium': 50, 'high': 75, 'very_high': 90}
        base_score = confidence_scores.get(base_confidence, 50)
        
        # 技術分析調整
        if technical_score >= 80:
            base_score += 15
        elif technical_score >= 60:
            base_score += 5
        elif technical_score <= 40:
            base_score -= 15
        
        # 風險調整
        risk_level = risk_assessment.get('risk_level', 'medium')
        risk_adjustments = {
            'very_low': 10, 'low': 5, 'medium': 0, 'high': -10, 'very_high': -20
        }
        base_score += risk_adjustments.get(risk_level, 0)
        
        # 轉換回信心等級
        final_score = max(0, min(100, base_score))
        
        if final_score >= 85:
            return 'very_high'
        elif final_score >= 65:
            return 'high'
        elif final_score >= 45:
            return 'medium'
        else:
            return 'low'
