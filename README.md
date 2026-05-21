# George V Gold Proof 5 Pounds 1911 - Auction Data Extractor

MHTMLファイルから競売ロット情報を抽出してCSVに変換するPythonスクリプトです。

## 機能

- MHTMLファイルをパース
- 各Lotの以下の情報を抽出：
  - **Auction No.**: 競売番号
  - **Lot No.**: ロット番号
  - **Name**: ロット名称
  - **Service**: 鑑定会社（NGC/PCGS/Uncertified）
  - **Grade**: グレード（PR/MS + 2桁数字）
  - **Auction Ended**: 競売終了日
  - **Sold For**: 落札価格（不成立の場合は該当テキスト）

## セットアップ

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python parse_mhtml.py
```

## 出力

`auction_results.csv` ファイルが生成されます。

## ファイル構成

- `parse_mhtml.py` - メインスクリプト
- `requirements.txt` - 依存パッケージ
- `Search_ Great Britain George V gold Proof 5 Pounds 1911.mhtml` - 入力ファイル
- `auction_results.csv` - 出力ファイル（生成される）

## 環境

- Python 3.7+
- BeautifulSoup4

## 不成立の判定

「Sold For」フィールドに数字（金額）以外の文字列が入っている場合、不成立と判定します。
