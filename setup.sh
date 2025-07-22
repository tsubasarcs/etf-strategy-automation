#!/bin/bash

# ETF策略自動化系統環境設置腳本
# 版本: v2.0
# 日期: 2025-07-22

set -e  # 遇到錯誤立即退出

echo "🚀 ETF策略自動化系統環境設置"
echo "=================================="

# 檢查是否在正確的目錄
if [ ! -f "README.md" ] || [ ! -d "scripts" ]; then
    echo "❌ 錯誤: 請在專案根目錄執行此腳本"
    echo "💡 正確位置應該包含 README.md 和 scripts 目錄"
    exit 1
fi

echo "✅ 專案目錄檢查通過"

# 檢查Python版本
PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "Python not found")
echo "🐍 Python版本: $PYTHON_VERSION"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝，請先安裝Python3"
    exit 1
fi

# 創建虛擬環境
echo ""
echo "📦 創建Python虛擬環境..."
if [ -d "etf-env" ]; then
    echo "⚠️  虛擬環境已存在，跳過創建"
else
    python3 -m venv etf-env
    echo "✅ 虛擬環境創建成功: etf-env/"
fi

# 激活虛擬環境
echo ""
echo "🔄 激活虛擬環境..."
source etf-env/bin/activate

# 升級pip
echo ""
echo "⬆️  升級pip..."
pip install --upgrade pip

# 安裝依賴項目
echo ""
echo "📚 安裝依賴項目..."

# 核心依賴
echo "   安裝核心依賴..."
pip install requests pandas numpy

# 可選依賴
echo "   安裝可選依賴..."
pip install lxml beautifulsoup4

echo "✅ 所有依賴安裝完成"

# 驗證安裝
echo ""
echo "🧪 驗證安裝..."
python -c "
import sys
modules = ['requests', 'pandas', 'numpy', 'lxml', 'bs4']
failed = []

for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
        failed.append(module)

if failed:
    print(f'⚠️  安裝失敗的模組: {failed}')
    sys.exit(1)
else:
    print('🎉 所有模組安裝成功!')
"

# 測試配置系統
echo ""
echo "🔧 測試配置系統..."
cd scripts

if python check_dependencies.py; then
    echo "✅ 依賴檢查通過"
else
    echo "⚠️  依賴檢查發現問題，但繼續進行..."
fi

# 測試配置載入
echo ""
echo "📋 測試配置載入..."
python -c "
import sys
sys.path.append('config')
sys.path.append('core')

try:
    from config_manager import get_dividend_schedule
    schedule = get_dividend_schedule()
    print(f'✅ 配置系統正常: {len(schedule)} 個ETF')
    
    from config.etf_config import ETF_LIST, ETF_INFO
    print(f'✅ ETF基本配置: {len(ETF_LIST)} 個ETF')
    
except Exception as e:
    print(f'❌ 配置測試失敗: {e}')
    exit(1)
"

cd ..

# 創建啟動腳本
echo ""
echo "📝 創建快速啟動腳本..."

cat > start_analysis.sh << 'EOF'
#!/bin/bash

# ETF分析系統快速啟動腳本

echo "🚀 啟動ETF分析系統..."

# 檢查虛擬環境
if [ ! -d "etf-env" ]; then
    echo "❌ 虛擬環境不存在，請先執行 ./setup.sh"
    exit 1
fi

# 激活虛擬環境
echo "🔄 激活虛擬環境..."
source etf-env/bin/activate

# 執行分析
echo "📊 開始執行分析..."
cd scripts
python main_analyzer.py

echo "🎉 分析完成！"
EOF

chmod +x start_analysis.sh

# 創建測試腳本
cat > test_system.sh << 'EOF'
#!/bin/bash

# ETF系統測試腳本

echo "🧪 ETF系統測試..."

# 激活虛擬環境
source etf-env/bin/activate

# 執行測試
cd scripts
echo "1. 依賴檢查測試..."
python check_dependencies.py

echo ""
echo "2. 配置系統測試..."
python test_config_system.py

echo "🎉 系統測試完成！"
EOF

chmod +x test_system.sh

# 完成設置
echo ""
echo "=================================="
echo "🎉 ETF策略自動化系統設置完成！"
echo "=================================="
echo ""
echo "📋 下一步操作："
echo ""
echo "1️⃣  測試系統："
echo "   ./test_system.sh"
echo ""
echo "2️⃣  執行分析："
echo "   ./start_analysis.sh"
echo ""
echo "3️⃣  手動操作："
echo "   source etf-env/bin/activate  # 激活環境"
echo "   cd scripts"
echo "   python main_analyzer.py      # 執行分析"
echo ""
echo "💡 提示："
echo "   - 每次使用前需要激活虛擬環境"
echo "   - 虛擬環境目錄: etf-env/"
echo "   - 可用快速腳本: start_analysis.sh, test_system.sh"
echo ""
echo "🔗 GitHub Actions 也會自動安裝這些依賴"
echo "=================================="