# core/dividend_collector.py
"""除息日期API收集器"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DividendDateCollector:
    """除息日期收集器"""
    
    def __init__(self):
        self.base_url_twse = "https://www.twse.com.tw/exchangeReport/TWT49U"
        self.base_url_tpex = "https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php"
    
    def get_twse_dividend_dates(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        從證交所API獲取除權除息日期
        
        Args:
            start_date: 開始日期 (YYYYMMDD)
            end_date: 結束日期 (YYYYMMDD)
        
        Returns:
            DataFrame: 除權除息資料
        """
        try:
            url = f"{self.base_url_twse}?response=html&strDate={start_date}&endDate={end_date}"
            
            print(f"📅 獲取證交所除息資料: {start_date} ~ {end_date}")
            
            # 使用pandas直接讀取HTML表格
            dividend_tables = pd.read_html(url)
            
            if dividend_tables and len(dividend_tables) > 0:
                df = dividend_tables[0]
                print(f"✅ 成功獲取 {len(df)} 筆除息資料")
                return df
            else:
                print("⚠️ 未找到除息資料")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ 獲取證交所除息資料失敗: {e}")
            return pd.DataFrame()
    
    def get_tpex_dividend_dates(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        從櫃買中心API獲取除權除息日期
        
        Args:
            start_date: 開始日期 (YYYYMMDD)
            end_date: 結束日期 (YYYYMMDD)
        
        Returns:
            DataFrame: 除權除息資料
        """
        try:
            # 轉換日期格式為民國年 (YYY/MM/DD)
            start_tw = f"{int(start_date[:4])-1911}/{start_date[4:6]}/{start_date[6:]}"
            end_tw = f"{int(end_date[:4])-1911}/{end_date[4:6]}/{end_date[6:]}"
            
            url = f"{self.base_url_tpex}?l=zh-tw&d={start_tw}&ed={end_tw}"
            
            print(f"📅 獲取櫃買中心除息資料: {start_tw} ~ {end_tw}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'aaData' in data and data['aaData']:
                    columns = [
                        "除權息日期", "代號", "名稱", "除權息前收盤價", "除權息參考價",
                        "權值", "息值", "權值+息值", "權/息", "漲停價", "跌停價",
                        "開始交易基準價", "減除股利參考價", "現金股利", "每仟股無償配股",
                        "現金增資股數", "現金增資認購價", "公開承銷股數", "員工認購股數",
                        "原股東認購股數", "按持股比例仟股認購"
                    ]
                    
                    df = pd.DataFrame(data['aaData'], columns=columns)
                    print(f"✅ 成功獲取 {len(df)} 筆櫃買除息資料")
                    return df
                else:
                    print("⚠️ 櫃買中心未找到除息資料")
                    return pd.DataFrame()
            else:
                print(f"❌ 櫃買中心API請求失敗: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ 獲取櫃買中心除息資料失敗: {e}")
            return pd.DataFrame()
    
    def get_etf_dividend_schedule(self, etf_list: List[str], months_ahead: int = 6) -> Dict[str, List[str]]:
        """
        獲取ETF的除息日程表
        
        Args:
            etf_list: ETF代號列表
            months_ahead: 向前查詢幾個月
        
        Returns:
            Dict: {ETF代號: [除息日期列表]}
        """
        
        # 設定查詢日期範圍
        today = datetime.now()
        start_date = (today - timedelta(days=30)).strftime('%Y%m%d')  # 往前一個月
        end_date = (today + timedelta(days=30*months_ahead)).strftime('%Y%m%d')  # 往後指定月份
        
        print(f"🔍 查詢ETF除息日期: {start_date} ~ {end_date}")
        
        # 合併證交所和櫃買中心的資料
        all_dividend_data = pd.DataFrame()
        
        # 獲取證交所資料
        twse_data = self.get_twse_dividend_dates(start_date, end_date)
        if not twse_data.empty:
            all_dividend_data = pd.concat([all_dividend_data, twse_data], ignore_index=True)
        
        # 小延遲避免請求過快
        time.sleep(1)
        
        # 獲取櫃買中心資料
        tpex_data = self.get_tpex_dividend_dates(start_date, end_date)
        if not tpex_data.empty:
            all_dividend_data = pd.concat([all_dividend_data, tpex_data], ignore_index=True)
        
        # 解析ETF除息日期
        etf_schedule = {}
        
        for etf_code in etf_list:
            etf_schedule[etf_code] = []
            
            if not all_dividend_data.empty:
                # 尋找該ETF的除息記錄
                etf_data = all_dividend_data[all_dividend_data['代號'] == etf_code]
                
                for _, row in etf_data.iterrows():
                    try:
                        # 解析日期格式
                        date_str = str(row['除權息日期'])
                        
                        # 處理不同的日期格式
                        if '/' in date_str:
                            # 民國年格式 (YYY/MM/DD)
                            parts = date_str.split('/')
                            if len(parts) == 3:
                                year = int(parts[0]) + 1911  # 轉換為西元年
                                month = int(parts[1])
                                day = int(parts[2])
                                formatted_date = f"{year:04d}-{month:02d}-{day:02d}"
                        else:
                            # 其他格式處理
                            formatted_date = self._parse_date_string(date_str)
                        
                        if formatted_date and formatted_date not in etf_schedule[etf_code]:
                            etf_schedule[etf_code].append(formatted_date)
                            
                    except Exception as e:
                        print(f"⚠️ 解析 {etf_code} 日期失敗: {e}")
                        continue
            
            # 排序日期
            etf_schedule[etf_code].sort()
            print(f"📅 {etf_code}: {len(etf_schedule[etf_code])} 個除息日期")
        
        return etf_schedule
    
    def _parse_date_string(self, date_str: str) -> Optional[str]:
        """解析各種日期格式"""
        try:
            # 嘗試不同的日期格式
            formats = ['%Y%m%d', '%Y-%m-%d', '%Y/%m/%d']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return None
        except:
            return None
    
    def update_config_file(self, etf_schedule: Dict[str, List[str]], config_file_path: str):
        """
        更新配置文件中的除息日期
        
        Args:
            etf_schedule: ETF除息日程
            config_file_path: 配置文件路徑
        """
        try:
            print("📝 更新配置文件...")
            
            # 讀取現有配置文件
            with open(config_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 生成新的DIVIDEND_CALENDAR
            new_calendar = "DIVIDEND_CALENDAR = {\n"
            for etf_code, dates in etf_schedule.items():
                new_calendar += f'    "{etf_code}": {dates},\n'
            new_calendar += "}"
            
            # 替換舊的DIVIDEND_CALENDAR
            import re
            pattern = r'DIVIDEND_CALENDAR\s*=\s*\{[^}]*\}'
            
            if re.search(pattern, content, re.DOTALL):
                new_content = re.sub(pattern, new_calendar, content, flags=re.DOTALL)
            else:
                # 如果找不到，添加到文件末尾
                new_content = content + f"\n\n# 自動更新的除息日期\n{new_calendar}\n"
            
            # 寫入文件
            with open(config_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ 配置文件更新完成")
            
        except Exception as e:
            print(f"❌ 更新配置文件失敗: {e}")

def main():
    """主函數 - 測試除息日期收集"""
    print("🎯 ETF除息日期自動收集器")
    print("=" * 40)
    
    # 初始化收集器
    collector = DividendDateCollector()
    
    # 要查詢的ETF列表
    etf_list = ['0056', '00878', '00919']
    
    # 獲取除息日程
    schedule = collector.get_etf_dividend_schedule(etf_list, months_ahead=12)
    
    # 顯示結果
    print("\n📅 ETF除息日程表:")
    for etf_code, dates in schedule.items():
        print(f"\n{etf_code}:")
        for date in dates:
            print(f"  - {date}")
    
    # 可選：更新配置文件
    # config_path = "config/etf_config.py"
    # collector.update_config_file(schedule, config_path)

if __name__ == "__main__":
    main()
