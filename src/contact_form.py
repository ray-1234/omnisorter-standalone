"""
お問い合わせフォームモジュール

OmniSorter製品に関する問い合わせを受け付けるフォーム
"""

import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re


def validate_email(email: str) -> bool:
    """
    メールアドレスの形式を検証

    Args:
        email: 検証するメールアドレス

    Returns:
        bool: 有効な形式の場合True
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_number(value, default='N/A'):
    """数値を安全にフォーマット（カンマ区切り）"""
    if value is None:
        return default
    try:
        return f"{value:,.0f}"
    except (ValueError, TypeError):
        return str(value) if value else default


def format_calculation_data(params: dict, result: dict) -> str:
    """
    計算結果をメール本文用にフォーマット

    Args:
        params: 入力パラメータ
        result: 計算結果

    Returns:
        フォーマットされた文字列
    """
    if not params or not result:
        return ""

    lines = []
    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("【試算入力条件】")
    lines.append(f"  日次出荷件数: {format_number(params.get('daily_orders'))} 件/日")
    lines.append(f"  平均ピース数/件: {params.get('pieces_per_order', 'N/A')} pcs")
    lines.append(f"  作業時間: {params.get('working_hours', 'N/A')} 時間/日")
    lines.append(f"  ピーク倍率: {params.get('peak_ratio', 'N/A')} 倍")
    lines.append(f"  商品サイズ(L×W×H): {params.get('product_length', 'N/A')} × {params.get('product_width', 'N/A')} × {params.get('product_height', 'N/A')} mm")
    lines.append(f"  商品重量: {params.get('product_weight', 'N/A')} kg")
    lines.append(f"  容器タイプ: {params.get('container_type', 'N/A')}")

    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("【試算結果】")

    # 推奨機種情報
    if 'selected_model' in result and result['selected_model']:
        model = result['selected_model']
        spec = model.get('spec', {})
        lines.append(f"  推奨機種: {spec.get('name', 'N/A')}")
        lines.append(f"  必要台数: {result.get('recommended_units', 'N/A')} 台")
        lines.append(f"  ブロック数: {result.get('num_blocks', 'N/A')} ブロック/台")
        lines.append(f"  間口数: {result.get('num_intervals', 'N/A')} 間口/台")
        lines.append(f"  処理能力: {format_number(result.get('actual_capacity'))} pcs/時")

    # 日次処理量
    if 'daily_pieces' in result:
        lines.append(f"  日次処理量: {format_number(result.get('daily_pieces'))} pcs/日")

    # 必要処理能力
    if 'required_capacity_per_hour' in result:
        lines.append(f"  必要処理能力: {format_number(result.get('required_capacity_per_hour'))} pcs/時")

    # 稼働率
    if 'capacity_utilization' in result:
        lines.append(f"  稼働率: {result.get('capacity_utilization', 0):.1f}%")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


def send_confirmation_email(name: str, email: str, company: str,
                           inquiry_type: str, message: str,
                           params: dict = None, result: dict = None) -> bool:
    """
    問い合わせ者への確認メールを送信

    Args:
        name: 氏名
        email: 送信先メールアドレス
        company: 会社名
        inquiry_type: 問い合わせ種別
        message: 問い合わせ内容
        params: 試算入力パラメータ（オプション）
        result: 試算結果（オプション）

    Returns:
        bool: 送信成功した場合True
    """
    try:
        smtp_config = st.secrets.get("smtp", {})
        if not smtp_config:
            return False

        # 計算データのフォーマット
        calculation_section = format_calculation_data(params, result)

        # 確認メール本文
        body = f"""{name} 様

このたびはOmniSorterに関するお問い合わせをいただき、
誠にありがとうございます。

以下の内容でお問い合わせを承りました。
担当者より3営業日以内にご連絡させていただきます。

━━━━━━━━━━━━━━━━━━━━━━
【お問い合わせ内容】
━━━━━━━━━━━━━━━━━━━━━━
会社名: {company}
お名前: {name}
問い合わせ種別: {inquiry_type}

■ ご記入内容
{message}
{calculation_section}
━━━━━━━━━━━━━━━━━━━━━━

ご不明な点がございましたら、お気軽にご連絡ください。

━━━━━━━━━━━━━━━━━━━━━━
署名
━━━━━━━━━━━━━━━━━━━━━━

※このメールは自動送信されています。
※心当たりのない場合は、お手数ですが本メールを破棄してください。
"""

        msg = MIMEMultipart()
        msg['From'] = smtp_config.get('from_email')
        msg['To'] = email
        msg['Subject'] = f"【OmniSorter】お問い合わせありがとうございます（{inquiry_type}）"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP(smtp_config['host'], int(smtp_config['port'])) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)

        return True

    except Exception:
        # 確認メール送信失敗は致命的エラーではないため、静かに失敗
        return False


def send_inquiry_email(company: str, name: str, email: str, phone: str,
                      inquiry_type: str, message: str,
                      params: dict = None, result: dict = None) -> bool:
    """
    問い合わせメールを送信（社内向け + 問い合わせ者への確認メール）

    Args:
        company: 会社名
        name: 氏名
        email: メールアドレス
        phone: 電話番号
        inquiry_type: 問い合わせ種別
        message: 問い合わせ内容
        params: 試算入力パラメータ（オプション）
        result: 試算結果（オプション）

    Returns:
        bool: 送信成功した場合True
    """
    try:
        # Streamlit Secretsから設定を取得
        smtp_config = st.secrets.get("smtp", {})

        if not smtp_config:
            st.warning("⚠️ メール設定が見つかりません。管理者にお問い合わせください。")
            return False

        # 計算データのフォーマット
        calculation_section = format_calculation_data(params, result)

        # メール本文を作成（社内向け）
        body = f"""
