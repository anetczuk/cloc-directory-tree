## <a name="main_help"></a> python3 -m clocdirtree.main --help
```
usage: python3 -m clocdirtree.main [-h] [-la] --clocdir CLOCDIR --outdir
                                   OUTDIR [--exclude EXCLUDE [EXCLUDE ...]]
                                   [--clocexcludedir CLOCEXCLUDEDIR [CLOCEXCLUDEDIR ...]]

dump cloc data and navigate it as directory tree

options:
  -h, --help            show this help message and exit
  -la, --logall         Log all messages (default: False)
  --clocdir CLOCDIR     Directory to analyze by 'cloc' (default: )
  --outdir OUTDIR       Output directory (default: )
  --exclude EXCLUDE [EXCLUDE ...]
                        Space separated list of items to exclude. e.g.
                        --exclude '/usr/*' '*/tmp/*' (default: [])
  --clocexcludedir CLOCEXCLUDEDIR [CLOCEXCLUDEDIR ...]
                        Space separated list of dirs to exclude by cloc
                        itself. e.g. --exclude 'usr' 'tmp' (default: [])
```
