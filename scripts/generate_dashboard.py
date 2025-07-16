# generate_dashboard.py
"""ETF策略儀表板生成器 - 模組化版本"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# 確保可以導入模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.firebase_client import FirebaseClient
from config.etf_config import ETF_INFO, ETF_LIST

class ModularDashboard:
    """模組化儀表板生成器"""
    
    def __init__(self):
        self.firebase_client = FirebaseClient()
        self.etf_info = ETF_INFO
        
    def generate_dashboard(self) -> str:
        """生成儀表板HTML"""
        
        # 獲取最新分析結果
        latest_status = self.firebase_client.get("latest_modular_status")
        
        if not latest_status:
            return self._generate_no_data_dashboard()
        
        # 生成完整儀表板
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ETF模組化策略儀表板</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 30px; 
            border-radius: 12px; 
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 5px 0; opacity: 0.9; }}
        
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px;
        }}
        .stat-card {{ 
            background: white; 
            padding: 25px; 
            border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .stat-card:hover {{ transform: translateY(-2px); }}
        .stat-card h3 {{ margin: 0 0 15px 0; color: #333; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        
        .opportunities {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .opportunity {{ 
            background: #f8f9fa; 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 8px; 
            border-left: 5px solid #ddd;
        }}
        .opportunity.buy {{ border-left-color: #28a745; }}
        .opportunity.sell {{ border-left-color: #dc3545; }}
        .opportunity.hold {{ border-left-color: #ffc107; }}
        .opportunity.strong-buy {{ border-left-color: #155724; background: #d4edda; }}
        
        .opportunity h3 {{ margin: 0 0 10px 0; color: #333; }}
        .opportunity-meta {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 10px; 
            margin-top: 15px;
        }}
        .meta-item {{ 
            background: white; 
            padding: 10px; 
            border-radius: 5px; 
            border: 1px solid #eee;
        }}
        .meta-label {{ font-weight: bold; color: #666; font-size: 0.9em; }}
        .meta-value {{ color: #333; }}
        
        .etf-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 15px; 
        }}
        .etf-card {{ 
            background: white; 
            padding: 15px; 
            border-radius: 8px; 
            border: 1px solid #eee;
        }}
        .etf-code {{ font-weight: bold; color: #667eea; font-size: 1.1em; }}
        .etf-name {{ color: #666; font-size: 0.9em; margin: 5px 0; }}
        .etf-return {{ color: #28a745; font-weight: bold; }}
        
        .footer {{ 
            text-align: center; 
            margin-top: 30px; 
            padding: 20px; 
            color: #666; 
            font-size: 0.9em;
        }}
        
        .status-badge {{ 
            display: inline-block; 
            padding: 4px 8px; 
            border-radius: 12px; 
            font-size: 0.8em; 
            font-weight: bold;
        }}
        .status-high {{ background: #d4edda; color: #155724; }}
        .status-medium {{ background: #fff3cd; color: #856404; }}
        .status-low {{ background: #f8d7da; color: #721c24; }}
        
        @media (max-width: 768px) {{
            .stats {{ grid-template-columns: 1fr; }}
            .opportunity-meta {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 ETF模組化策略儀表板</h1>
            <p>📅 最後更新: {datetime.fromisoformat(latest_status['last_update']).strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🔧 系統版本: {latest_status.get('system_version', 'Unknown')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>📊 投資機會總覽</h3>
                <div class="stat-number">{latest_status.get('summary', {}).get('total_opportunities', 0)}</div>
                <p>總機會數</p>
            </div>
            
            <div class="stat-card">
                <h3>🟢 買進信號</h3>
                <div class="stat-number">{latest_status.get('summary', {}).get('buy_signals', 0)}</div>
                <p>建議買進</p>
            </div>
            
            <div class="stat-card">
                <h3>🟠 賣出信號</h3>
                <div class="stat-number">{latest_status.get('summary', {}).get('sell_signals', 0)}</div>
                <p>建議賣出</p>
            </div>
            
            <div class="stat-card">
                <h3>⭐ 高信心機會</h3>
                <div class="stat-number">{latest_status.get('summary', {}).get('high_confidence', 0)}</div>
                <p>高信心度</p>
            </div>
        </div>
        
        <div class="stat-card">
            <h3>🎯 ETF基本資訊</h3>
            <div class="etf-grid">
                {self._generate_etf_info_html()}
            </div>
        </div>
        
        <div class="opportunities">
            <h2>🎪 投資機會分析</h2>
            {self._generate_opportunities_html(latest_status.get('opportunities', []))}
        </div>
        
        <div class="footer">
            <p>🤖 自動生成於: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>📊 數據來源: Firebase即時資料庫</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def _generate_etf_info_html(self) -> str:
        """生成ETF資訊HTML"""
        html = ""
        for etf_code, info in self.etf_info.items():
            html += f"""
            <div class="etf-card">
                <div class="etf-code">{etf_code}</div>
                <div class="etf-name">{info['name']}</div>
                <div class="etf-return">預期報酬: {info['expected_return']:.2f}%</div>
                <div style="margin-top: 10px;">
                    <span class="meta-label">優先級:</span> {info['priority']} | 
                    <span class="meta-label">Beta:</span> {info['beta']}
                </div>
            </div>
            """
        return html
    
    def _generate_opportunities_html(self, opportunities: List[Dict]) -> str:
        """生成投資機會HTML"""
        if not opportunities:
            return """
            <div style="text-align: center; padding: 40px; color: #666;">
                <h3>😴 目前沒有投資機會</h3>
                <p>系統正在監控中，有機會時會立即通知</p>
            </div>
            """
        
        html = ""
        for i, opp in enumerate(opportunities, 1):
            final_rec = opp.get('final_recommendation', {})
            action = final_rec.get('action', opp.get('action', 'UNKNOWN'))
            etf_code = opp.get('etf', '')
            
            # 決定CSS類別
            css_class = self._get_opportunity_css_class(action)
            
            # 信心度標籤
            confidence = opp.get('enhanced_confidence', opp.get('confidence', 'medium'))
            confidence_badge = self._get_confidence_badge(confidence)
            
            html += f"""
            <div class="opportunity {css_class}">
                <h3>#{i} {etf_code} - {action} {confidence_badge}</h3>
                <p><strong>📋 操作建議:</strong> {final_rec.get('reasoning', opp.get('reason', ''))}</p>
                
                <div class="opportunity-meta">
                    {self._generate_opportunity_meta_html(opp)}
                </div>
            </div>
            """
        
        return html
    
    def _generate_opportunity_meta_html(self, opp: Dict) -> str:
        """生成機會的詳細資訊HTML"""
        meta_html = ""
        
        # 基本資訊
        if 'days_after' in opp:
            meta_html += f"""
            <div class="meta-item">
                <div class="meta-label">除息後天數</div>
                <div class="meta-value">{opp['days_after']} 天</div>
            </div>
            """
        
        if 'dividend_date' in opp:
            meta_html += f"""
            <div class="meta-item">
                <div class="meta-label">除息日期</div>
                <div class="meta-value">{opp['dividend_date']}</div>
            </div>
            """
        
        # 技術分析
        tech_analysis = opp.get('technical_analysis', {})
        if tech_analysis:
            score = tech_analysis.get('score', 50)
            meta_html += f"""
            <div class="meta-item">
                <div class="meta-label">技術評分</div>
                <div class="meta-value">{score:.0f}/100</div>
            </div>
            """
        
        # 風險評估
        risk_assessment = opp.get('risk_assessment', {})
        if risk_assessment:
            risk_level = risk_assessment.get('risk_level', 'medium')
            meta_html += f"""
            <div class="meta-item">
                <div class="meta-label">風險等級</div>
                <div class="meta-value">{risk_level}</div>
            </div>
            """
        
        # 投資配置
        position_sizing = opp.get('position_sizing', {})
        if position_sizing:
            allocation = position_sizing.get('suggested_allocation_pct', 0)
            meta_html += f"""
            <div class="meta-item">
                <div class="meta-label">建議配置</div>
                <div class="meta-value">{allocation:.1f}%</div>
            </div>
            """
        
        return meta_html
    
    def _get_opportunity_css_class(self, action: str) -> str:
        """根據操作類型獲取CSS類別"""
        if action == 'STRONG_BUY':
            return 'strong-buy'
        elif 'BUY' in action:
            return 'buy'
        elif 'SELL' in action:
            return 'sell'
        else:
            return 'hold'
    
    def _get_confidence_badge(self, confidence: str) -> str:
        """生成信心度標籤"""
        badge_class = {
            'very_high': 'status-high',
            'high': 'status-high',
            'medium': 'status-medium',
            'low': 'status-low'
        }.get(confidence, 'status-medium')
        
        confidence_text = {
            'very_high': '極高',
            'high': '高',
            'medium': '中',
            'low': '低'
        }.get(confidence, '中')
        
        return f'<span class="status-badge {badge_class}">信心度: {confidence_text}</span>'
    
    def _generate_no_data_dashboard(self) -> str:
        """生成無數據時的儀表板"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>ETF策略儀表板 - 無數據</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
            text-align: center;
        }}
        .container {{ 
            max-width: 600px; 
            margin: 100px auto; 
            background: white; 
            padding: 50px; 
            border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .icon {{ font-size: 4em; margin-bottom: 20px; }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        p {{ color: #666; margin-bottom: 30px; }}
        .action-btn {{ 
            display: inline-block; 
            padding: 12px 24px; 
            background: #667eea; 
            color: white; 
            text-decoration: none; 
            border-radius: 6px; 
            transition: background 0.2s;
        }}
        .action-btn:hover {{ background: #5a67d8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">📊</div>
        <h1>ETF策略儀表板</h1>
        <p>⚠️ 暫無分析數據</p>
        <p>請先執行主分析程式來生成投資建議</p>
        <p><small>當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        <a href="#" class="action-btn" onclick="location.reload()">🔄 重新整理</a>
    </div>
</body>
</html>
        """
    
    def save_dashboard(self) -> bool:
        """保存儀表板到Firebase"""
        try:
            print("🎨 生成儀表板HTML...")
            html_content = self.generate_dashboard()
            
            dashboard_data = {
                'html_content': html_content,
                'generated_at': datetime.now().isoformat(),
                'version': 'modular_v1.0'
            }
            
            print("💾 保存儀表板到Firebase...")
            success = self.firebase_client.save('dashboard/latest', dashboard_data)
            
            if success:
                print("✅ 儀表板已保存到Firebase")
                
                # 同時保存到每日歷史
                daily_key = f"dashboard/history/{datetime.now().strftime('%Y-%m-%d')}"
                self.firebase_client.save(daily_key, dashboard_data)
                
                return True
            else:
                print("❌ 儀表板保存失敗")
                return False
                
        except Exception as e:
            print(f"❌ 儀表板生成失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_dashboard_url(self):
        """顯示儀表板URL（如果有的話）"""
        firebase_url = self.firebase_client.firebase_url
        if firebase_url and 'firebasedatabase.app' in firebase_url:
            dashboard_url = f"{firebase_url}/dashboard/latest/html_content.json"
            print(f"🔗 儀表板數據URL: {dashboard_url}")
        else:
            print("💡 請設置Firebase URL以獲取儀表板鏈接")

def main():
    """主函數"""
    print("🎨 ETF策略儀表板生成器")
    print("=" * 40)
    
    try:
        dashboard = ModularDashboard()
        success = dashboard.save_dashboard()
        
        if success:
            print("\n🎉 儀表板生成完成！")
            dashboard.print_dashboard_url()
            print("\n💡 提示：")
            print("   - 儀表板已保存到Firebase")
            print("   - 可以通過Firebase數據庫查看")
            print("   - 建議設置定期更新機制")
        else:
            print("\n💥 儀表板生成失敗")
            print("🔍 請檢查:")
            print("   - Firebase URL是否正確設置")
            print("   - 網絡連接是否正常")
            print("   - 是否有分析數據")
        
    except Exception as e:
        print(f"💥 程式執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
