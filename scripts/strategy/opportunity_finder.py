"""機會發現器"""

from typing import List, Dict, Any
from analysis import BasicDividendAnalyzer, TechnicalAnalyzer, RiskAnalyzer
from .signal_generator import SignalGenerator

class OpportunityFinder:
    """投資機會發現器"""
    
    def __init__(self):
        self.basic_analyzer = BasicDividendAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.signal_generator = SignalGenerator()
    
    def find_enhanced_opportunities(self, etf_data_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """尋找增強版投資機會"""
        
        # 1. 基礎除息機會分析
        basic_opportunities = self.basic_analyzer.find_dividend_opportunities()
        
        # 2. 對每個機會進行增強分析
        enhanced_opportunities = []
        
        for opportunity in basic_opportunities:
            etf_code = opportunity.get('etf', '')
            etf_data = etf_data_dict.get(etf_code)
            
            if etf_data is not None and len(etf_data) >= 30:
                enhanced_opp = self._enhance_opportunity(opportunity, etf_data)
                enhanced_opportunities.append(enhanced_opp)
            else:
                # 如果沒有足夠數據，使用基礎分析
                enhanced_opportunities.append(opportunity)
        
        return enhanced_opportunities
    
    def _enhance_opportunity(self, opportunity: Dict[str, Any], etf_data) -> Dict[str, Any]:
        """增強單個機會分析"""
        
        # 技術分析
        etf_df_with_indicators = self.technical_analyzer.calculate_indicators(etf_data)
        technical_signals = self.technical_analyzer.generate_signals(etf_df_with_indicators)
        technical_score = self.technical_analyzer.calculate_score(etf_df_with_indicators)
        
        # 風險評估
        risk_assessment = self.risk_analyzer.calculate_comprehensive_risk(
            opportunity, technical_signals, etf_data
        )
        
        # 信號生成
        final_recommendation = self.signal_generator.generate_final_recommendation(
            opportunity, technical_score, risk_assessment
        )
        
        position_sizing = self.signal_generator.calculate_position_sizing(
            risk_assessment, opportunity
        )
        
        enhanced_confidence = self.signal_generator.calculate_enhanced_confidence(
            opportunity, technical_score, risk_assessment
        )
        
        # 整合所有分析結果
        enhanced_opportunity = opportunity.copy()
        enhanced_opportunity.update({
            'technical_analysis': {
                'score': technical_score,
                'signals': technical_signals
            },
            'risk_assessment': risk_assessment,
            'final_recommendation': final_recommendation,
            'position_sizing': position_sizing,
            'enhanced_confidence': enhanced_confidence
        })
        
        return enhanced_opportunity
