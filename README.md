# 🤖 OmniSorter 簡易試算ツール

OmniSorterの機種選定と仕様を簡易的に試算するスタンドアロン版Streamlitアプリです。

## ✨ 機能

- ✅ 日次出荷件数・ピース数からの機種選定
- ✅ 商品サイズ・重量に基づく適合性チェック
- ✅ 間口構成・ブロック数の自動計算
- ✅ 処理能力と稼働率の可視化
- ✅ 代替機種の提案
- ✅ 問い合わせフォーム

## 📁 プロジェクト構成

```
omnisorter-standalone/
├── app.py                          # メインアプリケーション
├── requirements.txt                # 依存パッケージ
├── README.md                       # このファイル
├── .gitignore                      # Git除外設定
├── .streamlit/
│   ├── config.toml                 # Streamlit設定
│   └── secrets.toml.example        # シークレット設定サンプル
├── config/
│   ├── omnisorter_specs.yaml       # 機種仕様設定
│   └── container_model_matrix.yaml # 容器×機種マトリクス
└── src/
    ├── __init__.py
    ├── config_loader.py            # 設定ファイル読み込み
    ├── omnisorter_common.py        # 共通関数
    └── contact_form.py             # 問い合わせフォーム
```

## 🚀 ローカル実行

### 1. 前提条件

- Python 3.12 以上
- pip

### 2. インストール

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_ORG/omnisorter-standalone.git
cd omnisorter-standalone

# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 3. 設定ファイルの作成

```bash
# メール送信設定（任意）
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml を編集してSMTP情報を設定
```

### 4. アプリを起動

```bash
streamlit run app.py
```

ブラウザで http://localhost:8501 が自動的に開きます。

## ⚙️ 設定

### メール送信設定（任意）

問い合わせフォームからメールを送信する場合は、`.streamlit/secrets.toml` を作成してSMTP設定を記入してください。

```toml
[smtp]
host = "smtp.gmail.com"
port = 587
username = "your-email@gmail.com"
password = "your-app-password"
from_email = "noreply@bridgetown-eng.co.jp"
to_email = "sales@bridgetown-eng.co.jp"
```

**Gmail App Passwordの取得方法:**
1. Googleアカウントの2段階認証を有効化
2. https://myaccount.google.com/apppasswords でアプリパスワードを生成
3. 生成されたパスワードを `password` に設定

## 🌐 Streamlit Cloud デプロイ

### 1. GitHubにプッシュ

```bash
git init
git add .
git commit -m "Initial commit: OmniSorter standalone"
git remote add origin https://github.com/YOUR_ORG/omnisorter-standalone.git
git push -u origin main
```

### 2. Streamlit Cloudでデプロイ

1. https://share.streamlit.io にアクセス
2. "New app" をクリック
3. リポジトリを選択: `YOUR_ORG/omnisorter-standalone`
4. メインファイル: `app.py`
5. **Advanced settings** → **Secrets** に以下を設定:

```toml
[smtp]
host = "smtp.gmail.com"
port = 587
username = "your-email@gmail.com"
password = "your-app-password"
from_email = "noreply@bridgetown-eng.co.jp"
to_email = "sales@bridgetown-eng.co.jp"
```

6. "Deploy!" をクリック

## 📝 使い方

### 1. 基本情報を入力
- 会社名、業界、事業形態を選択

### 2. 運用条件を入力
- 日次出荷件数
- 平均ピース数/件
- 作業時間/日

### 3. 商品仕様を入力
- 長さ、幅、高さ (mm)
- 重量 (kg)
- 使用容器タイプ

### 4. 仕様計算を実行
- 「🚀 仕様計算を実行」ボタンをクリック

### 5. 結果を確認
- 推奨機種
- 処理能力と稼働率
- 間口構成
- 代替機種案

### 6. 問い合わせ
- 詳細な見積りやデモ見学は問い合わせフォームから

## 🔧 トラブルシューティング

### アプリが起動しない

```bash
# 依存パッケージを再インストール
pip install --upgrade -r requirements.txt

# Streamlitのバージョン確認
streamlit --version
```

### メール送信が失敗する

- `.streamlit/secrets.toml` の設定を確認
- Gmail App Passwordが正しいか確認
- SMTPポート（587）が開いているか確認

### 計算結果が表示されない

- ブラウザのコンソール（F12）でエラーを確認
- `src/omnisorter_common.py` が正しく配置されているか確認

## 📊 機能詳細

### 機種選定ロジック

1. **物理制約チェック**: 商品サイズ・重量が機種の最大値以内か
2. **容器対応チェック**: 選択した容器タイプに対応しているか
3. **スコア計算**: 以下の要素で総合評価
   - 基本優先度
   - 容器適合度
   - 容量適合度（稼働率60-90%が最適）
   - サイズ効率
   - 処理量に応じた機種選定

### 計算パラメータ

- 処理能力: 1200-1500 pcs/時（標準機）
- 最適稼働率: 60-90%
- 目標回転数: 2.5回/時間
- ブロック上限: 8ブロック

## 📄 ライセンス

© 2025 Bridgetown Engineering Co., Ltd. All rights reserved.

## 📧 お問い合わせ

- Email: info@bridgetown-eng.co.jp
- Website: https://bridgetown-eng.co.jp

---

**⚠️ 注意事項**

この試算は簡易的な目安です。正確な仕様提案には詳細な現地調査が必要です。
実際の導入には、レイアウト、動線、ピッキング方法などの詳細検討が必要です。
