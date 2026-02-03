# 🚀 OmniSorter スタンドアロン版 セットアップガイド

このガイドに従って、ローカルテスト、GitHub公開、Streamlit Cloudデプロイを行ってください。

---

## 📍 現在の状態

- ✅ プロジェクト場所: `c:\omnisorter-standalone\`
- ✅ 独立したGitリポジトリとして初期化済み
- ✅ 初回コミット完了（ブランチ: `main`）
- ✅ セキュリティリスクなし（APIキー・パスワード除去済み）
- ✅ Python 3.12 対応版にアップデート完了
- ✅ 依存パッケージインストール完了

---

## ステップ1: ローカル環境でテスト 🧪

### 1-1. 仮想環境の作成と有効化

**重要:** このプロジェクトは Python 3.12 が必要です。

```bash
# プロジェクトディレクトリに移動
cd c:\omnisorter-standalone

# 仮想環境を作成（Python 3.12を使用）
py -3.12 -m venv venv

# 仮想環境を有効化（Windows）
venv\Scripts\activate

# 仮想環境を有効化（PowerShell）
.\venv\Scripts\Activate.ps1

# 仮想環境を有効化（macOS/Linux）
source venv/bin/activate
```

### 1-2. 依存パッケージのインストール

```bash
# requirements.txtから一括インストール
# （仮想環境を有効化している場合）
pip install -r requirements.txt

# または、仮想環境なしで Python 3.12 を直接使用する場合
py -3.12 -m pip install -r requirements.txt

# インストール確認
pip list
```

**期待される出力（Python 3.12 対応版）:**
```
streamlit>=1.30.0
pandas>=2.0.3
numpy>=1.26.0
plotly>=5.17.0
```

### 1-3. アプリケーションの起動

```bash
# Streamlitアプリを起動（仮想環境を有効化している場合）
streamlit run app.py

# または、Python 3.12 を直接使用する場合
py -3.12 -m streamlit run app.py
```

**期待される動作:**
- ブラウザが自動で開く（http://localhost:8501）
- OmniSorter試算ツールの画面が表示される
- エラーなく動作する

### 1-4. 動作確認テスト

#### テストシナリオ1: 基本的な計算

1. 基本情報を入力:
   - 会社名: 任意
   - 業界: EC・通販
   - 事業形態: B2C

2. 運用条件を入力:
   - 日次出荷件数: `100`
   - 平均ピース数/件: `2.5`
   - 作業時間/日: `8`

3. 商品仕様を入力:
   - 長さ: `300` mm
   - 幅: `200` mm
   - 高さ: `150` mm
   - 重量: `1.5` kg

4. 「🚀 仕様計算を実行」ボタンをクリック

**期待される結果:**
- ✅ 推奨機種が表示される
- ✅ 処理能力・稼働率が表示される
- ✅ 間口構成グラフが表示される
- ✅ 代替機種案が表示される

#### テストシナリオ2: 大規模施設

- 日次出荷件数: `2000`
- 平均ピース数/件: `5.0`
- 商品: 500×400×180mm, 3kg

**期待:** OmniSorter M/L または複数台構成が提案される

### 1-5. 問い合わせフォームのテスト（任意）

**注意:** メール送信をテストする場合は、先に `.streamlit/secrets.toml` を設定する必要があります（ステップ2参照）。

---

## ステップ2: メール送信設定（任意）⚙️

問い合わせフォームからメールを送信する場合のみ必要です。

### 2-1. secrets.tomlファイルの作成

```bash
# サンプルファイルをコピー
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# エディタで編集
code .streamlit/secrets.toml
```

### 2-2. SMTP設定を記入

`.streamlit/secrets.toml` に以下を記入:

```toml
[smtp]
host = "smtp.gmail.com"
port = 587
username = "your-email@gmail.com"
password = "your-app-password"
from_email = "noreply@bridgetown-eng.co.jp"
to_email = "sales@bridgetown-eng.co.jp"
```

### 2-3. Gmail App Passwordの取得（Gmail使用の場合）

1. Googleアカウントの2段階認証を有効化
   - https://myaccount.google.com/security

2. アプリパスワードを生成
   - https://myaccount.google.com/apppasswords
   - アプリを選択: "メール"
   - デバイスを選択: "その他（カスタム名）" → "OmniSorter"
   - 「生成」をクリック

3. 生成された16桁のパスワードを `secrets.toml` の `password` に記入

### 2-4. メール送信テスト

1. アプリを再起動:
   ```bash
   streamlit run app.py
   ```

2. ページ下部の問い合わせフォームに入力して送信

3. 設定したメールアドレスに届くことを確認

---

## ステップ3: GitHubに公開 🐙

### 3-1. GitHub上で新しいリポジトリを作成

1. https://github.com/new にアクセス

2. リポジトリ情報を入力:
   - **Repository name:** `omnisorter-standalone`
   - **Description:** `OmniSorter機種選定・仕様試算ツール（スタンドアロン版）`
   - **Visibility:**
     - `Public` - 一般公開する場合
     - `Private` - 非公開にする場合

3. **重要:** 以下のチェックは全て外す
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license

   （既にローカルでコミット済みのため）

4. 「Create repository」をクリック

### 3-2. リモートリポジトリの追加とプッシュ

GitHubでリポジトリを作成すると表示されるコマンドを実行:

```bash
cd c:\omnisorter-standalone

