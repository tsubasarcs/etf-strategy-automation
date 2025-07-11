import requests
import pandas as pd
import json
from datetime import datetime, date, timedelta
import time
import os

class ETFAnalyzer:
    def __init__(self):
        self.etfs = ['0056', '00878', '00919']
        self.base_url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        
        # 配息行事曆
        self.dividend_calendar = {
            "0056": ["2025-07-15", "2025-10-15", "2026-01-15", "2026-04-15"],
            "00878": ["2025-08-16", "2025-11-21", "2026-02-20", "2026-05-19"], 
            "00919": ["2025-09-16", "2025-12-16", "2026-03-17", "2026-06-17"]
        }
        
        # 確保資料夾存在
        os.makedirs('data', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
    
    def convert_tw_date(self, date_str):
        """轉換台灣民國年為西元年"""
        try:
            parts = date_str.split('/')
            tw_year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            return f"{tw_year + 1911}-{month:02d}-{day:02d}"
        except:
            return None
    
    def get_etf_data(self, etf_code, year_month):
        """取得ETF月份資料"""
        url = f"{self.base_url}?response=json&date={year_month}01&stockNo={etf_code}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
                
            data = response.json()
            if data.get('stat') != 'OK' or not data.get('data'):
                return None
                
            df = pd.DataFrame(data['data'], columns=data['fields'])
            df['西元日期'] = df['日期'].apply(self.convert_tw_date)
            df['西元日期'] = pd.to_datetime(df['西元日期'])
            
            # 數值轉換
            numeric_cols = ['成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].str.replace(',', '').astype(float)
            
            return df
            
        except Exception as e:
            print(f"取得 {etf_code} 資料失敗: {e}")
            return None
    
    def update_etf_data(self, etf_code):
        """更新ETF歷史資料"""
        print(f"更新 {etf_code} 資料...")
        
        # 取得最近3個月的資料
        all_data = []
        current_date = datetime.now()
        
        for i in range(3):
            year_month = (current_date - timedelta(days=30*i)).strftime('%Y%m')
            monthly_data = self.get_etf_data(etf_code, year_month)
            
            if monthly_data is not None:
                all_data.append(monthly_data)
            
            time.sleep(1)  # 避免請求過快
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df = combined_df.drop_duplicates().sort_values('西元日期').reset_index(drop=True)
            
            # 保存資料
            filename = f'data/{etf_code}_data.csv'
            combined_df.to_csv(filename, index=False, encoding='utf-8')
            print(f"✅ {etf_code} 資料更新完成: {len(combined_df)} 筆記錄")
            return True
        else:
            print(f"❌ {etf_code} 無法取得資料")
            return False
    
    def analyze_dividend_opportunities(self):
        """分析配息機會"""
        today = date.today()
        opportunities = []
        
        for etf in self.etfs:
            dividend_dates = self.dividend_calendar.get(etf, [])
            
            for div_date_str in dividend_dates:
                try:
                    div_date = datetime.strptime(div_date_str, '%Y-%m-%d').date()
                    days_after_dividend = (today - div_date).days
                    
                    # 檢查買進機會（除息後1-7天）
                    if 1 <= days_after_dividend <= 7:
                        opportunities.append({
                            'etf': etf,
                            'action': 'BUY',
                            'dividend_date': div_date_str,
                            'days_after': days_after_dividend,
                            'priority': self.get_etf_priority(etf),
                            'reason': f'除息後第{days_after_dividend}天，建議買進'
                        })
                    
                    # 檢查即將配息（提前3天通知）
                    days_to_dividend = (div_date - today).days
                    if 0 <= days_to_dividend <= 3:
                        opportunities.append({
                            'etf': etf,
                            'action': 'PREPARE',
                            'dividend_date': div_date_str,
                            'days_to_dividend': days_to_dividend,
                            'priority': self.get_etf_priority(etf),
                            'reason': f'{days_to_dividend}天後除息，準備清倉'
                        })
                        
                except ValueError:
                    continue
        
        return sorted(opportunities, key=lambda x: x['priority'])
    
    def get_etf_priority(self, etf):
        """ETF優先級（基於策略分析結果）"""
        priority_map = {
            '0056': 1,   # 最高優先級：平均報酬9.43%
            '00919': 2,  # 中優先級：平均報酬6.26%
            '00878': 3   # 低優先級：平均報酬5.56%
        }
        return priority_map.get(etf, 999)
    
    def get_current_price(self, etf_code):
        """取得最新股價"""
        try:
            filename = f'data/{etf_code}_data.csv'
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                if not df.empty:
                    latest_price = df.iloc[-1]['收盤價']
                    latest_date = df.iloc[-1]['西元日期']
                    return latest_price, latest_date
        except:
            pass
        return None, None
    
    def generate_analysis_report(self, opportunities):
        """生成分析報告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_date': date.today().isoformat(),
            'opportunities': opportunities,
            'market_status': {}
        }
        
        # 取得各ETF最新價格
        for etf in self.etfs:
            price, price_date = self.get_current_price(etf)
            report['market_status'][etf] = {
                'latest_price': price,
                'price_date': price_date,
                'data_available': price is not None
            }
        
        # 保存報告
        filename = f'reports/analysis_{date.today().isoformat()}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def print_analysis_summary(self, report):
        """印出分析摘要"""
        print("\n" + "="*50)
        print("🎯 ETF除息策略分析報告")
        print("="*50)
        print(f"📅 分析日期: {report['analysis_date']}")
        print(f"⏰ 分析時間: {datetime.fromisoformat(report['timestamp']).strftime('%H:%M:%S')}")
        
        # 市場狀況
        print("\n📊 市場狀況:")
        for etf, status in report['market_status'].items():
            if status['data_available']:
                print(f"  {etf}: ${status['latest_price']:.2f} ({status['price_date']})")
            else:
                print(f"  {etf}: 資料更新中...")
        
        # 交易機會
        opportunities = report['opportunities']
        if opportunities:
            print(f"\n🎯 交易機會 ({len(opportunities)}個):")
            for opp in opportunities:
                emoji = "🟢" if opp['action'] == 'BUY' else "🟡"
                print(f"  {emoji} {opp['etf']}: {opp['action']} - {opp['reason']}")
        else:
            print("\n😴 目前沒有交易機會")
        
        print("\n" + "="*50)

def main():
    analyzer = ETFAnalyzer()
    
    print("🚀 開始ETF自動分析...")
    
    # 1. 更新所有ETF資料
    print("\n📊 更新ETF資料...")
    update_success = {}
    for etf in analyzer.etfs:
        update_success[etf] = analyzer.update_etf_data(etf)
    
    # 2. 分析交易機會
    print("\n🔍 分析交易機會...")
    opportunities = analyzer.analyze_dividend_opportunities()
    
    # 3. 生成報告
    print("\n📋 生成分析報告...")
    report = analyzer.generate_analysis_report(opportunities)
    
    # 4. 顯示結果
    analyzer.print_analysis_summary(report)
    
    # 5. 輸出給GitHub Actions
    print(f"\n📈 GitHub Actions 摘要:")
    print(f"資料更新: {sum(update_success.values())}/{len(update_success)} 成功")
    print(f"交易機會: {len(opportunities)} 個")
    
    return report

if __name__ == "__main__":
    main()
