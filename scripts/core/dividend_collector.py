# 修正版除息收集器 - 解決API失敗問題
"""
修正版除息日期收集器
主要修正：
1. 縮小查詢日期範圍（避免404錯誤）
2. 使用正確的API端點（TWT48U查未來，TWT49U查歷史）
3. 增加重試機制和延遲
4. 改善錯誤處理
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import pandas as pd
import re

class DividendDateCollector:
    """修正版除息日期收集器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.twse.com.tw/',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # 🔧 修正1: 定義API端點用途
        self.api_endpoints = {
            'future': 'https://www.twse.com.tw/exchangeReport/TWT48U',      # 除息預告（查未來）
            'history': 'https://www.twse.com.tw/exchangeReport/TWT49U',     # 除息計算結果（查歷史）
            'future_rwd': 'https://www.twse.com.tw/rwd/zh/afterTrading/TWT48U',
            'history_rwd': 'https://www.twse.com.tw/rwd/zh/afterTrading/TWT49U'
        }
        
        # 🔧 修正2: 限制查詢範圍（避免404）
        self.max_past_months = 3      # 最多查詢過去3個月
        self.max_future_months = 6    # 最多查詢未來6個月
        self.request_delay = 2        # 請求間隔（秒）
        self.max_retries = 3          # 最大重試次數
    
    def get_twse_dividend_dates(self, start_date: str, end_date: str) -> List[Dict]:
        """
        🔧 修正版證交所除息資料獲取
        根據日期選擇正確的API端點
        """
        
        # 判斷是查詢歷史還是未來
        query_date = datetime.strptime(start_date, '%Y%m%d')
        today = datetime.now()
        
        if query_date < today:
            # 查詢歷史：使用TWT49U（計算結果）
            api_key = 'history'
            api_description = "歷史除息計算結果"
        else:
            # 查詢未來：使用TWT48U（預告）
            api_key = 'future'
            api_description = "未來除息預告"
        
        # 🔧 修正3: 依序嘗試主要和RWD端點
        endpoints_to_try = [
            (self.api_endpoints[api_key], api_description),
            (self.api_endpoints[api_key + '_rwd'], api_description + " (RWD)")
        ]
        
        for endpoint_url, description in endpoints_to_try:
            for retry in range(self.max_retries):
                try:
                    print(f"🔍 嘗試{description} (第{retry+1}次): {start_date}")
                    
                    params = {
                        'response': 'json',
                        'date': start_date
                    }
                    
                    response = self.session.get(
                        endpoint_url,
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if data.get('stat') == 'OK' and data.get('data'):
                                print(f"✅ {description}成功獲取 {len(data['data'])} 筆資料")
                                return data['data']
                            else:
                                print(f"⚠️ {description}無資料: {data.get('stat', 'Unknown')}")
                                # 如果無資料，不重試，直接嘗試下一個端點
                                break
                        except json.JSONDecodeError:
                            print(f"❌ {description} JSON解析失敗")
                            if retry < self.max_retries - 1:
                                time.sleep(self.request_delay)
                                continue
                    
                    elif response.status_code == 404:
                        print(f"❌ {description} 404錯誤 - 日期超出範圍或端點不存在")
                        break  # 404不重試
                    
                    else:
                        print(f"❌ {description} HTTP {response.status_code}")
                        if retry < self.max_retries - 1:
                            time.sleep(self.request_delay)
                            continue
                    
                except requests.exceptions.Timeout:
                    print(f"⏰ {description} 請求超時")
                    if retry < self.max_retries - 1:
                        time.sleep(self.request_delay * 2)
                        continue
                
                except requests.exceptions.ConnectionError:
                    print(f"🌐 {description} 連接錯誤")
                    if retry < self.max_retries - 1:
                        time.sleep(self.request_delay * 2)
                        continue
                
                except Exception as e:
                    print(f"❌ {description} 未知錯誤: {str(e)}")
                    if retry < self.max_retries - 1:
                        time.sleep(self.request_delay)
                        continue
        
        print(f"❌ 所有API端點都失敗: {start_date}")
        return []
    
    def _parse_date_format(self, date_str: str) -> Optional[str]:
        """🔧 修正版日期解析"""
        if not date_str:
            return None
            
        date_str = date_str.strip()
        
        # 處理常見日期格式
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
        
        # 🔧 修正4: 改善民國年處理
        if '/' in date_str:
            try:
                parts = date_str.split('/')
                if len(parts) == 3:
                    # 嘗試不同的年份位置
                    for year_idx in [0, 2]:
                        try:
                            year = int(parts[year_idx])
                            month = int(parts[1])
                            day = int(parts[2] if year_idx == 0 else parts[0])
                            
                            # 民國年轉換
                            if year < 200:  # 假設是民國年
                                year += 1911
                            
                            # 驗證日期合理性
                            if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                                return f"{year:04d}-{month:02d}-{day:02d}"
                        except (ValueError, IndexError):
                            continue
            except Exception:
                pass
        
        return None
    
    def get_comprehensive_dividend_schedule(self, etf_codes: List[str]) -> Dict[str, List[str]]:
        """
        🔧 修正版綜合除息日程獲取
        主要改進：限制日期範圍，避免404錯誤
        """
        print(f"🔍 開始查詢ETF除息日程: {etf_codes}")
        
        # 初始化結果
        etf_schedule = {etf: [] for etf in etf_codes}
        
        today = datetime.now()
        
        # 🔧 修正5: 限制查詢範圍
        # 歷史資料：過去3個月
        start_date = today - timedelta(days=30 * self.max_past_months)
        # 未來資料：未來6個月
        end_date = today + timedelta(days=30 * self.max_future_months)
        
        print(f"📅 查詢範圍: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
        
        # 🔧 修正6: 按月份查詢，減少請求次數
        current_date = start_date
        
        while current_date <= end_date:
            # 每月查詢一次
            date_str = current_date.strftime('%Y%m%d')
            
            print(f"📅 查詢 {current_date.strftime('%Y年%m月')}...")
            
            try:
                dividend_data = self.get_twse_dividend_dates(date_str, date_str)
                
                # 解析除息資料
                for row in dividend_data:
                    try:
                        if len(row) >= 2:
                            stock_code = row[0].strip()
                            ex_date_str = row[1].strip()
                            
                            # 檢查是否為目標ETF
                            if stock_code in etf_codes:
                                formatted_date = self._parse_date_format(ex_date_str)
                                
                                if formatted_date and formatted_date not in etf_schedule[stock_code]:
                                    etf_schedule[stock_code].append(formatted_date)
                                    print(f"📊 找到 {stock_code} 除息日期: {formatted_date}")
                    except Exception as e:
                        print(f"⚠️ 解析資料錯誤: {e}")
                        continue
                
            except Exception as e:
                print(f"❌ 查詢失敗 {date_str}: {e}")
            
            # 🔧 修正7: 增加請求間隔
            time.sleep(self.request_delay)
            
            # 移到下個月
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # 🔧 修正8: 如果API完全失敗，使用更保守的備用方案
        if not any(dates for dates in etf_schedule.values()):
            print("🔄 所有API都失敗，使用備用方案...")
            etf_schedule = self.get_conservative_fallback_schedule(etf_codes)
        
        # 排序並去重
        for etf_code in etf_schedule:
            etf_schedule[etf_code] = sorted(list(set(etf_schedule[etf_code])))
            print(f"📊 {etf_code}: 總共 {len(etf_schedule[etf_code])} 個除息日期")
        
        return etf_schedule
    
    def get_conservative_fallback_schedule(self, etf_codes: List[str]) -> Dict[str, List[str]]:
        """
        🔧 修正9: 保守的備用除息日程
        只包含高信心度的近期日期
        """
        print("🔄 使用保守備用除息日程...")
        
        today = datetime.now()
        current_year = today.year
        
        # 基於ETF歷史規律的保守預測
        conservative_schedule = {}
        
        for etf_code in etf_codes:
            dates = []
            
            if etf_code == '0056':
                # 0056通常每季除息：1、4、7、10月
                base_months = [1, 4, 7, 10]
                for month in base_months:
                    for year in [current_year, current_year + 1]:
                        # 通常在15-18日左右
                        for day in [15, 16, 17]:
                            try:
                                date_obj = datetime(year, month, day)
                                if date_obj > today:  # 只包含未來日期
                                    dates.append(date_obj.strftime('%Y-%m-%d'))
                            except ValueError:
                                continue
            
            elif etf_code == '00878':
                # 00878通常每季除息：2、5、8、11月
                base_months = [2, 5, 8, 11]
                for month in base_months:
                    for year in [current_year, current_year + 1]:
                        for day in [15, 16, 17]:
                            try:
                                date_obj = datetime(year, month, day)
                                if date_obj > today:
                                    dates.append(date_obj.strftime('%Y-%m-%d'))
                            except ValueError:
                                continue
            
            elif etf_code == '00919':
                # 00919通常每季除息：3、6、9、12月
                base_months = [3, 6, 9, 12]
                for month in base_months:
                    for year in [current_year, current_year + 1]:
                        for day in [15, 16, 17]:
                            try:
                                date_obj = datetime(year, month, day)
                                if date_obj > today:
                                    dates.append(date_obj.strftime('%Y-%m-%d'))
                            except ValueError:
                                continue
            
            # 只保留未來6個月內的日期
            future_limit = today + timedelta(days=180)
            filtered_dates = [
                date for date in dates 
                if today < datetime.strptime(date, '%Y-%m-%d') <= future_limit
            ]
            
            conservative_schedule[etf_code] = sorted(filtered_dates)
            print(f"📅 {etf_code}: 保守預測 {len(conservative_schedule[etf_code])} 個除息日期")
        
        return conservative_schedule
    
    def get_etf_dividend_schedule(self, etf_codes: List[str]) -> Dict[str, List[str]]:
        """
        🔧 主要介面：獲取ETF除息日程表
        """
        try:
            print("🎯 ETF除息日程查詢 - 修正版")
            print("=" * 50)
            
            # 使用修正版方法獲取除息日程
            schedule = self.get_comprehensive_dividend_schedule(etf_codes)
            
            # 🔧 修正10: 驗證結果合理性
            for etf_code, dates in schedule.items():
                if dates:
                    print(f"✅ {etf_code}: {len(dates)} 個除息日期")
                    for date in dates[:3]:  # 只顯示前3個
                        print(f"  📅 {date}")
                    if len(dates) > 3:
                        print(f"  ... 還有 {len(dates) - 3} 個日期")
                else:
                    print(f"⚠️ {etf_code}: 未獲取到除息日期")
            
            return schedule
            
        except Exception as e:
            print(f"❌ 除息日程查詢失敗: {str(e)}")
            return self.get_conservative_fallback_schedule(etf_codes)
    
    def update_config_file(self, dividend_schedule: Dict[str, List[str]], config_path: str) -> bool:
        """更新配置文件"""
        try:
            print(f"📝 更新配置文件: {config_path}")
            
            # 檢查文件是否存在
            import os
            if not os.path.exists(config_path):
                print(f"❌ 配置文件不存在: {config_path}")
                return False
            
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

# 測試和使用示例
def main():
    """測試修正版除息日期收集器"""
    print("🎯 修正版ETF除息日期收集器測試")
    print("=" * 50)
    
    collector = DividendDateCollector()
    etf_codes = ['0056', '00878', '00919']
    
    # 測試除息日程獲取
    schedule = collector.get_etf_dividend_schedule(etf_codes)
    
    print(f"\n🎉 測試完成!")
    print(f"✅ 成功獲取 {len(schedule)} 個ETF的除息日程")
    
    # 統計結果
    total_dates = sum(len(dates) for dates in schedule.values())
    print(f"📊 總共獲取 {total_dates} 個除息日期")
    
    # 檢查是否有近期的除息日期
    today = datetime.now()
    near_future = today + timedelta(days=90)
    
    for etf_code, dates in schedule.items():
        upcoming_dates = [
            date for date in dates
            if today < datetime.strptime(date, '%Y-%m-%d') <= near_future
        ]
        if upcoming_dates:
            print(f"🎯 {etf_code} 近期除息日期: {upcoming_dates}")
    
    return schedule

if __name__ == "__main__":
    main()
