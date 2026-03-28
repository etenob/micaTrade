# Agent Master Instructions (System-Specific)
## Environment
- **OS**: Windows
- **Shell**: PowerShell (preferred)

## Command Usage Rules
- **DO NOT** use 'cat'. Use 'type' or Python's 'open().read()'.
- **DO NOT** use 'grep'. Use PowerShell's 'Select-String' or Python's 'find()'.
- **DO NOT** use 'rm -rf'. Use 'Remove-Item -Recurse -Force'.
- **DELETING MULTIPLE FILES**: Use 'Remove-Item file1, file2, file3'.

## Trading Specifics (Binance)
- **OCO Orders**: Always ensure Price (TP) > Market Price > StopPrice (Trigger) > StopLimitPrice (Execution).
- **Precision**: Use 'bm.format_quantity_str()' and 'bm.format_price_str()' from 'binance_manager.py'.
