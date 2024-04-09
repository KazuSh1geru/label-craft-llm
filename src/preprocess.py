from pathlib import Path

import pandas as pd

from src.utils.init_logger import init_logger

# ログ設定ファイルの読み込み
logger = init_logger()
ROOT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_PATH.joinpath("data")
PROCESSED_PATH = ROOT_PATH.joinpath("processed")

TARGET_COLS = [
    "c_code",
    "ca_name",
    "cag_name",
    "sectors",
    "subsectors",
    "industries",
]

RENAME_COLS = [
    "id",
    "属性名",
    "属性グループ名",
    "業界大分類",
    "業界中分類",
    "業界小分類",
]


def preprocess(obj_name: str) -> pd.DataFrame | None:
    try:
        obj_dataframe = pd.read_csv(DATA_PATH.joinpath(f"{obj_name}.csv"))
        logger.info(obj_dataframe.columns)

        # 必要なカラムのみ抽出
        obj_dataframe = obj_dataframe[TARGET_COLS]

        obj_dataframe.columns = RENAME_COLS
        logger.info(obj_dataframe.columns)
        # ファイルが存在しない場合、ディレクトリを作成する
        Path(PROCESSED_PATH).mkdir(parents=True, exist_ok=True)

        obj_dataframe.to_csv(
            PROCESSED_PATH.joinpath(f"{obj_name}.csv"),
            index=False,
        )
    except Exception:
        logger.exception("Failed to preprocess")
        return None
    else:
        logger.info("Finish preprocess")
        return obj_dataframe


if __name__ == "__main__":
    preprocess("組織属性ラベリング検証")
