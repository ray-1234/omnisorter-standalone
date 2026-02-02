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


def send_inquiry_email(company: str, name: str, email: str, phone: str,
                      inquiry_type: str, message: str) -> bool:
    """
    問い合わせメールを送信

    Args:
        company: 会社名
        name: 氏名
        email: メールアドレス
        phone: 電話番号
        inquiry_type: 問い合わせ種別
        message: 問い合わせ内容

    Returns:
        bool: 送信成功した場合True
    """
    try:
        # Streamlit Secretsから設定を取得
        smtp_config = st.secrets.get("smtp", {})

        if not smtp_config:
            st.warning("⚠️ メール設定が見つかりません。管理者にお問い合わせください。")
            return False

        # メール本文を作成
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

※このメールはOmniSorter簡易試算ツールから自動送信されました
"""

        # メールメッセージを構築
        msg = MIMEMultipart()
        msg['From'] = smtp_config.get('from_email', 'noreply@bridgetown-eng.co.jp')
        msg['To'] = smtp_config.get('to_email', 'sales@bridgetown-eng.co.jp')
        msg['Subject'] = f"[OmniSorter] {inquiry_type} - {company}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # SMTP経由で送信
        with smtplib.SMTP(smtp_config['host'], int(smtp_config['port'])) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)

        return True

    except KeyError as e:
        st.error(f"❌ メール設定が不完全です: {e}")
        return False
    except Exception as e:
        st.error(f"❌ メール送信に失敗しました: {e}")
        return False


def render_contact_form():
    """
    問い合わせフォームを表示
    """
    st.markdown("""
    ### 📧 お問い合わせフォーム
    OmniSorterに関するご質問・お見積り依頼はこちらから承ります。
    お気軽にお問い合わせください。
    """)

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
                placeholder="例：tanaka@example.com"
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
                        inquiry_type, message
                    ):
                        st.success("✅ お問い合わせを送信しました！")
                        st.balloons()
                        st.info("📞 3営業日以内に担当者よりご連絡いたします")
                    else:
                        st.warning("""
                        メール送信機能が設定されていません。
                        下記まで直接ご連絡ください：

                        📧 info@bridgetown-eng.co.jp
                        📞 03-XXXX-XXXX
                        """)

    # 免責事項
    with st.expander("プライバシーポリシー"):
        st.markdown("""
        お預かりした個人情報は、お問い合わせへの対応およびご連絡のみに使用し、
        第三者への提供は行いません。
        """)
