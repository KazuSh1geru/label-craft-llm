COMMON_PROMPT = "加工の仕様をインプットとして与えます.ルールに従って「考慮した仕様のコメント」と「SQLのfield,列名」を出力してください.構文はBigQuerySQLです."

COMMON_RULES = """・SQLの末尾に改行コードを入れる.
・<移行不要>がtrueの時は、空文字""を出力.
"""

CONVERT_PROMPT = f"""{COMMON_PROMPT}
#命令
・マスキング, 列名の変更をしてください.
・CASTはINT64, FLOAT64, TIMESTAMP, DATEの場合に使用してください.（それ以外はデータ型変換をしない.）
・ルールに従って、コメントを生成してください.

# CASTの規則
<データ型"数値"の場合>
仕様の<文字数(整数、小数)>を元にCASTを行ってください.
・INT64 数値(整数, 0)
・FLOAT64 数値(整数, 整数)
<データ型"通貨"の場合>
INT64でCASTする

#ルール
{COMMON_RULES}
・SQLは基本的に`<元データ:API参照名> as <API参照名>`とする.
・<API参照名>と<元データ:API参照名>が異なる場合、コメントに "API名変更あり"を出力.
・<加工要件概要>がある場合は、1.コメントで"加工要件あり"を出力 2.SQLのフィールド参照を`cs.<API参照名>`とする.
  マスクなし例: `cs.<API参照名>`
  マスクあり例: `IF(cs.<API参照名> IS NULL, NULL, ${{when(... `cs.<API参照名>`)}})`
・<元データ:API参照名>が空または"-"の場合、コメントに"API参照名なし"と出力.
・<元データ:API参照名>が複数ある場合, コメントに"API参照名複数あり(<元データ:API参照名>,)"と出力.
"""

CUSTOMIZE_PROMPT = f"""{COMMON_PROMPT}
#ルール
・SQLは`<元データ:API参照名> as <API参照名>`とする.
・コメントで"TODO: 加工要件を要確認"を出力.
{COMMON_RULES}
・<API参照名>と<元データ:API参照名>が異なる場合、コメントに "API名変更あり"を出力.
・<元データ:API参照名>が空または"-"の場合、1.コメントに"API参照名なし"と出力. 2.SQLを`'' as <API参照名>`とする.
・<元データ:API参照名>が複数ある場合,1.コメントに"API参照名複数あり(<元データ:API参照名>,)"と出力. 2.SQLを`最初の<元データ:API参照名> as <API参照名>`とする.
"""


