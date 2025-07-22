"""基礎除息分析器 - v2.0 更新版（使用新配置系統）"""

from datetime import datetime, date
from typing import List, Dict, Any

# 使用新的配置系統
from config import ETF_INFO
from config.etf_config import get_dividend_schedule

class BasicDividendAnalyzer:
    """基礎除息分析器 - 使用新配置系統"""
    
    def __init__(self):
        self.etf_info = ETF_INFO
        # 動態載入除息日程
        self._load_dividend_schedule()
    
    def _load_dividend_schedule(self):
        """動態載入除息日程"""
        try:
            self.dividend_calendar = get_dividend_schedule()
            print(f"📅 除息分析器載入: {len(self.dividend_calendar)} 個ETF日程")
        except Exception as e:
            print(f"⚠️ 除息日程載入失敗: {e}")
            # 使用緊急備用日程
            self.dividend_calendar = self._get_emergency_schedule()
    
    def _get_emergency_schedule(self) -> Dict[str, List[str]]:
        """緊急備用日程"""
        today = date.today()
        current_year = today.year
        
        return {
            "0056": [f"{current_year}-10-16", f"{current_year+1}-01-16", f"{current_year+1}-04-16"],
            "00878": [f"{current_year}-11-21", f"{current_year+1}-02-20", f"{current_year+1}-05-19"], 
            "00919": [f"{current_year}-12-16", f"{current_year+1}-03-17", f"{current_year+1}-06-17"]
        }
    
    def find_dividend_opportunities(self) -> List[Dict[str, Any]]:
        """尋找配息機會"""
        today = date.today()
        opportunities = []
        
        for etf, dividend_dates in self.dividend_calendar.items():
            for div_date_str in dividend_dates:
                try:
                    div_date = datetime.strptime(div_date_str, '%Y-%m-%d').date()
                    
                    # 買進機會（除息後1-7天）
                    days_after = (today - div_date).days
                    if 1 <= days_after <= 7:
                        opportunities.append({
                            'etf': etf,
                            'action': 'BUY',
                            'dividend_date': div_date_str,
                            'days_after': days_after,
                            'priority': self.etf_info.get(etf, {}).get('priority', 99),
                            'reason': f'除息後第{days_after}天，建議買進',
                            'confidence': 'high' if days_after <= 3 else 'medium',
                            'expected_return': self.etf_info.get(etf, {}).get('expected_return', 0),
                            'success_rate': self.etf_info.get(etf, {}).get('success_rate', 0.5)
                        })
                    
                    # 清倉提醒（除息前0-3天）
                    days_to = (div_date - today).days
                    if 0 <= days_to <= 3:
                        opportunities.append({
                            'etf': etf,
                            'action': 'PREPARE',
                            'dividend_date': div_date_str,
                            'days_to_dividend': days_to,
                            'priority': self.etf_info.get(etf, {}).get('priority', 99),
                            'reason': f'{days_to}天後除息，準備清倉' if days_to > 0 else '今日除息，立即清倉',
                            'confidence': 'high',
                            'urgency': 'high' if days_to <= 1 else 'medium'
                        })
                        
                except ValueError as e:
                    print(f"⚠️ 日期格式錯誤 {etf} {div_date_str}: {e}")
                    continue
                except Exception as e:
                    print(f"❌ 處理 {etf} {div_date_str} 時發生錯誤: {e}")
                    continue
        
        # 按優先級排序
        opportunities.sort(key=lambda x: (x.get('priority', 99), x.get('days_after', 99)))
        
        print(f"🎯 找到 {len(opportunities)} 個投資機會")
        return opportunities
    
    def get_next_dividend_dates(self, etf_code: str, limit: int = 3) -> List[str]:
        """獲取指定ETF的下幾個除息日期"""
        today = date.today()
        etf_dates = self.dividend_calendar.get(etf_code, [])
        
        future_dates = [
            date_str for date_str in etf_dates
            if datetime.strptime(date_str, '%Y-%m-%d').date() > today
        ]
        
        return future_dates[:limit]
    
    def is_in_buy_window(self, etf_code: str, target_date: date = None) -> Dict[str, Any]:
        """檢查是否在買進窗口期"""
        if target_date is None:
            target_date = date.today()
        
        etf_dates = self.dividend_calendar.get(etf_code, [])
        
        for div_date_str in etf_dates:
            try:
                div_date = datetime.strptime(div_date_str, '%Y-%m-%d').date()
                days_after = (target_date - div_date).days
                
                if 1 <= days_after <= 7:
                    return {
                        'in_buy_window': True,
                        'dividend_date': div_date_str,
                        'days_after': days_after,
                        'window_type': '1-7天買進窗口',
                        'confidence': 'high' if days_after <= 3 else 'medium'
                    }
                    
            except ValueError:
                continue
        
        return {
            'in_buy_window': False,
            'dividend_date': None,
            'days_after': None,
            'window_type': None,
            'confidence': 'low'
        }
    
    def refresh_schedule(self):
        """刷新除息日程（重新載入最新配置）"""
        print("🔄 刷新除息日程...")
        self._load_dividend_schedule()
    
    def get_schedule_info(self) -> Dict[str, Any]:
        """獲取日程資訊"""
        total_dates = sum(len(dates) for dates in self.dividend_calendar.values())
        
        return {
            'total_etfs': len(self.dividend_calendar),
            'total_dates': total_dates,
            'etf_schedule': {
                etf: len(dates) for etf, dates in self.dividend_calendar.items()
            }
        }

# 測試功能
if __name__ == "__main__":
    print("🧪 基礎除息分析器測試")
    print("="*50)
    
    try:
        analyzer = BasicDividendAnalyzer()
        
        # 顯示日程資訊
        info = analyzer.get_schedule_info()
        print(f"📊 日程資訊: {info['total_etfs']} 個ETF, {info['total_dates']} 個日期")
        
        # 尋找機會
        opportunities = analyzer.find_dividend_opportunities()
        print(f"🎯 找到 {len(opportunities)} 個機會")
        
        for opp in opportunities[:3]:  # 顯示前3個
            print(f"  📈 {opp['etf']}: {opp['action']} - {opp['reason']}")
        
        # 測試買進窗口檢查
        for etf in ['0056', '00878', '00919']:
            window_info = analyzer.is_in_buy_window(etf)
            if window_info['in_buy_window']:
                print(f"🟢 {etf}: 在買進窗口 ({window_info['window_type']})")
            else:
                print(f"⚪ {etf}: 不在買進窗口")
        
        print("✅ 測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()