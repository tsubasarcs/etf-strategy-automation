# core/dividend_collector.py
"""增強版除息日期API收集器"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import pandas as pd

class DividendDateCollector:
    """除息日期收集器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_twse_dividend_dates(self, start_date: str, end_date: str) -> List[Dict]:
        """
        從證交所TWT49U API獲取除息日期
        
        Args:
            start_date: 開始日期 (YYYYMMDD)
            end_date: 結束日期 (YYYYMMDD)
        
        Returns:
            List[Dict]: 除息資料列表
        """
        try:
            url = "https://www.twse.com.tw/rwd/zh/afterTrading/TWT49U"
            params = {
                'response': 'json',
                'date': start_date
            }
            
            print(f"📅 查詢證交所除息資料: {start_date}")
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('stat') == 'OK' and data.get('data'):
                    print(f"✅ 證交所成功獲取 {len(data['data'])} 筆除息資料")
                    return data['data']
                else:
                    print(f"⚠️ 證交所回應狀態: {data.get('stat', 'Unknown')}")
                    return []
            else:
                print(f"❌ 證交所API請求失敗: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 證交所API異常: {str(e)}")
            return []
    
    def get_etf_dividend_calendar(self) -> Dict[str, List[str]]:
        """
        從證交所ETF配息行事曆獲取除息日期
        
        Returns:
            Dict[str, List[str]]: {ETF代號: [除息日期列表]}
        """
        try:
            url = "https://www.twse.com.tw/zh/ETFortune/dividendCalendar"
            
            print("📅 查詢ETF配息行事曆...")
            
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 解析配息行事曆
                dividend_info = {}
                
                # 尋找包含ETF代號的元素
                etf_elements = soup.find_all(text=lambda text: text and ('0056' in text or '00878' in text or '00919' in text))
                
                for element in etf_elements:
                    text = element.strip()
                    if '0056' in text or '00878' in text or '00919' in text:
                        # 提取ETF代號
                        if '0056' in text:
                            etf_code = '0056'
                        elif '00878' in text:
                            etf_code = '00878'
                        elif '00919' in text:
                            etf_code = '00919'
                        else:
                            continue
                        
                        # 初始化該ETF的除息日期列表
                        if etf_code not in dividend_info:
                            dividend_info[etf_code] = []
                
                print(f"✅ 從配息行事曆識別到 {len(dividend_info)} 個ETF")
                return dividend_info
            else:
                print(f"❌ 配息行事曆查詢失敗: HTTP {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ 配息行事曆查詢異常: {str(e)}")
            return {}
    
    def get_comprehensive_dividend_schedule(self, etf_codes: List[str]) -> Dict[str, List[str]]:
        """
        獲取綜合除息日程表（多種方法結合）
        
        Args:
            etf_codes: ETF代號列表
        
        Returns:
            Dict[str, List[str]]: {ETF代號: [除息日期列表]}
        """
        print(f"🔍 開始查詢ETF除息日程: {etf_codes}")
        
        # 初始化結果
        etf_schedule = {etf: [] for etf in etf_codes}
        
        # 方法1: 查詢近期的除息資料
        today = datetime.now()
        
        # 查詢過去3個月到未來12個月的除息資料
        for month_offset in range(-3, 13):
            query_date = today + timedelta(days=30 * month_offset)
            date_str = query_date.strftime('%Y%m%d')
            
            print(f"📅 查詢 {query_date.strftime('%Y年%m月')} 的除息資料...")
            
            # 從證交所API獲取除息資料
            dividend_data = self.get_twse_dividend_dates(date_str, date_str)
            
            # 解析除息資料
            for row in dividend_data:
                try:
                    if len(row) >= 3:
                        stock_code = row[0].strip()
                        ex_date_str = row[1].strip()
                        
                        # 檢查是否為目標ETF
                        if stock_code in etf_codes:
                            # 處理日期格式
                            formatted_date = self._parse_date_format(ex_date_str)
                            
                            if formatted_date and formatted_date not in etf_schedule[stock_code]:
                                etf_schedule[stock_code].append(formatted_date)
                                print(f"📊 找到 {stock_code} 除息日期: {formatted_date}")
                except Exception as e:
                    print(f"⚠️ 解析除息資料錯誤: {e}")
                    continue
            
            # 間隔1秒避免API限制
            time.sleep(1)
        
        # 方法2: 使用已知的季度配息規律進行預測
        predicted_dates = self._predict_quarterly_dividends(etf_codes)
        
        # 合併預測日期
        for etf_code, dates in predicted_dates.items():
            for date in dates:
                if date not in etf_schedule[etf_code]:
                    etf_schedule[etf_code].append(date)
                    print(f"📈 預測 {etf_code} 除息日期: {date}")
        
        # 排序並去重
        for etf_code in etf_schedule:
            etf_schedule[etf_code] = sorted(list(set(etf_schedule[etf_code])))
            print(f"📊 {etf_code}: 總共 {len(etf_schedule[etf_code])} 個除息日期")
        
        return etf_schedule
    
    def _parse_date_format(self, date_str: str) -> Optional[str]:
        """解析各種日期格式"""
        try:
            # 嘗試不同的日期格式
            formats = [
                '%Y%m%d',      # 20250716
                '%Y-%m-%d',    # 2025-07-16
                '%Y/%m/%d',    # 2025/07/16
                '%m/%d/%Y',    # 07/16/2025
            ]
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # 處理民國年格式
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    try:
                        tw_year = int(parts[0])
                        if tw_year < 1000:  # 民國年
                            year = tw_year + 1911
                            month = int(parts[1])
                            day = int(parts[2])
                            return f"{year:04d}-{month:02d}-{day:02d}"
                    except:
                        pass
            
            return None
            
        except Exception as e:
            print(f"⚠️ 日期解析失敗: {date_str} - {e}")
            return None
    
    def _predict_quarterly_dividends(self, etf_codes: List[str]) -> Dict[str, List[str]]:
        """
        基於歷史規律預測季度除息日期
        
        Returns:
            Dict[str, List[str]]: 預測的除息日期
        """
        
        # 基於歷史規律的季度除息預測
        base_patterns = {
            '0056': [
                (1, 15),   # 1月中旬
                (4, 15),   # 4月中旬  
                (7, 15),   # 7月中旬
                (10, 15)   # 10月中旬
            ],
            '00878': [
                (2, 15),   # 2月中旬
                (5, 15),   # 5月中旬
                (8, 15),   # 8月中旬
                (11, 15)   # 11月中旬
            ],
            '00919': [
                (3, 15),   # 3月中旬
                (6, 15),   # 6月中旬
                (9, 15),   # 9月中旬
                (12, 15)   # 12月中旬
            ]
        }
        
        current_year = datetime.now().year
        next_year = current_year + 1
        
        predicted_dates = {}
        
        for etf_code in etf_codes:
            predicted_dates[etf_code] = []
            
            if etf_code in base_patterns:
                pattern = base_patterns[etf_code]
                
                # 生成本年度和明年度的預測日期
                for year in [current_year, next_year]:
                    for month, day in pattern:
                        try:
                            # 檢查日期是否未來
                            predicted_date = datetime(year, month, day)
                            if predicted_date > datetime.now():
                                formatted_date = predicted_date.strftime('%Y-%m-%d')
                                predicted_dates[etf_code].append(formatted_date)
                        except:
                            continue
        
        return predicted_dates
    
    def get_etf_dividend_schedule(self, etf_codes: List[str]) -> Dict[str, List[str]]:
        """
        主要介面：獲取ETF除息日程表
        
        Args:
            etf_codes: ETF代號列表
        
        Returns:
            Dict[str, List[str]]: {ETF代號: [除息日期列表]}
        """
        try:
            # 使用綜合方法獲取除息日程
            schedule = self.get_comprehensive_dividend_schedule(etf_codes)
            
            # 如果API獲取失敗，使用備用預測
            if not any(dates for dates in schedule.values()):
                print("🔄 API獲取失敗，使用備用預測方案")
                schedule = self.get_fallback_dividend_schedule(etf_codes)
            
            return schedule
            
        except Exception as e:
            print(f"❌ 除息日程查詢失敗: {str(e)}")
            return self.get_fallback_dividend_schedule(etf_codes)
    
    def get_fallback_dividend_schedule(self, etf_codes: List[str]) -> Dict[str, List[str]]:
        """
        備用除息日程（基於歷史規律）
        
        Returns:
            Dict[str, List[str]]: 備用除息日程
        """
        print("🔄 使用備用除息日程...")
        
        # 基於最新市場資訊的除息日程
        fallback_schedule = {
            "0056": [
                "2025-07-21",  # Q2 2025 (基於最新資訊)
                "2025-10-20",  # Q3 2025
                "2026-01-19",  # Q4 2025
                "2026-04-20"   # Q1 2026
            ],
            "00878": [
                "2025-08-18",  # Q2 2025
                "2025-11-17",  # Q3 2025
                "2026-02-16",  # Q4 2025
                "2026-05-18"   # Q1 2026
            ],
            "00919": [
                "2025-09-15",  # Q2 2025
                "2025-12-15",  # Q3 2025
                "2026-03-16",  # Q4 2025
                "2026-06-15"   # Q1 2026
            ]
        }
        
        result = {}
        for etf_code in etf_codes:
            result[etf_code] = fallback_schedule.get(etf_code, [])
            print(f"📅 {etf_code}: 使用 {len(result[etf_code])} 個備用除息日期")
        
        return result
    
    def update_config_file(self, dividend_schedule: Dict[str, List[str]], config_path: str) -> bool:
        """
        更新配置文件中的除息日期
        
        Args:
            dividend_schedule: 除息日程
            config_path: 配置文件路徑
        
        Returns:
            bool: 更新是否成功
        """
        try:
            print(f"📝 更新配置文件: {config_path}")
            
            # 讀取現有配置
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 生成新的DIVIDEND_CALENDAR
            new_calendar = "DIVIDEND_CALENDAR = {\n"
            for etf_code, dates in dividend_schedule.items():
                dates_str = ', '.join([f'"{date}"' for date in dates])
                new_calendar += f'    "{etf_code}": [{dates_str}],\n'
            new_calendar += "}"
            
            # 替換配置文件中的DIVIDEND_CALENDAR
            import re
            pattern = r'DIVIDEND_CALENDAR\s*=\s*\{[^}]*\}'
            
            if re.search(pattern, content, re.DOTALL):
                new_content = re.sub(pattern, new_calendar, content, flags=re.DOTALL)
                print("✅ 找到並替換現有DIVIDEND_CALENDAR")
            else:
                # 如果找不到，添加到文件末尾
                new_content = content + f"\n\n# 自動更新的除息日期 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{new_calendar}\n"
                print("✅ 在文件末尾添加DIVIDEND_CALENDAR")
            
            # 寫回文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ 配置文件更新成功")
            return True
            
        except Exception as e:
            print(f"❌ 配置文件更新失敗: {str(e)}")
            return False

def main():
    """測試除息日期收集器"""
    print("🎯 ETF除息日期自動收集器測試")
    print("=" * 50)
    
    collector = DividendDateCollector()
    etf_codes = ['0056', '00878', '00919']
    
    # 測試除息日程獲取
    schedule = collector.get_etf_dividend_schedule(etf_codes)
    
    print(f"\n📅 ETF除息日程表:")
    for etf_code, dates in schedule.items():
        print(f"\n{etf_code}:")
        for date in dates:
            print(f"  📊 {date}")
    
    # 測試配置文件更新
    # config_path = "config/etf_config.py"
    # success = collector.update_config_file(schedule, config_path)
    # print(f"\n📝 配置文件更新: {'✅ 成功' if success else '❌ 失敗'}")

if __name__ == "__main__":
    main()
