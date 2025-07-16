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
