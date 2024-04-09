import json

COMMON_PROMPT = """あなたはデータラベリングを行うシステムです。JSONをインプットとして与えます.ルールに従い「ラベル」と「ラベリング信頼度」を選択して出力してください.
"""

COMMON_RULES = """
# 命令
・<属性名>を適切なラベルに分類してください.
・<属性名>に対して適切なラベリング信頼度を選択してください.
・背景情報として、<属性グループ名>,<業界大分類>,<業界中分類>,<業界小分類>を参照してください.
・出力は、id,属性名,属性グループ名,ラベル,ラベリング信頼度を含むカンマ区切りで出力してください.
・末尾は改行してください.
"""

CATEGORY_RULES = """
{COMMON_RULES}
# ラベルの選択肢
下記の6種類から1つ選択してください.
部門,業種,職種,入社形態,国,雇用形態

# ラベリング信頼度の選択肢
ラベリング精度を検証するのに使用します.下記の3種類から1つ選択してください.
高い,普通,低い
"""

CATEGORY_PROMPT = f"""{COMMON_PROMPT}
{CATEGORY_RULES}
"""


def get_select_prompt(select_items: list[str]) -> str:
    items = ",".join(select_items)
    return f"""{COMMON_PROMPT}
{COMMON_RULES}
# ラベルの選択肢
下記の選択肢から1つ選択してください.
{items}

# ラベリング信頼度の選択肢
ラベリング精度を検証するのに使用します.下記の3種類から1つ選択してください.
高い,普通,低い
"""


SELECTION_ITEM_DICT = {
    "部門": ["管理部門", "営業部門", "研究部門", "開発部門", "その他", "不明"],
    "業種": ["ブルーカラー", "ホワイトカラー", "不明"],
    "職種": [
        "管理職",
        "専門職",
        "技術職",
        "事務職",
        "販売職",
        "サービス職",
        "クリエイティブ職",
        "教育職",
        "公務員",
        "医療・福祉職",
        "不明",
    ],
    "入社形態": ["新卒", "中途", "不明"],
    "国": ["日本", "アジア", "欧州", "アメリカ", "その他", "不明"],
    "雇用形態": ["正社員", "契約社員", "アルバイト", "派遣社員", "不明"],
}


def create_input_category_messages(json_str: str) -> list[dict[str, str | None]]:
    messages = [
        {
            "role": "system",
            "content": CATEGORY_PROMPT,
        },
        # アウトプット例などを入力する
        # {
        #     "role": "user",
        #     "content": '',
        # },
        # {
        #     "role": "assistant",
        #     "content": "",
        # },
        # 仕様をインプットして, SQLXを生成する
        {
            "role": "user",
            "content": json_str,
        },
    ]
    return messages


def create_input_selection_messages(json_str: str) -> list[dict[str, str | None]]:
    # JSON文字列をPythonの辞書に変換
    data = json.loads(json_str)
    # 'ラベル'の値を取得
    label_value = data["ラベル"]
    select_prompt = get_select_prompt(select_items=SELECTION_ITEM_DICT[label_value])
    messages = [
        {
            "role": "system",
            "content": select_prompt,
        },
        # アウトプット例などを入力する
        # {
        #     "role": "user",
        #     "content": '',
        # },
        # {
        #     "role": "assistant",
        #     "content": "",
        # },
        # 仕様をインプットして, SQLXを生成する
        {
            "role": "user",
            "content": json_str,
        },
    ]
    return messages
