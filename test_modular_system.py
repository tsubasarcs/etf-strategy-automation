# test_modular_system.py
"""模組化ETF策略系統測試器"""

import sys
import os
import traceback
import logging
from datetime import datetime
from typing import Dict, Any, List

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('modular_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ModularSystemTester:
    """模組化系統測試器"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        logger.info("🧪 開始模組化系統測試...")
    
    def test_1_module_imports(self) -> bool:
        """測試1: 模組導入"""
        logger.info("📦 測試模組導入...")
        
        try:
            # 測試配置模組
            from config import ETF_INFO, DIVIDEND_CALENDAR, ETF_LIST
            from config import BASIC_STRATEGY, TECHNICAL_PARAMS, RISK_WEIGHTS
            logger.info("  ✅ 配置模組導入成功")
            
            # 測試核心模組
            from core import FirebaseClient, ETFDataCollector, ETFDataParser
            logger.info("  ✅ 核心模組導入成功")
            
            # 測試分析模組
            from analysis import BasicDividendAnalyzer, TechnicalAnalyzer, RiskAnalyzer
            logger.info("  ✅ 分析模組導入成功")
            
            # 測試策略模組
            from strategy import SignalGenerator, OpportunityFinder
            logger.info("  ✅ 策略模組導入成功")
            
            # 驗證配置數據
            assert len(ETF_LIST) == 3
            assert '0056' in ETF_INFO
            assert 'buy_window_days' in BASIC_STRATEGY
            logger.info("  ✅ 配置數據驗證通過")
            
            self.test_results['module_imports'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ 模組導入失敗: {e}")
            traceback.print_exc()
            self.test_results['module_imports'] = False
            return False
    
    def test_2_firebase_connectivity(self) -> bool:
        """測試2: Firebase連接"""
        logger.info("🔗 測試Firebase連接...")
        
        try:
            from core import FirebaseClient
            
            client = FirebaseClient()
            
            # 測試寫入
            test_data = {
                'test': True,
                'timestamp': datetime.now().isoformat(),
                'system': 'modular_test'
            }
            
            write_success = client.save('test/modular_connectivity', test_data)
            if not write_success:
                raise Exception("Firebase寫入失敗")
            
            # 測試讀取
            read_data = client.get('test/modular_connectivity')
            if not read_data or read_data.get('test') != True:
                raise Exception("Firebase讀取失敗")
            
            logger.info("  ✅ Firebase讀寫測試通過")
            self.test_results['firebase_connectivity'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Firebase連接失敗: {e}")
            self.test_results['firebase_connectivity'] = False
            return False
    
    def test_3_data_collection(self) -> bool:
        """測試3: 數據收集功能"""
        logger.info("📊 測試數據收集...")
        
        try:
            from core import ETFDataCollector
            
            collector = ETFDataCollector()
            
            # 測試收集單一ETF數據
            test_etf = '0056'
            logger.info(f"  📈 測試收集 {test_etf} 數據...")
            
            # 嘗試獲取最近一個月數據
            year_month = datetime.now().strftime('%Y%m')
            monthly_data = collector.get_monthly_data(test_etf, year_month)
            
            if monthly_data is not None and len(monthly_data) > 0:
                logger.info(f"    ✅ 成功收集 {len(monthly_data)} 筆數據")
                
                # 驗證數據結構
                required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                missing_columns = [col for col in required_columns if col not in monthly_data.columns]
                
                if missing_columns:
                    raise Exception(f"缺少必要欄位: {missing_columns}")
                
                logger.info("    ✅ 數據結構驗證通過")
                self.test_results['data_collection'] = True
                return True
            else:
                raise Exception("數據收集返回空值")
                
        except Exception as e:
            logger.error(f"  ❌ 數據收集失敗: {e}")
            self.test_results['data_collection'] = False
            return False
    
    def test_4_analysis_modules(self) -> bool:
        """測試4: 分析模組"""
        logger.info("🔍 測試分析模組...")
        
        try:
            from analysis import BasicDividendAnalyzer, TechnicalAnalyzer, RiskAnalyzer
            import pandas as pd
            import numpy as np
            
            # 測試基礎除息分析
            dividend_analyzer = BasicDividendAnalyzer()
            opportunities = dividend_analyzer.find_dividend_opportunities()
            logger.info(f"  📅 基礎分析找到 {len(opportunities)} 個機會")
            
            # 測試技術分析
            technical_analyzer = TechnicalAnalyzer()
            
            # 創建測試數據
            dates = pd.date_range('2025-01-01', periods=50, freq='D')
            test_data = pd.DataFrame({
                'date': dates,
                'open': np.random.uniform(20, 25, 50),
                'high': np.random.uniform(25, 30, 50),
                'low': np.random.uniform(15, 20, 50),
                'close': np.random.uniform(20, 25, 50),
                'volume': np.random.randint(1000000, 5000000, 50)
            })
            
            # 計算技術指標
            enhanced_data = technical_analyzer.calculate_indicators(test_data)
            assert 'RSI' in enhanced_data.columns
            assert 'BB_Upper' in enhanced_data.columns
            logger.info("  📊 技術指標計算成功")
            
            # 生成信號
            signals = technical_analyzer.generate_signals(enhanced_data)
            tech_score = technical_analyzer.calculate_score(enhanced_data)
            logger.info(f"  🎯 生成 {len(signals)} 個技術信號，評分: {tech_score}")
            
            # 測試風險分析
            risk_analyzer = RiskAnalyzer()
            mock_opportunity = {
                'etf': '0056',
                'action': 'BUY',
                'days_after': 3,
                'confidence': 'high'
            }
            
            risk_assessment = risk_analyzer.calculate_comprehensive_risk(
                mock_opportunity, signals, test_data
            )
            
            assert 'comprehensive_risk_score' in risk_assessment
            assert 'risk_level' in risk_assessment
            logger.info(f"  ⚠️ 風險評估完成: {risk_assessment['risk_level']}")
            
            self.test_results['analysis_modules'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ 分析模組測試失敗: {e}")
            traceback.print_exc()
            self.test_results['analysis_modules'] = False
            return False
    
    def test_5_strategy_modules(self) -> bool:
        """測試5: 策略模組"""
        logger.info("🎯 測試策略模組...")
        
        try:
            from strategy import SignalGenerator, OpportunityFinder
            from analysis import TechnicalAnalyzer
            import pandas as pd
            import numpy as np
            
            # 測試信號生成器
            signal_generator = SignalGenerator()
            
            mock_opportunity = {
                'etf': '0056',
                'action': 'BUY',
                'confidence': 'high',
                'days_after': 2
            }
            
            mock_risk_assessment = {
                'risk_level': 'low',
                'comprehensive_risk_score': 30
            }
            
            # 生成投資建議
            recommendation = signal_generator.generate_final_recommendation(
                mock_opportunity, 75, mock_risk_assessment
            )
            
            assert 'action' in recommendation
            assert 'reasoning' in recommendation
            logger.info(f"  💡 投資建議: {recommendation['action']}")
            
            # 測試投資配置
            position_sizing = signal_generator.calculate_position_sizing(
                mock_risk_assessment, mock_opportunity
            )
            
            assert 'suggested_allocation_pct' in position_sizing
            logger.info(f"  💰 建議配置: {position_sizing['suggested_allocation_pct']:.1f}%")
            
            # 測試機會發現器
            opportunity_finder = OpportunityFinder()
            
            # 創建測試數據字典
            test_data_dict = {}
            for etf in ['0056', '00878', '00919']:
                dates = pd.date_range('2025-01-01', periods=40, freq='D')
                test_data_dict[etf] = pd.DataFrame({
                    'date': dates,
                    'open': np.random.uniform(20, 25, 40),
                    'high': np.random.uniform(25, 30, 40),
                    'low': np.random.uniform(15, 20, 40),
                    'close': np.random.uniform(20, 25, 40),
                    'volume': np.random.randint(1000000, 5000000, 40)
                })
            
            enhanced_opportunities = opportunity_finder.find_enhanced_opportunities(test_data_dict)
            logger.info(f"  🎪 增強機會分析: {len(enhanced_opportunities)} 個機會")
            
            self.test_results['strategy_modules'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ 策略模組測試失敗: {e}")
            traceback.print_exc()
            self.test_results['strategy_modules'] = False
            return False
    
    def test_6_main_analyzer_integration(self) -> bool:
        """測試6: 主分析器整合"""
        logger.info("🔄 測試主分析器整合...")
        
        try:
            # 這裡我們不實際執行完整分析，而是測試類的初始化
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            
            # 嘗試導入主分析器
            from main_analyzer import ETFStrategyAnalyzer
            
            # 初始化測試
            analyzer = ETFStrategyAnalyzer()
            
            # 驗證組件初始化
            assert hasattr(analyzer, 'firebase_client')
            assert hasattr(analyzer, 'data_collector')
            assert hasattr(analyzer, 'opportunity_finder')
            
            logger.info("  ✅ 主分析器初始化成功")
            logger.info("  ✅ 所有組件正確載入")
            
            self.test_results['main_analyzer_integration'] = True
            return True
            
        except Exception as e:
            logger.error(f"  ❌ 主分析器整合測試失敗: {e}")
            traceback.print_exc()
            self.test_results['main_analyzer_integration'] = False
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """生成測試報告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'tests_passed': passed_tests,
            'tests_total': total_tests,
            'success_rate': success_rate,
            'overall_status': 'PASS' if success_rate >= 0.8 else 'FAIL',
            'test_results': self.test_results,
            'recommendations': self._generate_recommendations(success_rate)
        }
        
        return report
    
    def _generate_recommendations(self, success_rate: float) -> List[str]:
        """生成建議"""
        recommendations = []
        
        if success_rate >= 0.9:
            recommendations.extend([
                "🎉 系統測試優秀！可以立即部署使用",
                "💡 建議開始小額實盤測試",
                "📈 考慮添加更多技術指標或策略"
            ])
        elif success_rate >= 0.8:
            recommendations.extend([
                "✅ 系統基本正常，可以謹慎使用",
                "🔧 建議修復失敗的測試項目",
                "📊 增加更多錯誤處理機制"
            ])
        else:
            recommendations.extend([
                "⚠️ 系統存在重要問題，建議修復後再使用",
                "🛠️ 優先解決模組導入和核心功能問題",
                "📋 建議重新檢查模組依賴關係"
            ])
        
        # 針對具體失敗項目的建議
        if not self.test_results.get('module_imports', True):
            recommendations.append("🔍 檢查Python路徑和模組文件結構")
        
        if not self.test_results.get('firebase_connectivity', True):
            recommendations.append("🔗 檢查Firebase URL和網絡連接")
        
        if not self.test_results.get('data_collection', True):
            recommendations.append("📊 檢查證交所API連接和數據格式")
        
        return recommendations
    
    def print_test_summary(self, report: Dict[str, Any]) -> None:
        """打印測試摘要"""
        print("\n" + "="*80)
        print("🧪 模組化ETF系統測試報告")
        print("="*80)
        print(f"⏰ 測試時間: {report['duration_seconds']:.1f}秒")
        print(f"📊 測試結果: {report['tests_passed']}/{report['tests_total']} 通過")
        print(f"📈 成功率: {report['success_rate']:.1%}")
        print(f"🎯 整體狀態: {report['overall_status']}")
        
        print(f"\n📋 詳細測試結果:")
        test_names = {
            'module_imports': '模組導入測試',
            'firebase_connectivity': 'Firebase連接測試',
            'data_collection': '數據收集測試',
            'analysis_modules': '分析模組測試',
            'strategy_modules': '策略模組測試',
            'main_analyzer_integration': '主分析器整合測試'
        }
        
        for test_key, result in report['test_results'].items():
            test_name = test_names.get(test_key, test_key)
            status = "✅ 通過" if result else "❌ 失敗"
            print(f"  {status} {test_name}")
        
        print(f"\n💡 建議事項:")
        for i, recommendation in enumerate(report['recommendations'], 1):
            print(f"  {i}. {recommendation}")
        
        print("\n" + "="*80)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """執行所有測試"""
        tests = [
            self.test_1_module_imports,
            self.test_2_firebase_connectivity,
            self.test_3_data_collection,
            self.test_4_analysis_modules,
            self.test_5_strategy_modules,
            self.test_6_main_analyzer_integration
        ]
        
        for test_func in tests:
            if not test_func():
                logger.warning(f"測試 {test_func.__name__} 失敗，繼續執行其他測試...")
        
        report = self.generate_test_report()
        self.print_test_summary(report)
        
        return report

def main():
    """主函數"""
    print("🚀 啟動模組化ETF策略系統測試器")
    print("=" * 50)
    
    tester = ModularSystemTester()
    report = tester.run_all_tests()
    
    # 保存測試報告
    try:
        import json
        with open('modular_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n💾 測試報告已保存到: modular_test_report.json")
    except Exception as e:
        print(f"⚠️ 測試報告保存失敗: {e}")
    
    # GitHub Actions 友好的輸出
    if report['overall_status'] == 'PASS':
        print(f"\n🎉 模組化系統測試通過！")
        print(f"📊 準備就緒指數: {report['success_rate']:.1%}")
        exit(0)
    else:
        print(f"\n⚠️ 模組化系統測試未完全通過")
        print(f"📊 準備就緒指數: {report['success_rate']:.1%}")
        exit(1)

if __name__ == "__main__":
    main()
