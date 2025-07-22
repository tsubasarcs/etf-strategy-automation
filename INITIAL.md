## FEATURE:

ETF策略自動化系統 - 基於除息週期的智能投資決策系統

核心功能包括：
- 分層配置系統 (靜態基礎配置 + 動態更新機制)
- 投資機會自動識別 (基於37個週期100%成功率的策略)
- Firebase即時資料庫整合
- GitHub Actions自動化執行
- Claude MCP直接查詢支援
- 零API依賴的穩定架構設計

## EXAMPLES:

目前專案中的關鍵模式和範例：

### 配置系統範例
- `scripts/config/base_dividend.py` - 展示如何基於歷史規律創建靜態配置
- `scripts/config/dynamic_dividend.json` - 動態配置檔案結構和更新機制
- `scripts/core/config_manager.py` - 統一配置管理器，展示分層配置合併邏輯

### 分析邏輯範例  
- `scripts/analysis/basic_analyzer.py` - 核心投資機會識別邏輯
- `scripts/strategy/opportunity_finder.py` - 策略引擎和信號生成
- `scripts/main_analyzer.py` - 主分析流程和系統整合

### 測試和自動化範例
- `scripts/test_config_system.py` - 完整的配置系統測試套件
- `.github/workflows/etf-daily.yml` - 生產級GitHub Actions工作流程
- `setup.sh` - 環境自動化設置腳本

### Firebase整合範例
- `scripts/core/firebase_client.py` - Firebase即時資料庫客戶端
- 數據結構: latest_modular_status, latest_prices, dividend_config等路徑

## DOCUMENTATION:

### 投資策略文檔
- **歷史績效驗證**: 37個除息週期，100%成功率，平均7.08%報酬率
- **ETF個別表現**: 0056 (9.43%), 00919 (6.26%), 00878 (5.56%)
- **核心邏輯**: 除息後1-7天買進窗口，獲利5%或最佳時機賣出

### 技術文檔
- **Python環境**: 3.9+，使用虛擬環境etf-env
- **核心依賴**: pandas, numpy, requests, firebase相關套件
- **系統架構**: 分層配置系統 + 分析引擎 + 策略引擎

### API和整合文檔
- **Firebase**: 即時資料庫結構和查詢路徑
- **證交所API**: TWSE股票日報表API (有SSL憑證問題)
- **Claude MCP**: 直接查詢Firebase數據的整合方式

### GitHub Actions文檔
- **執行時間**: 每日台灣時間15:30 (UTC 07:30)
- **工作流程**: 配置載入 → 數據分析 → 結果儲存 → Firebase備份
- **環境變數**: FIREBASE_URL等敏感資訊管理

## OTHER CONSIDERATIONS:

### 已知技術問題
1. **SSL憑證問題**: 證交所API有SSL憑證驗證問題，需要特殊處理
2. **向後相容性**: 舊代碼使用DIVIDEND_CALENDAR，新代碼使用get_dividend_schedule()
3. **數據收集穩定性**: 外部API不穩定，主要依賴配置系統和Firebase歷史數據

### 系統設計原則
1. **穩定性優先**: v2.0專注簡化和穩定，避免依賴不穩定的外部API
2. **分層架構**: 靜態配置 + 動態配置 + 統一管理，確保靈活性和可維護性
3. **自動化優先**: GitHub Actions自動執行，減少人工干預
4. **AI友善**: 支援Claude MCP直接查詢，提供即時投資建議

### 投資策略特色
1. **歷史驗證**: 基於37個實際除息週期的回測結果
2. **風險控制**: 100%成功率記錄，無失敗週期
3. **時機精準**: 除息後1-7天的最佳買進窗口
4. **標的優化**: 根據歷史表現排序ETF優先級

### Claude Code開發重點
1. **配置系統**: 理解分層配置的設計邏輯和合併機制
2. **投資邏輯**: 掌握核心的1-7天買進窗口策略
3. **Firebase整合**: 熟悉數據結構和查詢路徑
4. **測試驗證**: 確保配置系統5/5測試通過
5. **向後相容**: 維護舊版API的相容性

### 常見AI助手容易遺漏的點
1. **不要修改歷史績效數據** - 37週期/7.08%是實際驗證結果
2. **不要破壞配置系統分層** - 靜態與動態配置有明確分工
3. **不要假設SSL問題已解決** - 這是已知長期問題  
4. **不要忽略向後相容性** - 必須支援DIVIDEND_CALENDAR舊API
5. **不要修改投資時機邏輯** - 1-7天窗口是策略核心