新規お問い合わせがありました

━━━━━━━━━━━━━━━━━━━━━━
【会社名】
{company}

【お名前】
{name}

【メールアドレス】
{email}

【電話番号】
{phone or '未入力'}

【問い合わせ種別】
{inquiry_type}

【お問い合わせ内容】
{message}
━━━━━━━━━━━━━━━━━━━━━━
{calculation_section}

※このメールはOmniSorter簡易試算ツールから自動送信されました
"""

        # メールメッセージを構築
        msg = MIMEMultipart()
        msg['From'] = smtp_config.get('from_email', 'noreply@bridgetown-eng.co.jp')
        msg['To'] = smtp_config.get('to_email', 'sales@bridgetown-eng.co.jp')
        msg['Subject'] = f"[OmniSorter] {inquiry_type} - {company}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # SMTP経由で送信（社内向け）
        with smtplib.SMTP(smtp_config['host'], int(smtp_config['port'])) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)

        # 問い合わせ者への確認メールを送信
        send_confirmation_email(
            name=name,
            email=email,
            company=company,
            inquiry_type=inquiry_type,
            message=message,
            params=params,
            result=result
        )

        return True

    except KeyError as e:
        st.error(f"❌ メール設定が不完全です: {e}")
        return False
    except Exception as e:
        st.error(f"❌ メール送信に失敗しました: {e}")
        return False


def render_contact_form(params: dict = None, result: dict = None):
    """
    問い合わせフォームを表示

    Args:
        params: 試算入力パラメータ（オプション）
        result: 試算結果（オプション）
    """
    st.markdown("""
    ### 📧 お問い合わせフォーム
    OmniSorterに関するご質問・お見積り依頼はこちらから承ります。
    お気軽にお問い合わせください。
    """)

    # 試算結果がある場合は表示
    if params and result:
        st.info("💡 試算結果が入力されています。お問い合わせ時に自動で送信されます。")

    with st.form("contact_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input(
                "会社名 *",
                placeholder="例：株式会社サンプル"
            )
            name = st.text_input(
                "お名前 *",
                placeholder="例：山田 太郎"
            )
            email = st.text_input(
                "メールアドレス *",
                placeholder="例：yamada@example.com"
            )

        with col2:
            phone = st.text_input(
                "電話番号",
                placeholder="例：03-1234-5678"
            )
            inquiry_type = st.selectbox(
                "お問い合わせ種別 *",
                [
                    "製品資料請求",
                    "お見積り依頼",
                    "デモ見学希望",
                    "導入相談",
                    "技術的な質問",
                    "その他"
                ]
            )

        message = st.text_area(
            "お問い合わせ内容 *",
            placeholder="お問い合わせ内容を詳しくご記入ください",
            height=150
        )

        st.caption("* 必須項目")

        # 送信ボタン
        submitted = st.form_submit_button("📤 送信", type="primary", use_container_width=True)

        if submitted:
            # バリデーション
            if not all([company_name, name, email, message]):
                st.error("❌ 必須項目（*）をすべて入力してください")
            elif not validate_email(email):
                st.error("❌ 有効なメールアドレスを入力してください")
            else:
                # メール送信
                with st.spinner("送信中..."):
                    if send_inquiry_email(
                        company_name, name, email, phone,
                        inquiry_type, message,
                        params=params, result=result
                    ):
                        st.success("✅ お問い合わせを送信しました！")
                        st.balloons()
                        st.markdown(f"""
                        **ご入力いただいたメールアドレス（{email}）に確認メールをお送りしました。**

                        3営業日以内に担当者よりご連絡いたします。

                        ---
                        **確認メールが届かない場合：**
                        - 迷惑メールフォルダをご確認ください
                        - メールアドレスに誤りがないかご確認ください
                        - 上記でも届かない場合は、お手数ですが下記までご連絡ください

                        📧 info@bridgetown-eng.co.jp
                        """)
                    else:
                        st.warning("""
                        メール送信機能が設定されていません。
                        下記まで直接ご連絡ください：

                        📧 info@bridgetown-eng.co.jp
                        📞 03-XXXX-XXXX
                        """)

    # プライバシーポリシー
    with st.expander("プライバシーポリシー"):
        st.markdown("""
        **個人情報の取り扱いについて**

        当社は、お客様からお預かりした個人情報を以下の方針に基づき適切に管理いたします。

        **1. 利用目的**
        お預かりした個人情報は、以下の目的にのみ使用いたします。
        - お問い合わせへの回答およびご連絡
        - 製品・サービスに関する情報提供
        - お見積り・ご提案書の作成・送付

        **2. 第三者への提供**
        お客様の同意なく、個人情報を第三者に提供することはありません。
        ただし、法令に基づく場合を除きます。

        **3. 安全管理**
        個人情報への不正アクセス、紛失、改ざん、漏洩を防止するため、
        適切なセキュリティ対策を実施しております。

        **4. 開示・訂正・削除**
        ご本人からの個人情報の開示・訂正・削除のご要望には、
        合理的な範囲で速やかに対応いたします。

        **5. お問い合わせ窓口**
        個人情報の取り扱いに関するお問い合わせは、下記までご連絡ください。
        📧 info@bridgetown-eng.co.jp
        """)
