# Update Dividend Schedule

Update the dynamic dividend configuration for ETF ex-dividend dates.

## Purpose

This command helps you update the dividend schedule when new ex-dividend dates are announced or need correction.

## Usage

```
/update-dividend
```

## Configuration Files

### Static Configuration
- `scripts/config/base_dividend.py` - Historical dividend data (don't modify)
- `scripts/config/etf_config.py` - ETF basic information

### Dynamic Configuration
- `scripts/config/dynamic_dividend.json` - Runtime updates (modify this)

## Update Process

1. **Check current configuration**
```python
cd scripts
python -c "from core.config_manager import get_dividend_schedule; import json; print(json.dumps(get_dividend_schedule(), indent=2, ensure_ascii=False))"
```

2. **Edit dynamic configuration**
```bash
# Edit the JSON file
nano scripts/config/dynamic_dividend.json
```

3. **Validate changes**
```python
python test_config_system.py
```

## JSON Format

```json
{
  "0056": {
    "2025": {
      "ex_dividend_dates": ["2025-03-20", "2025-06-19"],
      "payment_dates": ["2025-04-25", "2025-07-25"],
      "dividend_amounts": [0.75, 0.80]
    }
  }
}
```

## Important Notes

- Dates must be in "YYYY-MM-DD" format
- Arrays must have matching lengths
- Missing data will fall back to base configuration
- Changes take effect immediately

## Verification

After updating, verify the configuration:
```bash
cd scripts
python -c "
from core.config_manager import ConfigManager
cm = ConfigManager()
for etf in ['0056', '00878', '00713', '00919']:
    schedule = cm.get_etf_dividend_schedule(etf)
    print(f'{etf}: {len(schedule)} records')
"
```