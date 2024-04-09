import argparse
from pathlib import Path

from src.create_messages import (
    create_input_messages,
)
from src.generate_by_gpt import generate_message
from src.preprocess import preprocess
from src.utils.init_logger import init_logger

ROOT_PATH = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT_PATH.joinpath("output", "category")


# ログ設定ファイルの読み込み
logger = init_logger()

CATEGORY_CSV_COLS = [
    "id",
    "属性名",
    "属性グループ名",
    "ラベル",
    "ラベリング信頼度",
]


def main(obj_name: str) -> None:
    # データの前処理を行う
    obj_dataframe = preprocess(obj_name=obj_name)
    if obj_dataframe is None:
        logger.error("Failed to preprocess data")
        return

    # アウトプットを初期化する
    _initialize_file(obj_name=obj_name, path=OUTPUT_PATH, columns=CATEGORY_CSV_COLS)

    # 仕様レコードごとにSQLを生成する
    for _, row in obj_dataframe.iterrows():
        # JSON形式に変換する
        json_str = row.to_json(force_ascii=False)
        logger.info(json_str)

        convert_sqlx = generate_message(
            messages=create_input_messages(json_str=json_str),
        )
        # 書き込みを行う
        _append_to_file(
            obj_name=obj_name,
            content=convert_sqlx,
            path=OUTPUT_PATH,
        )


def _append_to_file(obj_name: str, content: str, path: Path) -> None:
    file_name = path.joinpath(f"{obj_name}.csv")
    # ファイルを追記モードで開く
    with Path(file_name).open("a") as file:
        # 指定された内容をファイルに書き込む
        file.write(content)


# ファイルに書き込みが存在する場合, ファイルを初期化する
def _initialize_file(obj_name: str, path: Path, columns: list) -> None:
    # ファイルが存在しない場合、ディレクトリを作成する
    Path(path).mkdir(parents=True, exist_ok=True)

    file_name = path.joinpath(f"{obj_name}.csv")
    # CSVファイルを開き、カラムを書き込む
    with open(file_name, "w", newline="") as csvfile:
        # カンマ区切りでカラムを結合し、ファイルに書き込む
        csvfile.write(",".join(columns) + "\n")


if __name__ == "__main__":
    # argparseをセットアップします
    parser = argparse.ArgumentParser(description="Process some objects.")
    parser.add_argument("obj_name", type=str, help="The name of the object to process")

    # コマンドライン引数を解析します
    args = parser.parse_args()

    # main関数を呼び出し、コマンドラインから取得したobj_nameを引数に渡します
    main(obj_name=args.obj_name)
