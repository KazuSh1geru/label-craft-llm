PROMPT = """あなたはデータラベリングを行うシステムです。JSONをインプットとして与えます.ルールに従い「ラベル」と「ラベリング信頼度」を選択して出力してください.
"""

CATEGORY_RULES = """
# 命令
・<属性名>を適切なラベルに分類してください.
・<属性名>に対して適切なラベリング信頼度を選択してください.
・背景情報として、<属性グループ名>,<業界大分類>,<業界中分類>,<業界小分類>を参照してください.
・出力は、id,属性名,属性グループ名,ラベル,ラベリング信頼度を含むカンマ区切りで出力してください.
・末尾は改行してください.

# ラベルの選択肢
下記の6種類から1つ選択してください.
部門,業種,職種,入社形態,国,雇用形態

# ラベリング信頼度の選択肢
ラベリング精度を検証するのに使用します.下記の3種類から1つ選択してください.
高い,普通,低い
"""

CATEGORY_PROMPT = f"""{PROMPT}
{CATEGORY_RULES}
"""


def create_input_messages(json_str: str) -> list[dict[str, str | None]]:
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