def create_input_messages(json_str: str) -> list[dict[str, str | None]]:
    messages = [
        {
            "role": "system",
            "content": CONVERT_PROMPT,
        },
        # 変換なし
        {
            "role": "user",
            "content": '{"項目表示ラベル":"キャンペーン ID","API参照名":"CampaignId","データ型":"参照関係","文字数":null,"関連先":"キャンペーン","元データ:API参照名":"CampaignId","移行不要":false,"加工要件概要":null,"マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- キャンペーン ID: 参照関係(キャンペーン), マスクなし\nCampaignId AS CampaignId,\n",
        },
        # 変換なし, マスクなし
        {
            "role": "user",
            "content": '{"項目表示ラベル":"削除","API参照名":"IsDeleted","データ型":"チェックボックス","文字数":null,"関連先":null,"元データ:API参照名":"IsDeleted","移行不要":false,"加工要件概要":null,"マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- 削除: チェックボックス, マスクなし\nIsDeleted AS IsDeleted,\n",
        },
        # CAST: タイムスタンプ
        {
            "role": "user",
            "content": r'{"項目表示ラベル":"最終更新日","API参照名":"LastModifiedDate","データ型":"日付\/時間","文字数":null,"関連先":null,"元データ:API参照名":"LastModifiedDate","移行不要":false,"加工要件概要":null,"マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- 最終更新日: 日付/時間, マスクなし\nCAST(LastModifiedDate AS TIMESTAMP) AS LastModifiedDate,\n",
        },
        # CAST: DATE
        {
            "role": "user",
            "content": '{"項目表示ラベル":"最終移行日","API参照名":"LastTransferDate","データ型":"日付","文字数":null,"選択リスト値(選択リストの場合)":null,"関連先":null,"元データ:API参照名":"LastTransferDate","移行不要":false,"備考（手動）":"OK","加工要件概要":"なし","加工要件詳細":null,"加工要件備考":null,"マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- 最終移行日: 日付, マスクなし\nCAST(LastTransferDate AS DATE) AS LastTransferDate,\n",
        },
        # 数値: FLOAT
        {
            "role": "user",
            "content": '{"項目表示ラベル":"緯度","API参照名":"Latitude","データ型":"数値","文字数":"18 (3, 15)","関連先":null,"元データ:API参照名":"Latitude","移行不要":false,"加工要件概要":"なし","マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- 緯度: 数値(FLOAT), マスクなし\nCAST(Latitude AS FLOAT64) AS Latitude,\n",
        },
        # 数値: INT
        {
            "role": "user",
            "content": '{"項目表示ラベル":"NPSスコア","API参照名":"LMI_NPS_Score__c","データ型":"数値","文字数":"2 (2, 0)","関連先":null,"元データ:API参照名":"LMI_NPS_score__c","移行不要":false,"加工要件概要":null,"マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- NPSスコア: 数値(INT), マスクなし\nCAST(LMI_NPS_Score__c as INT64) as LMI_NPS_Score__c,\n",
        },
        # 通貨
        {
            "role": "user",
            "content": '{"項目表示ラベル":"年間売上","API参照名":"AnnualRevenue","データ型":"通貨","文字数":null,"関連先":null,"元データ:API参照名":"AnnualRevenue","移行不要":false,"加工要件概要":"なし","マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- 年間売上: 通貨, マスクなし\nCAST(AnnualRevenue as INT64) AS AnnualRevenue,\n",
        },
        # ロングテキスト: マスクあり
        {
            "role": "user",
            "content": '{"項目表示ラベル":"説明","API参照名":"Description","データ型":"ロングテキストエリア","文字数":"32000","関連先":null,"元データ:API参照名":"Description","移行不要":false,"加工要件概要":null,"マスキング有無":true}',
        },
        {
            "role": "assistant",
            "content": '-- 説明: ロングテキストエリア, マスクあり\nIF(Description IS NULL, NULL,\n  ${\n    when(\n      dataform.projectConfivars.maskData === "true",\n      `${constants.MASK_STR_VAL}`,\n      `Description`\n    )\n  }\n  ) AS `Description`,\n',
        },
        # メール: マスクあり
        {
            "role": "user",
            "content": '{"項目表示ラベル":"メール","API参照名":"Email","データ型":"メール","文字数":null,"関連先":null,"元データ:API参照名":"Email","移行不要":false,"加工要件概要":null,"マスキング有無":true}',
        },
        {
            "role": "assistant",
            "content": '-- メール: メール, マスクあり\nIF(Email IS NULL, NULL,\n  ${\n    when(\n      dataform.projectConfig.vars.env === "dev",\n      `${constants.MASK_STR_VAL}`,\n      `Email`\n    )\n  }\n  ) AS `Email`,\n',
        },
        # 電話: マスクあり
        {
            "role": "user",
            "content": '{"項目表示ラベル":"携帯電話","API参照名":"MobilePhone","データ型":"電話","文字数":"40","関連先":null,"元データ:API参照名":"MobilePhone\nMobileNumber__c  ","移行不要":false,"備考（手動）":"OK\n両方クエリ取得OK","加工要件概要":"その他","マスキング有無":true}',
        },
        {
            "role": "assistant",
            "content": '-- 携帯電話: 電話, マスクあり\n-- API参照名複数あり\n-- 加工要件あり\nIF(cs.MobilePhone IS NULL, NULL,\n  ${\n    when(\n      dataform.projectConfig.vars.env === "dev",\n      `${constants.MASK_STR_VAL}`,\n      `cs.MobilePhone`\n    )\n  }\n  ) AS `MobilePhone`,\n',
        },
        # 数値(INT): マスクあり
        {
            "role": "user",
            "content": '{"項目表示ラベル":"名寄せ用_法人番号","API参照名":"hojin_no__c","データ型":"数値","文字数":"13 (13, 0)","関連先":null,"元データ:API参照名":"hojin_no__c","移行不要":false,"加工要件概要":"なし","マスキング有無":true}',
        },
        {
            "role": "assistant",
            "content": '-- 名寄せ用_法人番号: 数値(INT), マスクあり\nIF(hojin_no__c IS NULL, NULL,\n  ${\n    when(\n      dataform.projectConfig.vars.env === "dev",\n      `${constants.MASK_NUM_VAL}`,\n      `hojin_no__c`\n    )\n  }\n  ) AS `hojin_no__c`,\n',
        },
        # 加工要件なし: API名変更あり
        {
            "role": "user",
            "content": '{"項目表示ラベル":"メール案内を見て_クラウド","API参照名":"LMI_MailMagazine__c","データ型":"チェックボックス","文字数":null,"関連先":null,"元データ:API参照名":"LMI_mail_magazine__c","移行不要":false,"加工要件概要":null,"マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- メール案内を見て_クラウド: チェックボックス, マスクなし\n-- API名変更あり\nLMI_Mail_magazine__c AS LMI_MailMagazine__c,\n",
        },
        # 加工要件あり: 選択リスト
        {
            "role": "user",
            "content": '{"項目表示ラベル":"状況","API参照名":"Status","データ型":"選択リスト","文字数":null,"関連先":null,"元データ:API参照名":"Status","移行不要":false,"加工要件概要":"値の変更","マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- 状況: 選択リスト, マスクなし\n-- 加工要件あり\ncs.Status AS `Status`,\n",
        },
        # 加工要件あり: 参照関係
        {
            "role": "user",
            "content": '{"項目表示ラベル":"作成者 ID","API参照名":"CreatedById","データ型":"参照関係","文字数":null,"関連先":"ユーザー","元データ:API参照名":"CreatedById","移行不要":false,"加工要件概要":"値の変更","マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- 作成者 ID: 参照関係(ユーザー), マスクなし\n-- 加工要件あり\ncs.CreatedById AS CreatedById,\n",
        },
        # API参照名なし
        {
            "role": "user",
            "content": '{"項目表示ラベル":"限定利用可能法人","API参照名":"LimitedUsableCompany__c","データ型":"選択リスト (複数選択)","文字数":null,"関連先":null,"元データ:API参照名":"-","移行不要":false,"加工要件概要":"その他","マスキング有無":false}',
        },
        {
            "role": "assistant",
            "content": "-- 限定利用可能法人: 選択リスト (複数選択), マスクなし\n-- 加工要件あり\n-- API参照名なし\n-- cs.LimitedUsableCompany__c AS LimitedUsableCompany__c,\n",
        },
        # 加工要件あり: API参照複数あり
        {
            "role": "user",
            "content": '{"項目表示ラベル":"担当者情報","API参照名":"StaffInfo__c","データ型":"ロングテキストエリア","文字数":"32768","関連先":null,"元データ:API参照名":"LEI_StaffRemarks__c \nLEI_ISMemo__c       \nLastName_Kana__c\nFirstNameKana__c","移行不要":false,"備考（手動）":"OK\n4項目ともクエリ取得可能","加工要件概要":"その他","マスキング有無":true}',
        },
        {
            "role": "assistant",
            "content": '-- 担当者情報: ロングテキストエリア, マスクあり\n-- 加工要件あり\n-- API参照名複数あり(Field14__c,LMI_StaffRemarks__c,LMI_NumberOfEmployees__c,kuremu__c)\n-- API名変更あり\nIF(cs.StaffInfo__c IS NULL, NULL,  ${\n    when(\n      dataform.projectConfig.vars.env === "dev",\n      `${constants.MASK_STR_VAL}`,\n      `cs.StaffInfo__c`\n    )\n  }\n  ) AS `StaffInfo__c`,\n',
        },
        # 仕様をインプットして, SQLXを生成する
        {
            "role": "user",
            "content": json_str,
        },
    ]
    return messages
