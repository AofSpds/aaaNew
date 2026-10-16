#!/usr/bin/env bash
# usage: run.sh <outname> <claude args...>   (run from experiment cwd)
S="C:/Users/ms1pk/AppData/Local/Temp/claude/C--Users-ms1pk-dev-aaaNew/e3bfd5a5-84f2-486d-8ccc-fa5aff396d2b/scratchpad"
out="$1"; shift
unset $(env | grep -oE '^(CLAUDE[A-Z_]*|MCP_[A-Z_]*|ANTHROPIC_BASE_URL)=' | grep -v ADDITIONAL_DIRECTORIES_CLAUDE_MD | tr -d '=')
"${XBIN:-claude}" "$@" --model haiku --output-format json < /dev/null > "$S/$out.json" 2> "$S/$out.err"
echo "exit=$?"
python -I -c "
import json,sys
try:
  d=json.load(open(sys.argv[1],encoding='utf-8'))
  open(sys.argv[2],'w',encoding='utf-8').write(str(d.get('session_id'))+'\n'+str(d.get('is_error'))+' '+str(d.get('subtype'))+'\n'+str(d.get('result')))
except Exception as e:
  open(sys.argv[2],'w',encoding='utf-8').write('PARSE_FAIL '+repr(e))
" "$S/$out.json" "$S/$out.txt"
