"""
OmniSorter 簡易試算ツール
スタンドアロン版 - データ分析機能を除き、OmniSorter機種選定に特化

Features:
- 日次出荷件数・ピース数からの機種選定
- 商品サイズ・重量に基づく適合性チェック
- 間口構成・ブロック数の自動計算
- 問い合わせフォーム
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

from src.omnisorter_common import (
    initialize_session_state_safely,
    get_default_container_model_matrix,
    get_default_omnisorter_specs,
    get_container_model_config
)
from src.contact_form import render_contact_form


# ページ設定
st.set_page_config(
    page_title="OmniSorter 簡易試算ツール",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def initialize_app():
    """アプリケーションの初期化"""
    initialize_session_state_safely()

    # デフォルト値の設定
    if 'daily_orders' not in st.session_state:
        st.session_state['daily_orders'] = 100
    if 'pieces_per_order' not in st.session_state:
        st.session_state['pieces_per_order'] = 2.5
    if 'working_hours' not in st.session_state:
        st.session_state['working_hours'] = 8
    if 'product_length' not in st.session_state:
        st.session_state['product_length'] = 300
    if 'product_width' not in st.session_state:
        st.session_state['product_width'] = 200
    if 'product_height' not in st.session_state:
        st.session_state['product_height'] = 150
    if 'product_weight' not in st.session_state:
        st.session_state['product_weight'] = 1.5


def render_input_form():
    """入力フォームの表示"""
    st.subheader("📋 作業条件の入力")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 基本情報")
        company_name = st.text_input(
            "会社名",
            placeholder="例：株式会社サンプル"
        )
        industry = st.selectbox(
            "業界",
            ["EC・通販", "小売・卸売", "食品", "アパレル", "医薬品", "製造業", "3PL", "その他"]
        )
        business_type = st.selectbox(
            "事業形態",
            ["B2C（toC）", "B2B（toB）", "B2B2C", "その他"]
        )

        st.markdown("#### 運用条件")
        daily_orders_val = int(st.session_state.get('daily_orders', 100))
        daily_orders_val = max(1, min(50000, daily_orders_val))
        daily_orders = st.number_input(
            "日次出荷件数",
            min_value=1,
            max_value=50000,
            value=daily_orders_val,
            step=10,
            help="1日あたりの出荷件数を入力"
        )

        pieces_val = float(st.session_state.get('pieces_per_order', 2.5))
        pieces_val = max(0.1, min(100.0, pieces_val))
        pieces_per_order = st.number_input(
            "平均ピース数/件",
            min_value=0.1,
            max_value=100.0,
            value=pieces_val,
            step=0.1,
            help="1件あたりの平均商品点数"
        )

        hours_val = float(st.session_state.get('working_hours', 8))
        hours_val = max(1.0, min(24.0, hours_val))
        working_hours = st.number_input(
            "作業時間/日（時間）",
            min_value=1.0,
            max_value=24.0,
            value=hours_val,
            step=1.0,
            help="1日の作業時間"
        )

    with col2:
        st.markdown("#### 商品仕様")

        col2_1, col2_2 = st.columns(2)
        with col2_1:
            length_val = int(st.session_state.get('product_length', 300))
            length_val = max(50, min(1500, length_val))
            product_length = st.number_input(
                "長さ (mm)",
                min_value=50,
                max_value=1500,
                value=length_val,
                step=10,
                help="商品の最大長さ"
            )
            width_val = int(st.session_state.get('product_width', 200))
            width_val = max(50, min(1000, width_val))
            product_width = st.number_input(
                "幅 (mm)",
                min_value=50,
                max_value=1000,
                value=width_val,
                step=10,
                help="商品の最大幅"
            )

        with col2_2:
            height_val = int(st.session_state.get('product_height', 150))
            height_val = max(10, min(600, height_val))
            product_height = st.number_input(
                "高さ (mm)",
                min_value=10,
                max_value=600,
                value=height_val,
                step=10,
                help="商品の最大高さ"
            )
            weight_val = float(st.session_state.get('product_weight', 1.5))
            weight_val = max(0.1, min(30.0, weight_val))
            product_weight = st.number_input(
                "重量 (kg)",
                min_value=0.1,
                max_value=30.0,
                value=weight_val,
                step=0.1,
                help="商品の最大重量"
            )

        container_type = st.selectbox(
            "使用容器タイプ",
            ["標準トート", "オリコン30L", "オリコン40L", "オリコン50L", "不明"]
        )

        st.markdown("#### 追加情報（任意）")
        peak_ratio = st.slider(
            "ピーク倍率",
            min_value=1.0,
            max_value=5.0,
            value=1.5,
            step=0.1,
            help="通常時に対するピーク時の倍率"
        )

    return {
        'company_name': company_name,
        'industry': industry,
        'business_type': business_type,
        'daily_orders': daily_orders,
        'pieces_per_order': pieces_per_order,
        'working_hours': working_hours,
        'product_length': product_length,
        'product_width': product_width,
        'product_height': product_height,
        'product_weight': product_weight,
        'container_type': container_type,
        'peak_ratio': peak_ratio
    }


def calculate_omnisorter_spec(params):
    """OmniSorter仕様の計算"""
    PRODUCT_SPECS = get_default_omnisorter_specs()
    CONTAINER_MODEL_MATRIX = get_default_container_model_matrix()

    # 必要処理能力の計算
    daily_pieces = params['daily_orders'] * params['pieces_per_order']
    required_capacity_per_hour = (daily_pieces / params['working_hours']) * params['peak_ratio']

    # 機種選定ロジック
    selected_model = None
    best_score = -1

    for model_name, spec in PRODUCT_SPECS.items():
        # 物理制約チェック
        max_product = spec.get('maxProduct', {})
        if (params['product_length'] > max_product.get('L', 9999) or
            params['product_width'] > max_product.get('W', 9999) or
            params['product_height'] > max_product.get('H', 9999) or
            params['product_weight'] > max_product.get('weight', 9999)):
            continue

        # 容器対応チェック
        container_config = get_container_model_config(
            params['container_type'],
            model_name,
            CONTAINER_MODEL_MATRIX
        )

        if not container_config or not container_config.get('supported'):
            continue

        # スコア計算
        score = 0
        score += spec.get('priority', 5)  # 基本優先度

        # 容器適合度
        if container_config.get('recommended'):
            score += 20

        # 容量適合度
        capacity_ratio = required_capacity_per_hour / spec.get('processingCapacity', 1200)
        if 0.6 <= capacity_ratio <= 0.9:
            score += 30  # 最適範囲
        elif 0.4 <= capacity_ratio < 0.6:
            score += 20  # 低稼働
        elif capacity_ratio > 1:
            score -= 10  # 能力不足

        # サイズ効率
        max_product = spec.get('maxProduct', {})
        max_area = max_product.get('L', 1) * max_product.get('W', 1)
        if max_area > 0:
            size_ratio = (params['product_length'] * params['product_width']) / max_area
            if size_ratio > 0.5:
                score += 15  # サイズ利用効率が高い

        # 処理量に応じた機種優遇
        if daily_pieces <= 3000:
            if 'mini' in model_name.lower():
                score += 25
        elif daily_pieces <= 8000:
            if model_name in ['S', 'M']:
                score += 20
        else:
            if model_name in ['M', 'L']:
                score += 25

        # 大型商品の場合はM/L型を優遇
        if params['product_length'] > 500 or params['product_weight'] > 3:
            if model_name in ['M', 'L']:
                score += 15

        if score > best_score:
            best_score = score
            selected_model = {
                'name': model_name,
                'spec': spec,
                'container_config': container_config,
                'score': score
            }

    if not selected_model:
        return None

    # 間口・ブロック数の計算
    spec = selected_model['spec']

    if 'mini' in selected_model['name'].lower():
        # mini版は固定構成
        num_intervals = spec.get('unitCapacity', 30)
        num_blocks = 1
    else:
        # 標準機の場合
        required_capacity = required_capacity_per_hour
        processing_time = 3600 / spec.get('processingCapacity', 1200)  # 秒/個
        target_rotation = 2.5  # 目標回転数（時間あたり）

        num_intervals = int(np.ceil(required_capacity * processing_time / (3600 / target_rotation)))
        num_intervals = max(spec.get('minIntervals', 4), min(num_intervals, spec.get('maxIntervals', 32)))

        # ブロック数（8ブロック上限）
        if num_intervals <= 8:
            num_blocks = 1
        elif num_intervals <= 16:
            num_blocks = 2
        elif num_intervals <= 24:
            num_blocks = 3
        else:
            num_blocks = 4

    # 能力評価
    actual_capacity = spec.get('processingCapacity', 1200)
    capacity_utilization = (required_capacity_per_hour / actual_capacity) * 100

    # 容量不足チェック
    if capacity_utilization > 95:
        recommended_units = int(np.ceil(capacity_utilization / 85))
    else:
        recommended_units = 1

    # 設置寸法の計算
    installation_length = spec.get('length', 4000)
    installation_width = spec.get('width', 2000)
    installation_height = spec.get('height', 2000)

    # 代替案の生成（上位3つ）
    alternatives = []
    for model_name, spec_alt in PRODUCT_SPECS.items():
        if model_name == selected_model['name']:
            continue

        # 物理制約チェック
        max_product_alt = spec_alt.get('maxProduct', {})
        if (params['product_length'] <= max_product_alt.get('L', 9999) and
            params['product_width'] <= max_product_alt.get('W', 9999) and
            params['product_height'] <= max_product_alt.get('H', 9999) and
            params['product_weight'] <= max_product_alt.get('weight', 9999)):

            container_config_alt = get_container_model_config(
                params['container_type'],
                model_name,
                CONTAINER_MODEL_MATRIX
            )

            if container_config_alt and container_config_alt.get('supported'):
                alternatives.append({
                    'name': model_name,
                    'spec': spec_alt,
                    'container_config': container_config_alt
                })

    alternatives = alternatives[:3]

    return {
        'selected_model': selected_model,
        'num_intervals': num_intervals,
        'num_blocks': num_blocks,
        'required_capacity_per_hour': required_capacity_per_hour,
        'actual_capacity': actual_capacity,
        'capacity_utilization': capacity_utilization,
        'recommended_units': recommended_units,
        'installation_length': installation_length,
        'installation_width': installation_width,
        'installation_height': installation_height,
        'alternatives': alternatives,
        'daily_pieces': daily_pieces
    }


def render_results(result, params):
    """計算結果の表示"""
    if not result:
        st.error("❌ 条件に適合する機種が見つかりませんでした。商品サイズまたは重量を見直してください。")
        return

    st.success("✅ 推奨仕様の計算が完了しました")

    # メトリクス表示
    st.markdown("---")
    st.subheader("🎯 推奨仕様")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "推奨機種",
            result['selected_model']['name'],
            help="最適な機種名"
        )

    with col2:
        st.metric(
            "処理能力",
            f"{result['actual_capacity']:,.0f} pcs/時",
            help="時間あたりの処理能力"
        )

    with col3:
        st.metric(
            "稼働率",
            f"{result['capacity_utilization']:.1f}%",
            delta=f"{'過負荷' if result['capacity_utilization'] > 95 else '適正'}",
            help="処理能力に対する稼働率"
        )

    with col4:
        st.metric(
            "推奨台数",
            f"{result['recommended_units']}台",
            help="適正稼働率を保つための推奨台数"
        )

    # 詳細仕様表
    st.markdown("---")
    st.subheader("📊 詳細仕様")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 機種情報")
        spec_data = {
            "項目": [
                "機種名",
                "処理能力",
                "間口数",
                "ブロック数",
                "最大商品寸法",
                "最大商品重量"
            ],
            "仕様": [
                result['selected_model']['name'],
                f"{result['actual_capacity']:,.0f} pcs/時",
                f"{result['num_intervals']}間口",
                f"{result['num_blocks']}ブロック",
                f"{result['selected_model']['spec']['maxProduct']['L']}×{result['selected_model']['spec']['maxProduct']['W']}×{result['selected_model']['spec']['maxProduct']['H']}mm",
                f"{result['selected_model']['spec']['maxProduct']['weight']}kg"
            ]
        }
        st.dataframe(
            pd.DataFrame(spec_data),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### 設置寸法")
        installation_data = {
            "項目": ["長さ", "幅", "高さ"],
            "寸法 (mm)": [
                f"{result['installation_length']:,.0f}",
                f"{result['installation_width']:,.0f}",
                f"{result['installation_height']:,.0f}"
            ]
        }
        st.dataframe(
            pd.DataFrame(installation_data),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown("#### 運用条件")
        operation_data = {
            "項目": [
                "日次出荷件数",
                "平均ピース数/件",
                "日次総ピース数",
                "必要処理能力",
                "作業時間",
                "ピーク倍率"
            ],
            "値": [
                f"{params['daily_orders']:,.0f}件",
                f"{params['pieces_per_order']:.1f}個",
                f"{result['daily_pieces']:,.0f}個",
                f"{result['required_capacity_per_hour']:,.0f} pcs/時",
                f"{params['working_hours']}時間",
                f"{params['peak_ratio']:.1f}倍"
            ]
        }
        st.dataframe(
            pd.DataFrame(operation_data),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### 容器対応")
        container_config = result['selected_model']['container_config']
        container_status = {
            "項目": ["容器タイプ", "対応状況", "推奨度"],
            "値": [
                params['container_type'],
                "✅ 対応" if container_config.get('supported') else "❌ 非対応",
                "⭐ 推奨" if container_config.get('recommended') else "△ 可能"
            ]
        }
        st.dataframe(
            pd.DataFrame(container_status),
            use_container_width=True,
            hide_index=True
        )

    # 間口構成グラフ
    st.markdown("---")
    st.subheader("📈 間口構成")

    fig = go.Figure()

    # 間口構成の可視化
    fig.add_trace(go.Bar(
        x=[f"ブロック{i+1}" for i in range(result['num_blocks'])],
        y=[result['num_intervals'] // result['num_blocks']] * result['num_blocks'],
        name="間口数",
        marker=dict(color='#FF6B35'),
        text=[f"{result['num_intervals'] // result['num_blocks']}間口"] * result['num_blocks'],
        textposition='auto'
    ))

    fig.update_layout(
        title=f"間口構成: 合計{result['num_intervals']}間口 / {result['num_blocks']}ブロック",
        xaxis_title="ブロック",
        yaxis_title="間口数",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # 能力チャート
    col1, col2 = st.columns(2)

    with col1:
        # 処理能力vs必要能力
        fig_capacity = go.Figure()

        fig_capacity.add_trace(go.Bar(
            x=["必要能力", "実能力"],
            y=[result['required_capacity_per_hour'], result['actual_capacity']],
            marker=dict(color=['#FFA500', '#FF6B35']),
            text=[f"{result['required_capacity_per_hour']:,.0f}", f"{result['actual_capacity']:,.0f}"],
            textposition='auto'
        ))

        fig_capacity.update_layout(
            title="処理能力比較 (pcs/時)",
            yaxis_title="処理能力",
            height=350,
            showlegend=False
        )

        st.plotly_chart(fig_capacity, use_container_width=True)

    with col2:
        # 稼働率ゲージ
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=result['capacity_utilization'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "稼働率 (%)"},
            delta={'reference': 85, 'increasing': {'color': "red"}},
            gauge={
                'axis': {'range': [None, 120]},
                'bar': {'color': "#FF6B35"},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, 85], 'color': "lightgreen"},
                    {'range': [85, 95], 'color': "yellow"},
                    {'range': [95, 120], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))

        fig_gauge.update_layout(height=350)
        st.plotly_chart(fig_gauge, use_container_width=True)

    # 代替案
    if result['alternatives']:
        st.markdown("---")
        st.subheader("💡 代替機種案")

        for i, alt in enumerate(result['alternatives'], 1):
            with st.expander(f"代替案 {i}: {alt['name']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("処理能力", f"{alt['spec'].get('processingCapacity', 1200):,.0f} pcs/時")
                with col2:
                    max_prod = alt['spec'].get('maxProduct', {})
                    st.metric("最大寸法", f"{max_prod.get('L', 0)}×{max_prod.get('W', 0)}mm")
                with col3:
                    container_status = "✅ 推奨" if alt['container_config'].get('recommended') else "△ 可能"
                    st.metric("容器対応", container_status)

    # 注意事項
    if result['capacity_utilization'] > 95:
        st.warning(f"""
        ⚠️ **注意**: 稼働率が95%を超えています（{result['capacity_utilization']:.1f}%）

        - 推奨台数: {result['recommended_units']}台での運用を検討してください
        - またはより大型の機種への変更をご検討ください
        """)

    st.info("""
    💡 **ご注意**
    - この試算は簡易的な目安です。正確な仕様提案には詳細な現地調査が必要です。
    - 実際の導入には、レイアウト、動線、ピッキング方法などの詳細検討が必要です。
    - お見積りやデモ見学のご希望は、下記の問い合わせフォームからご連絡ください。
    """)


def main():
    """メイン関数"""
    # アプリ初期化
    initialize_app()

    # カスタムCSS
    st.markdown("""
    <style>
    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # ヘッダー
    st.title("🤖 OmniSorter 簡易試算ツール")
    st.markdown("""
    OmniSorterの機種選定と仕様を簡易的に試算するツールです。
    作業条件と商品仕様を入力して、最適な機種を確認してください。
    """)

    # 入力フォーム
    st.markdown("---")
    params = render_input_form()

    # 計算実行
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_button = st.button(
            "🚀 仕様計算を実行",
            type="primary",
            use_container_width=True
        )

    if calculate_button:
        with st.spinner("計算中..."):
            result = calculate_omnisorter_spec(params)
            if result:
                st.session_state['last_result'] = result
                st.session_state['last_params'] = params

    # 結果表示
    if 'last_result' in st.session_state and 'last_params' in st.session_state:
        render_results(st.session_state['last_result'], st.session_state['last_params'])

    # 問い合わせフォーム
    st.markdown("---")
    st.markdown("---")
    render_contact_form()

    # フッター
    st.markdown("---")
    st.caption("© 2025 Bridgetown Engineering Co., Ltd. All rights reserved.")


if __name__ == "__main__":
    main()
