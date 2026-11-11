"""Export the logical source registry for external tools; never replace its manifest."""
import argparse
import json
from pathlib import Path
from registry_store import NAME, read_json

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    output=Path(args.output).resolve()
    if output==root/'data'/NAME:
        raise SystemExit('导出文件不能覆盖源库清单')
    output.parent.mkdir(parents=True,exist_ok=True)
    value=read_json(root/'data'/NAME)
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(f"已导出{len(value['works'])}条原始身份记录：{output}")