# リモートリポジトリを追加
# 【重要】YOUR_ORG を実際の組織名/ユーザー名に変更してください
git remote add origin https://github.com/YOUR_ORG/omnisorter-standalone.git

# リモートの確認
git remote -v

# プッシュ
git push -u origin main
```

**期待される出力:**
```
Enumerating objects: 13, done.
Counting objects: 100% (13/13), done.
...
To https://github.com/YOUR_ORG/omnisorter-standalone.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

### 3-3. GitHubで確認

https://github.com/YOUR_ORG/omnisorter-standalone にアクセスして、以下を確認:

- ✅ README.mdが表示される
- ✅ 10個のファイルがコミットされている
- ✅ .envファイルが含まれていない（セキュリティ）
- ✅ secrets.tomlが含まれていない（セキュリティ）

---

## ステップ4: Streamlit Cloudにデプロイ ☁️

### 4-1. Streamlit Cloudにログイン

1. https://share.streamlit.io にアクセス

2. 「Sign in」をクリック

3. GitHubアカウントでログイン

4. Streamlitに必要な権限を付与

### 4-2. 新しいアプリをデプロイ

1. 「New app」ボタンをクリック

2. デプロイ設定を入力:
   - **Repository:** `YOUR_ORG/omnisorter-standalone`
   - **Branch:** `main`
   - **Main file path:** `app.py`

3. 「Advanced settings」をクリック（メール送信機能を使う場合のみ）

### 4-3. Secretsの設定（メール送信機能を使う場合のみ）

「Advanced settings」→「Secrets」に以下を入力:

```toml
[smtp]
host = "smtp.gmail.com"
port = 587
username = "your-email@gmail.com"
password = "your-app-password"
from_email = "noreply@bridgetown-eng.co.jp"
to_email = "sales@bridgetown-eng.co.jp"
```

**重要:** Gmail App Passwordを使用してください（通常のパスワードは動作しません）

### 4-4. デプロイ実行

1. 「Deploy!」ボタンをクリック

2. デプロイ進行状況を確認
   - ビルドログが表示される
   - 依存パッケージがインストールされる
   - アプリが起動する

3. デプロイ完了後、アプリのURLが表示される
   - 例: `https://your-app-name.streamlit.app`

### 4-5. デプロイ後の確認

1. アプリのURLにアクセス

2. 動作確認:
   - ✅ ページが正常に表示される
   - ✅ 計算機能が動作する
   - ✅ グラフが表示される
   - ✅ 問い合わせフォームが表示される

3. 本番環境でのテスト実行

---

## ステップ5: セキュリティ最終確認 🔒

### 5-1. ローカルでの確認

```bash
cd c:\omnisorter-standalone

# APIキーが含まれていないか確認
grep -r "sk-proj-" . || echo "✅ No API keys found"

# 機密情報が含まれていないか確認
grep -r "api_key\s*=" . --include="*.py" | grep -v "secrets" || echo "✅ Clean"
```

**期待される出力:**
```
✅ No API keys found
✅ Clean
```

### 5-2. GitHubでの確認

https://github.com/YOUR_ORG/omnisorter-standalone で確認:

- ✅ `.env` ファイルがコミットされていない
- ✅ `.streamlit/secrets.toml` がコミットされていない
- ✅ `__pycache__/` がコミットされていない
- ✅ `.gitignore` が正しく設定されている

### 5-3. Git履歴の確認

```bash
# コミット履歴を確認
git log --all --full-history -- ".env"
git log -S "sk-proj-" --all

# 何も出力されなければOK
```

---

## トラブルシューティング 🔧

### 問題1: Python と pip のバージョン不一致

**原因:** `python` コマンドと `pip` コマンドが異なるバージョンを指している

**確認方法:**
```bash
python --version
pip --version
```

**解決:**
Python 3.12 を使用することを推奨します。
```bash
# Python 3.12 を直接使用
py -3.12 -m pip install -r requirements.txt
py -3.12 -m streamlit run app.py
```

### 問題2: numpy インストールエラー（`AttributeError: module 'pkgutil' has no attribute 'ImpImporter'`）

**原因:** 古いバージョンの numpy が Python 3.12 と互換性がない

**解決:**
```bash
# requirements.txt が更新されていることを確認
# numpy>=1.26.0 が必要
py -3.12 -m pip install --upgrade -r requirements.txt
```

