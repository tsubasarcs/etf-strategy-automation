# core/dividend_collector.py
"""除息日期API收集器 - 修復版本"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import re

class DividendDateCollector:
    """除息日期收集器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_twse_dividend_data(self, start_date: str, end_date: str) -> List[Dict]:
        """獲取證交所除息資料"""
        try:
            # 證交所除權除息API
            url = "https://www.twse.com.tw/rwd/zh/afterTrading/TWT49U"
            params = {
                'date': start_date.replace('-', ''),
                'stockNo': '',
                'response': 'json'
            }
            
            print(f"📊 查詢證交所除息資料: {start_date} ~ {end_date}")
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('stat') == 'OK' and data.get('data'):
                    print(f"✅ 證交所回應成功，找到 {len(data['data'])} 筆資料")
                    return data['data']
                else:
                    print(f"⚠️ 證交所回應：{data.get('stat', '無狀態')}")
                    return []
            else:
                print(f"❌ 證交所API失敗：HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 證交所API異常：{str(e)}")
            return []
    
    def get_tpex_dividend_data(self, start_date: str, end_date: str) -> List[Dict]:
        """獲取櫃買中心除息資料"""
        try:
            # 櫃買中心除權除息API
            url = "https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php"
            params = {
                'l': 'zh-tw',
                'd': start_date.replace('-', '/'),
                'ed': end_date.replace('-', '/'),
                'response': 'json'
            }
            
            print(f"📊 查詢櫃買中心除息資料: {start_date} ~ {end_date}")
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('aaData'):
                    print(f"✅ 櫃買中心回應成功，找到 {len(data['aaData'])} 筆資料")
                    return data['aaData']
                else:
                    print(f"⚠️ 櫃買中心無資料")
                    return []
            else:
                print(f"❌ 櫃買中心API失敗：HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 櫃買中心API異常：{str(e)}")
            return []
    
    def parse_dividend_data(self, twse_data: List, tpex_data: List, etf_codes: List[str]) -> Dict[str, List[str]]:
        """解析除息資料"""
        result = {}
        
        # 初始化結果
        for code in etf_codes:
            result[code] = []
        
        # 解析證交所資料
        for row in twse_data:
            if len(row) >= 3:  # 確保有足夠的欄位
                stock_code = row[0].strip()
                ex_date = row[1].strip()  # 除息日期
                
                # 檢查是否為我們關注的ETF
                if stock_code in etf_codes:
                    # 轉換日期格式 (民國年 -> 西元年)
                    try:
                        if '/' in ex_date:
                            parts = ex_date.split('/')
                            if len(parts) == 3:
                                year = int(parts[0]) + 1911  # 民國年轉西元年
                                formatted_date = f"{year}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                                result[stock_code].append(formatted_date)
                                print(f"📅 找到 {stock_code} 除息日期: {formatted_date}")
                    except:
                        pass
        
        # 解析櫃買中心資料
        for row in tpex_data:
            if len(row) >= 3:  # 確保有足夠的欄位
                stock_code = row[0].strip()
                ex_date = row[1].strip()  # 除息日期
                
                # 檢查是否為我們關注的ETF
                if stock_code in etf_codes:
                    # 轉換日期格式
                    try:
                        if '/' in ex_date:
                            parts = ex_date.split('/')
                            if len(parts) == 3:
                                year = int(parts[0]) + 1911  # 民國年轉西元年
                                formatted_date = f"{year}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                                result[stock_code].append(formatted_date)
                                print(f"📅 找到 {stock_code} 除息日期: {formatted_date}")
                    except:
                        pass
        
        return result
    
    def get_etf_dividend_schedule(self, etf_codes: List[str]) -> Dict[str, List[str]]:
        """獲取ETF除息日程表"""
        print(f"🔍 開始查詢ETF除息日程: {etf_codes}")
        
        # 設定查詢日期範圍（過去6個月到未來18個月）
        end_date = datetime.now() + timedelta(days=547)  # 18個月
        start_date = datetime.now() - timedelta(days=180)  # 6個月
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        print(f"📅 查詢日期範圍: {start_str} ~ {end_str}")
        
        # 由於API限制，分批查詢
        all_twse_data = []
        all_tpex_data = []
        
        # 分季度查詢
        current_date = start_date
        while current_date < end_date:
            quarter_end = min(current_date + timedelta(days=90), end_date)
            
            query_start = current_date.strftime("%Y-%m-%d")
            query_end = quarter_end.strftime("%Y-%m-%d")
            
            # 查詢證交所
            twse_data = self.get_twse_dividend_data(query_start, query_end)
            all_twse_data.extend(twse_data)
            
            time.sleep(1)  # 避免API限制
            
            # 查詢櫃買中心
            tpex_data = self.get_tpex_dividend_data(query_start, query_end)
            all_tpex_data.extend(tpex_data)
            
            current_date = quarter_end + timedelta(days=1)
            time.sleep(1)  # 避免API限制
        
        # 解析資料
        result = self.parse_dividend_data(all_twse_data, all_tpex_data, etf_codes)
        
        # 排序日期
        for code in result:
            result[code] = sorted(list(set(result[code])))  # 去重並排序
            print(f"📊 {code}: {len(result[code])} 個除息日期")
        
        return result
    
    def get_fallback_dividend_schedule(self, etf_codes: List[str]) -> Dict[str, List[str]]:
        """獲取備用的除息日程表（基於歷史規律預估）"""
        print("🔄 API失敗，使用備用除息日程表")
        
        # 基於歷史規律的預估日程
        fallback_schedule = {
            "0056": [
                "2025-07-21",  # Q2 (基於歷史規律)
                "2025-10-21",  # Q3 (預估)
                "2026-01-20",  # Q4 (預估)
                "2026-04-21"   # 2026Q1 (預估)
            ],
            "00878": [
                "2025-08-15",  # Q2 (預估)
                "2025-11-15",  # Q3 (預估)
                "2026-02-15",  # Q4 (預估)
                "2026-05-15"   # 2026Q1 (預估)
            ],
            "00919": [
                "2025-09-15",  # Q2 (預估)
                "2025-12-15",  # Q3 (預估)
                "2026-03-15",  # Q4 (預估)
                "2026-06-15"   # 2026Q1 (預估)
            ]
        }
        
        result = {}
        for code in etf_codes:
            if code in fallback_schedule:
                result[code] = fallback_schedule[code]
                print(f"📅 {code}: 使用備用日程 {len(result[code])} 個日期")
            else:
                result[code] = []
                print(f"⚠️ {code}: 無備用日程")
        
        return result
    
    def update_config_file(self, dividend_schedule: Dict[str, List[str]], config_path: str) -> bool:
        """更新配置文件"""
        try:
            print(f"📝 更新配置文件: {config_path}")
            
            # 讀取現有配置
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 構建新的DIVIDEND_CALENDAR字典
            new_calendar = "DIVIDEND_CALENDAR = {\n"
            for code, dates in dividend_schedule.items():
                dates_str = ', '.join([f'"{date}"' for date in dates])
                new_calendar += f'    "{code}": [{dates_str}],\n'
            new_calendar += "}"
            
            # 替換配置文件中的DIVIDEND_CALENDAR
            import re
            pattern = r'DIVIDEND_CALENDAR\s*=\s*\{[^}]*\}'
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                content = re.sub(pattern, new_calendar, content, flags=re.MULTILINE | re.DOTALL)
            else:
                # 如果找不到現有的DIVIDEND_CALENDAR，在文件末尾添加
                content += f"\n\n{new_calendar}\n"
            
            # 寫回文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ 配置文件更新完成")
            return True
            
        except Exception as e:
            print(f"❌ 更新配置文件失敗: {str(e)}")
            return False
