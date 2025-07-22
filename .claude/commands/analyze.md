# ETF Analysis Runner

Run the ETF dividend strategy analysis for Taiwan ETFs.

## Purpose

This command executes the complete ETF analysis pipeline, checking for optimal entry points based on dividend patterns and technical indicators.

## Usage

```
/analyze
```

## What this command does

1. **Loads configuration** from base and dynamic dividend files
2. **Fetches latest ETF data** for 0056, 00878, 00713, 00919
3. **Runs technical analysis** (RSI, Bollinger Bands, Volume)
4. **Performs risk assessment** and opportunity scoring
5. **Generates signals** for buy/sell recommendations
6. **Saves results** to Firebase (if configured)

## Example Commands

### Run complete analysis
```bash
# Activate environment and run
source etf-env/bin/activate
cd scripts
python main_analyzer.py
```

### Quick analysis script
```bash
# Use the convenience script
./start_analysis.sh
```

### Test configuration first
```bash
# Test system before analysis
./test_system.sh
```

## Output Format

The analysis generates:
- Entry signals with confidence scores
- Risk assessments with suggested position sizes
- Technical indicator values
- Opportunity scores (0-100)
- Detailed recommendations

## Schedule

- Automated: Daily at 15:30 Taiwan time via GitHub Actions
- Manual: Run anytime using the commands above

## ETF Coverage

| ETF | Name | Dividend Frequency |
|-----|------|-------------------|
| 0056 | 元大高股息 | Quarterly (3,6,9,12) |
| 00878 | 國泰永續高股息 | Quarterly (2,5,8,11) |
| 00713 | 元大台灣高息低波 | Biannual (7,12) |
| 00919 | 群益台灣精選高息 | Quarterly (3,6,9,12) |