## <a name="main_help"></a> python3 -m clocdirtree.main --help
```
usage: python3 -m clocdirtree.main [-h] [-la] --clocdir CLOCDIR --outdir
                                   OUTDIR [--exclude EXCLUDE [EXCLUDE ...]]
                                   [--include-lang INCLUDE_LANG [INCLUDE_LANG ...]]
                                   [--exclude-lang EXCLUDE_LANG [EXCLUDE_LANG ...]]

dump cloc data and navigate it as directory tree

options:
  -h, --help            show this help message and exit
  -la, --logall         Log all messages (default: False)
  --clocdir CLOCDIR     Directory to analyze by 'cloc' (default: )
  --outdir OUTDIR       Output directory (default: )
  --exclude EXCLUDE [EXCLUDE ...]
                        Space separated list of files and directories to
                        exclude. e.g. --exclude '/usr/*' '*/tmp/*' (default:
                        [])
  --include-lang INCLUDE_LANG [INCLUDE_LANG ...]
                        Space separated list of languages to include.
                        (default: [])
  --exclude-lang EXCLUDE_LANG [EXCLUDE_LANG ...]
                        Space separated list of languages to exclude.
                        (default: [])
```