### 問題3: `streamlit: command not found`

**原因:** Streamlitがインストールされていない

**解決:**
```bash
pip install streamlit
# または
py -3.12 -m pip install streamlit
```

### 問題4: `ModuleNotFoundError: No module named 'src'`

**原因:** Pythonパスが正しく設定されていない

**解決:**
```bash
# プロジェクトルートから実行していることを確認
cd c:\omnisorter-standalone
streamlit run app.py
```

### 問題5: メール送信が失敗する

**原因1:** `.streamlit/secrets.toml` が存在しない

**解決:**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.tomlを編集
```

**原因2:** Gmail App Passwordが正しくない

**解決:**
- 2段階認証が有効化されているか確認
- 新しいApp Passwordを生成
- スペースを含めずに16桁のパスワードを入力

**原因3:** SMTPポートがブロックされている

**解決:**
- ポート587が開いているか確認
- ファイアウォール設定を確認

### 問題6: Streamlit Cloudでデプロイが失敗する

**原因1:** `requirements.txt` の依存関係エラー

**解決:**
- ローカルで `pip install -r requirements.txt` が成功するか確認
- エラーログを確認してパッケージバージョンを調整

**原因2:** Secretsの設定ミス

**解決:**
- Streamlit Cloud の Secrets設定を確認
- TOML形式が正しいか確認（インデント、引用符など）

### 問題7: 計算結果が表示されない

**原因:** `src/omnisorter_common.py` が正しく読み込まれていない

**解決:**
```bash
# ファイルが存在するか確認
ls -la src/omnisorter_common.py

# インポートテスト
python -c "from src.omnisorter_common import get_omnisorter_specs; print('OK')"
```

---

## 追加リソース 📚

### ドキュメント

- [README.md](README.md) - プロジェクト概要
- [requirements.txt](requirements.txt) - 依存パッケージ
- [.streamlit/config.toml](.streamlit/config.toml) - Streamlit設定

### 公式ドキュメント

- Streamlit: https://docs.streamlit.io/
- Streamlit Cloud: https://docs.streamlit.io/streamlit-community-cloud
- Plotly: https://plotly.com/python/

### サポート

- GitHub Issues: https://github.com/YOUR_ORG/omnisorter-standalone/issues
- Email: info@bridgetown-eng.co.jp

---

## 次の開発ステップ 🛠️

プロジェクトが正常にデプロイできたら、以下の拡張を検討してください:

### 機能拡張案

1. **Excel/CSVエクスポート機能**
   - 計算結果をダウンロード可能にする
   - 見積書PDFの生成

2. **履歴保存機能**
   - 過去の試算結果を保存
   - 比較機能の追加

3. **多言語対応**
   - 英語版の追加
   - 国際展開を見据えた設計

4. **カスタマイズ機能**
   - 独自の機種スペックの追加
   - 容器タイプのカスタマイズ

5. **分析機能**
   - 利用統計の収集
   - よく使われる構成の分析

### コード改善案

1. **テストの追加**
   - ユニットテスト（pytest）
   - 統合テスト

2. **パフォーマンス最適化**
   - キャッシング機能の追加
   - 計算の高速化

3. **エラーハンドリングの強化**
   - より詳細なエラーメッセージ
   - ユーザーフレンドリーなエラー表示

---

## チェックリスト ✅

デプロイ前に以下を確認してください:

### ローカル環境

- [ ] 仮想環境を作成した
- [ ] 依存パッケージをインストールした
- [ ] `streamlit run app.py` でアプリが起動する
- [ ] 計算機能が正常に動作する
- [ ] グラフが正しく表示される
- [ ] メール送信機能をテストした（任意）

### セキュリティ

- [ ] `.env` ファイルが含まれていない
- [ ] `secrets.toml` が含まれていない
- [ ] APIキーがコミットされていない
- [ ] パスワードがコミットされていない
- [ ] `.gitignore` が正しく設定されている

### GitHub

- [ ] リポジトリを作成した
- [ ] リモートリポジトリを追加した
- [ ] `git push` が成功した
- [ ] GitHub上でファイルが確認できる
- [ ] README.mdが正しく表示される

### Streamlit Cloud（任意）

- [ ] アプリをデプロイした
- [ ] Secretsを設定した（メール機能使用時）
- [ ] 本番環境で動作確認した
- [ ] URLを関係者に共有した

---

## 完了！🎉

すべてのステップが完了したら、OmniSorterスタンドアロン版が稼働しています！

**公開URL（Streamlit Cloud使用時）:**
- https://your-app-name.streamlit.app

**次のアクション:**
1. 関係者にURLを共有
2. フィードバックを収集
3. 必要に応じて機能を追加・改善

---

**最終更新:** 2025-02-02
**バージョン:** 1.0.0
**作成者:** Bridgetown Engineering Co., Ltd.