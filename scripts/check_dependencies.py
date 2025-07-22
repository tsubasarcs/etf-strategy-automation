#!/usr/bin/env python3
"""
依賴項目檢查腳本
檢查ETF分析系統所需的所有依賴項目

使用方式：
    python check_dependencies.py
"""

import sys
import importlib

def check_module(module_name, description=""):
    """檢查單個模組"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name:20s} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name:20s} - 缺失 ({description})")
        print(f"   錯誤: {e}")
        return False

def main():
    print("🔍 ETF分析系統依賴項目檢查")
    print("="*50)
    
    # 核心依賴
    print("\n📦 核心依賴項目:")
    core_modules = [
        ("requests", "HTTP請求庫"),
        ("pandas", "數據處理庫"),
        ("numpy", "數值計算庫"),
        ("json", "JSON處理（內建）"),
        ("datetime", "日期時間處理（內建）"),
        ("os", "作業系統介面（內建）"),
        ("sys", "系統相關功能（內建）")
    ]
    
    core_results = []
    for module, desc in core_modules:
        result = check_module(module, desc)
        core_results.append(result)
    
    # 可選依賴
    print("\n📦 可選依賴項目:")
    optional_modules = [
        ("lxml", "XML/HTML解析庫"),
        ("bs4", "BeautifulSoup4網頁解析庫"),
    ]
    
    optional_results = []
    for module, desc in optional_modules:
        result = check_module(module, desc)
        optional_results.append(result)
    
    # 專案模組檢查
    print("\n📦 專案模組檢查:")
    
    # 添加scripts目錄到路徑
    import os
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    
    project_modules = [
        ("config.etf_config", "ETF配置模組"),
        ("config.base_dividend", "基礎除息配置"),
        ("core.config_manager", "配置管理器"),
        ("core.firebase_client", "Firebase客戶端"),
        ("core.data_collector", "數據收集器"),
        ("core.etf_data_parser", "數據解析器"),
    ]
    
    project_results = []
    for module, desc in project_modules:
        result = check_module(module, desc)
        project_results.append(result)
    
    # 功能測試
    print("\n🧪 功能測試:")
    
    # 測試配置系統
    try:
        from core.config_manager import get_dividend_schedule
        schedule = get_dividend_schedule()
        if schedule:
            print(f"✅ 配置系統功能測試 - 成功載入 {len(schedule)} 個ETF")
        else:
            print("⚠️ 配置系統功能測試 - 配置為空")
    except Exception as e:
        print(f"❌ 配置系統功能測試 - 失敗: {e}")
    
    # 測試Firebase客戶端初始化
    try:
        from core.firebase_client import FirebaseClient
        client = FirebaseClient()
        print("✅ Firebase客戶端初始化 - 成功")
    except Exception as e:
        print(f"❌ Firebase客戶端初始化 - 失敗: {e}")
    
    # 統計結果
    print("\n" + "="*50)
    print("📊 檢查結果摘要:")
    
    core_passed = sum(core_results)
    core_total = len(core_results)
    print(f"核心依賴: {core_passed}/{core_total} 通過")
    
    optional_passed = sum(optional_results)
    optional_total = len(optional_results)
    print(f"可選依賴: {optional_passed}/{optional_total} 通過")
    
    project_passed = sum(project_results)
    project_total = len(project_results)
    print(f"專案模組: {project_passed}/{project_total} 通過")
    
    # 建議
    print("\n💡 建議:")
    if core_passed < core_total:
        print("❌ 核心依賴缺失，請執行:")
        print("   pip install requests pandas numpy")
    
    if optional_passed < optional_total:
        print("⚠️ 可選依賴缺失，建議執行:")
        print("   pip install lxml beautifulsoup4")
    
    if project_passed < project_total:
        print("⚠️ 專案模組問題，請檢查檔案是否存在且格式正確")
    
    if core_passed == core_total:
        print("✅ 核心依賴完整，系統應該可以正常運行")
        print("💡 可以嘗試執行: python main_analyzer.py")
    
    print("\n" + "="*50)
    
    return core_passed == core_total

if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 檢查被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 檢查過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)