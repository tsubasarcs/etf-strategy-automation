import requests
import json
import os
from datetime import datetime, date

class DashboardGenerator:
    def __init__(self):
        self.firebase_url = os.getenv('FIREBASE_URL', 'https://your-project-default-rtdb.asia-southeast1.firebasedatabase.app')
        self.etf_info = {
            '0056': {'name': '元大高股息ETF', 'expected_return': 9.43, 'priority': 1},
            '00878': {'name': '國泰永續高股息ETF', 'expected_return': 5.56, 'priority': 3},
            '00919': {'name': '群益台灣精選高息ETF', 'expected_return': 6.26, 'priority': 2}
        }
    
    def get_from_firebase(self, path):
        """從Firebase讀取資料"""
        url = f"{self.firebase_url}/{path}.json"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Firebase讀取失敗: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Firebase讀取錯誤: {e}")
            return None
    
    def get_dashboard_data(self):
        """獲取儀表板所需資料"""
        print("📊 從Firebase獲取資料...")
        
        # 獲取最新狀態
        latest_status = self.get_from_firebase("latest_status")
        
        # 獲取最新價格
        latest_prices = {}
        for etf in self.etf_info.keys():
            price_data = self.get_from_firebase(f"latest_prices/{etf}")
            latest_prices[etf] = price_data
        
        # 獲取今日分析報告
        today_str = date.today().isoformat()
        today_analysis = self.get_from_firebase(f"daily_analysis/{today_str}")
        
        return {
            'latest_status': latest_status,
            'latest_prices': latest_prices,
            'today_analysis': today_analysis,
            'update_time': datetime.now().isoformat()
        }
    
    def generate_html(self, data):
        """生成HTML儀表板"""
        
        # 處理資料
        latest_status = data.get('latest_status', {})
        latest_prices = data.get('latest_prices', {})
        today_analysis = data.get('today_analysis', {})
        
        opportunities = latest_status.get('opportunities', [])
        last_update = latest_status.get('last_update', data['update_time'])
        
        # 格式化更新時間
        try:
            update_dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            formatted_time = update_dt.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_time = '資料載入中...'
        
        # 生成價格表格HTML
        price_table_html = self.generate_price_table(latest_prices)
        
        # 生成交易機會HTML
        opportunities_html = self.generate_opportunities_html(opportunities)
        
        # 生成策略統計HTML
        strategy_stats_html = self.generate_strategy_stats()
        
        # 主要HTML模板
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 ETF除息策略儀表板</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card-title {{
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: #2d3748;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .price-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f8fafc;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #3182ce;
        }}
        
        .etf-name {{
            font-weight: 600;
            color: #2d3748;
        }}
        
        .etf-code {{
            font-size: 0.9rem;
            color: #718096;
        }}
        
        .price {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #2b6cb0;
        }}
        
        .opportunity {{
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }}
        
        .opportunity.prepare {{
            background: linear-gradient(135deg, #ed8936, #dd6b20);
        }}
        
        .opportunity-header {{
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 5px;
        }}
        
        .opportunity-reason {{
            opacity: 0.9;
            font-size: 0.95rem;
        }}
        
        .no-opportunities {{
            text-align: center;
            padding: 30px;
            color: #718096;
            font-style: italic;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 10px;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }}
        
        .update-time {{
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 20px;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 ETF除息策略儀表板</h1>
            <p class="subtitle">智能化投資策略分析系統</p>
            <div class="update-time">
                📅 最後更新：{formatted_time}
            </div>
        </div>
        
        <div class="grid">
            <!-- 最新股價 -->
            <div class="card">
                <h2 class="card-title">📊 最新股價</h2>
                {price_table_html}
            </div>
            
            <!-- 交易機會 -->
            <div class="card">
                <h2 class="card-title">🎯 交易機會</h2>
                {opportunities_html}
            </div>
        </div>
        
        <!-- 策略統計 -->
        <div class="card">
            <h2 class="card-title">📈 策略統計</h2>
            {strategy_stats_html}
        </div>
        
        <div class="footer">
            <p>🤖 由GitHub Actions自動更新 | 📊 資料來源：台灣證券交易所</p>
            <p>🔥 資料儲存：Firebase | ⚡ 網頁託管：GitHub Pages</p>
        </div>
    </div>
    
    <script>
        // 自動刷新頁面 (每5分鐘)
        setTimeout(() => {{
            location.reload();
        }}, 300000);
        
        // 顯示載入完成
        console.log('🎯 ETF儀表板載入完成');
    </script>
</body>
</html>
        """
        
        return html_content
    
    def generate_price_table(self, latest_prices):
        """生成價格表格HTML"""
        if not latest_prices:
            return '<p class="no-opportunities">價格資料載入中...</p>'
        
        html = ""
        for etf, info in self.etf_info.items():
            price_data = latest_prices.get(etf, {})
            
            if price_data and price_data.get('latest_price'):
                price = price_data['latest_price']
                date_str = price_data.get('latest_date', '未知')
                
                html += f"""
                <div class="price-item">
                    <div>
                        <div class="etf-name">{info['name']}</div>
                        <div class="etf-code">{etf} | 預期報酬 {info['expected_return']:.1f}%</div>
                    </div>
                    <div class="price">${price:.2f}</div>
                </div>
                """
            else:
                html += f"""
                <div class="price-item">
                    <div>
                        <div class="etf-name">{info['name']}</div>
                        <div class="etf-code">{etf}</div>
                    </div>
                    <div class="price">載入中...</div>
                </div>
                """
        
        return html
    
    def generate_opportunities_html(self, opportunities):
        """生成交易機會HTML"""
        if not opportunities:
            return '<div class="no-opportunities">😴 目前沒有交易機會<br><small>系統持續監控中...</small></div>'
        
        html = ""
        for opp in opportunities:
            action_class = "prepare" if opp.get('action') == 'PREPARE' else ""
            emoji = "🟡" if opp.get('action') == 'PREPARE' else "🟢"
            
            etf_name = self.etf_info.get(opp.get('etf', ''), {}).get('name', opp.get('etf', ''))
            
            html += f"""
            <div class="opportunity {action_class}">
                <div class="opportunity-header">
                    {emoji} {opp.get('etf', '')} - {etf_name}
                </div>
                <div class="opportunity-reason">
                    {opp.get('reason', '分析中...')}
                </div>
            </div>
            """
        
        return html
    
    def generate_strategy_stats(self):
        """生成策略統計HTML"""
        return """
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">100%</div>
                <div class="stat-label">歷史成功率</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">7.08%</div>
                <div class="stat-label">平均報酬率</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">25-35%</div>
                <div class="stat-label">年化報酬率</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">1-7天</div>
                <div class="stat-label">最佳操作窗口</div>
            </div>
        </div>
        """
    
    def generate_dashboard(self):
        """生成完整儀表板"""
        print("🌐 開始生成儀表板...")
        
        # 確保輸出目錄存在
        os.makedirs('docs', exist_ok=True)
        
        # 獲取資料
        data = self.get_dashboard_data()
        
        # 生成HTML
        html_content = self.generate_html(data)
        
        # 保存到docs/index.html
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 生成簡單的404頁面
        self.generate_404_page()
        
        print("✅ 儀表板生成完成！")
        print("📁 檔案儲存至: docs/index.html")
        
        return True
    
    def generate_404_page(self):
        """生成404頁面"""
        html_404 = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>頁面未找到 - ETF策略儀表板</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            background: white; 
            padding: 40px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        }
        h1 { color: #333; }
        a { 
            color: #007bff; 
            text-decoration: none; 
            font-weight: bold; 
        }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 頁面未找到</h1>
        <p>您要找的頁面不存在。</p>
        <p><a href="/">🎯 返回ETF策略儀表板</a></p>
    </div>
</body>
</html>
        """
        
        with open('docs/404.html', 'w', encoding='utf-8') as f:
            f.write(html_404)

def main():
    generator = DashboardGenerator()
    generator.generate_dashboard()

if __name__ == "__main__":
    main()
