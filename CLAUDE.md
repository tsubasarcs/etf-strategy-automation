### 🔄 ETF策略專案感知與上下文
- **系統版本**: v2.0 簡化穩定版 - 零API依賴的分層配置系統
- **核心邏輯**: 基於37個週期100%成功率的除息後1-7天買進策略  
- **主要目標**: 7.08%平均報酬的自動化投資系統
- **專案狀態**: 生產就緒，GitHub Actions每日15:30自動執行
- **Always read the main context document** 開始新對話時優先理解系統架構
- **Check Firebase數據結構** 在處理數據查詢時參考最新的資料庫結構

### 🏗️ 代碼結構與模組化 (ETF專案特定)
- **Never modify files longer than 300 lines** - ETF專案重視穩定性，保持文件精簡
- **Follow the layered config pattern** - 靜態配置 + 動態配置 + 配置管理器的三層架構
- **Maintain backward compatibility** - config/__init__.py必須支援舊版API (DIVIDEND_CALENDAR)
- **Use virtual environment etf-env** 執行任何Python命令時
- **Respect the directory structure**:
  ```
  scripts/config/     # 分層配置系統 - 專案核心
  scripts/core/       # 核心引擎 (Firebase, 配置管理)
  scripts/analysis/   # 投資分析邏輯
  scripts/strategy/   # 策略引擎
  ```

### 🎯 ETF投資邏輯一致性
- **Always maintain the 1-7 days buy window logic** - 這是37個週期驗證的核心邏輯
- **Preserve the success rate and return calculations** - 不可修改歷史驗證的績效數據
- **Keep ETF priority order**: 0056 (priority:1) > 00919 (priority:2) > 00878 (priority:3)
- **Maintain dividend date prediction patterns** - 基於歷史規律的季度預測邏輯
- **Follow the layered config approach** - 靜態base_dividend.py + 動態dynamic_dividend.json

### 🧪 測試與可靠性 (ETF專案專用)
- **Always test config system first** - 配置系統是專案核心，優先測試
- **Use the existing test suites**: `./test_system.sh`, `python check_dependencies.py`
- **Validate Firebase connectivity** - 確保Firebase儲存和查詢正常
- **Test with real ETF codes only**: 0056, 00878, 00919 - 不使用模擬數據
- **Mock external APIs carefully** - 証交所API有SSL問題，測試時需要模擬

### ✅ 任務完成規則
- **Check system health after changes** - 修改後執行 `./test_system.sh`
- **Validate config integrity** - 確保配置系統5/5測試通過
- **Ensure backward compatibility** - 舊代碼必須能使用DIVIDEND_CALENDAR
- **Update Firebase structure documentation** - 修改數據結構時更新文檔

### 📎 風格與慣例 (ETF專案專用)
- **Use Python 3.9+** with type hints for better Claude Code compatibility
- **Follow the existing naming conventions**:
  - `get_dividend_schedule()` for new API
  - `DIVIDEND_CALENDAR` for backward compatibility
  - `latest_modular_status` for Firebase paths
- **Maintain logging consistency**:
  ```python
  print("📊 配置系統載入...")  # 使用emoji prefix
  print("✅ 成功")            # 成功狀態
  print("❌ 失敗")            # 錯誤狀態
  ```
- **Use ISO datetime format**: "2025-07-22T22:07:00" for all timestamps
- **Keep decimal precision**: Use 2 decimal places for prices, percentages

### 🔥 Firebase與MCP整合規則
- **Always preserve Firebase data structure** - 不可破壞現有查詢路徑
- **Maintain Claude MCP compatibility** - 確保Claude可以直接查詢投資建議
- **Keep critical paths stable**:
  - `/latest_modular_status` - 系統狀態和投資機會
  - `/latest_prices/{ETF}` - ETF最新價格
  - `/dividend_config/latest` - 除息日程配置
- **Follow the query patterns** documented in context for optimal Claude interaction

### 📚 文檔與可解釋性
- **Update context document** when adding new features or changing architecture
- **Maintain the investment logic explanations** - 37個週期的績效數據是系統核心價值
- **Document config system changes** - 分層配置系統是創新點，需詳細記錄
- **Explain Firebase data structure updates** for Claude MCP queries

### 🧠 AI行為規則 (ETF專項)
- **Never assume ETF market hours** - 台灣股市有特定交易時間
- **Never modify historical performance data** - 37週期/7.08%報酬率/100%成功率是事實
- **Always check dividend date validity** - 除息日期必須符合台灣ETF實際規律
- **Never break the config layer separation** - 靜態配置與動態配置有明確分工
- **Respect SSL certificate issues** - 証交所API有已知SSL問題，不強制修復

### 🚨 ETF專案關鍵限制
- **Investment advice is reference only** - 系統建議僅供參考，需註明風險
- **Maintain data source priorities**: Config System > Firebase History > External APIs
- **Preserve the simplified architecture** - v2.0版本專注穩定性，避免複雜化
- **Keep GitHub Actions workflow stable** - 生產環境每日運行，變更需謹慎
- **SSL issues are acceptable** - 數據收集失敗不影響核心投資邏輯

### 💡 ETF專案創新特色
- **Layered configuration system** - 業界首創的投資策略配置管理
- **Zero API dependency** - 不依賴不穩定外部API的自主系統
- **100% success rate validation** - 基於實際歷史數據的策略驗證
- **Claude MCP integration ready** - 支援AI助手直接查詢投資建議
- **Automated decision support** - GitHub Actions自動化投資決策支援

---

## 🎯 工作優先級指引

### 🥇 高優先級 (直接影響投資決策)
1. 配置系統穩定性 - 確保除息日期準確
2. 投資邏輯正確性 - 維護1-7天買進窗口
3. Firebase數據完整性 - 保證Claude MCP查詢可用
4. 系統健康監控 - 確保每日自動執行正常

### 🥈 中優先級 (改善用戶體驗)  
1. SSL問題解決 - 改善數據收集穩定性
2. 測試覆蓋增強 - 提高系統可靠性
3. 文檔完善 - 便於維護和擴展
4. 性能優化 - 加快分析執行速度

### 🥉 低優先級 (功能增強)
1. 新ETF支援 - 擴展投資標的
2. 策略模型改進 - 提升預測準確度  
3. 視覺化增強 - 改善結果呈現
4. 國際化支援 - 支援其他市場ETF