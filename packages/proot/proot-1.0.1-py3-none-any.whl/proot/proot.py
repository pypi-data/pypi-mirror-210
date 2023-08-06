import inspect
from pathlib import Path


def get_proot(marker="pyproject.toml"):
    # 呼び出し元のファイルのフルパスを取得
    frame = inspect.stack()[1]
    caller_file = frame[0].f_globals['__file__']
    caller_path = Path(caller_file).resolve().parent

    path = caller_path
    while path != path.parent:  # ルートフォルダに到達するまでループ
        if marker.startswith("."):  # マーカーが拡張子の場合
            if any(f for f in path.iterdir() if f.suffix == marker):
                return path
        else:  # マーカーが具体的なファイル名の場合
            if (path / marker).exists():
                return path
        path = path.parent
    raise FileNotFoundError(f"No '{marker}' file found, cannot determine project root")
