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
from pathlib import Path
import base64

from src.omnisorter_common import (
    initialize_session_state_safely,
    get_omnisorter_specs,
    get_container_matrix,
    get_container_model_config,
    get_app_settings
)
from src.contact_form import render_contact_form

# アプリケーション設定を読み込み
APP_SETTINGS = get_app_settings()

# 画像ディレクトリのパス
ASSETS_DIR = Path(__file__).parent / "assets" / "images"


def get_model_image_base64(image_filename: str) -> str:
    """機種画像をBase64エンコードして返す"""
    if not image_filename:
        return None

    image_path = ASSETS_DIR / image_filename
    if not image_path.exists():
        return None

    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    # 拡張子から MIME タイプを判定
    suffix = image_path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    mime_type = mime_types.get(suffix, 'image/png')

    return f"data:{mime_type};base64,{data}"


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

    # 設定からデフォルト値を取得
    ui_defaults = APP_SETTINGS.get('ui_defaults', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 基本情報")
        company_name = st.text_input(
            "会社名",
            placeholder="例：株式会社サンプル",
            key="input_company_name"
        )
        industry = st.selectbox(
            "業界",
            ["EC・通販", "小売・卸売", "食品", "アパレル", "医薬品", "製造業", "3PL", "その他"],
            key="input_industry"
        )
        business_type = st.selectbox(
            "事業形態",
            ["B2C（toC）", "B2B（toB）", "B2B2C", "その他"],
            key="input_business_type"
        )

        st.markdown("#### 運用条件")
        daily_orders = st.number_input(
            "平均日次出荷件数",
            min_value=1,
            max_value=50000,
            value=ui_defaults.get('daily_orders', 1000),
            step=10,
            key="input_daily_orders",
            help="1日あたりの出荷件数を入力"
        )

        pieces_per_order = st.number_input(
            "平均ピース数/件",
            min_value=0.1,
            max_value=1000.0,
            value=ui_defaults.get('pieces_per_order', 2.0),
            step=0.1,
            key="input_pieces_per_order",
            help="1件あたりの平均商品点数"
        )

        working_hours = st.number_input(
            "作業可能時間/日（時間）",
            min_value=1.0,
            max_value=24.0,
            value=ui_defaults.get('working_hours', 8.0),
            step=1.0,
            key="input_working_hours",
            help="1日で仕分けにとれる作業可能時間"
        )

    with col2:
        st.markdown("#### 商品平均仕様")

        col2_1, col2_2 = st.columns(2)
        with col2_1:
            product_length = st.number_input(
                "長さ (mm)",
                min_value=50,
                max_value=1500,
                value=ui_defaults.get('product_length', 300),
                step=10,
                key="input_product_length",
                help="商品の最大長さ"
            )
            product_width = st.number_input(
                "幅 (mm)",
                min_value=50,
                max_value=1000,
                value=ui_defaults.get('product_width', 200),
                step=10,
                key="input_product_width",
                help="商品の最大幅"
            )

        with col2_2:
            product_height = st.number_input(
                "高さ (mm)",
                min_value=10,
                max_value=600,
                value=ui_defaults.get('product_height', 150),
                step=10,
                key="input_product_height",
                help="商品の最大高さ"
            )
            product_weight = st.number_input(
                "平均重量 (kg)",
                min_value=0.1,
                max_value=10.0,
                value=ui_defaults.get('product_weight', 1.5),
                step=0.1,
                key="input_product_weight",
                help="商品の最大重量（Lサイズは8kgまで対応）"
            )

        container_type = st.selectbox(
            "出荷容器タイプ",
            ["OS標準トート", "オリコン30L", "オリコン40L", "オリコン50L", "その他"],
            key="input_container_type"
        )

        st.markdown("#### 追加情報（任意）")
        peak_ratio_options = ui_defaults.get('peak_ratio_options', [1.0, 1.2, 1.5, 2.0, 2.5, 3.0])
        peak_ratio = st.selectbox(
            "ピーク倍率",
            options=peak_ratio_options,
            index=0,  # デフォルト: 1.0
            format_func=lambda x: f"{x:.1f}倍",
            key="input_peak_ratio",
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
    """OmniSorter仕様の計算

    計算ロジック:
    1. 必要処理能力（pcs/h）と必要件数（件/h）を算出
    2. 機種の処理能力で対応可能かを判定
    3. 回転数を考慮した最小間口数を算出（コスト最小化）
    4. 必要台数を算出

    パラメータは config/app_settings.yaml から読み込み
    """
    PRODUCT_SPECS = get_omnisorter_specs()
    CONTAINER_MODEL_MATRIX = get_container_matrix()

    # 設定から計算パラメータを取得
    calc_settings = APP_SETTINGS.get('calculation', {})
    scoring_settings = APP_SETTINGS.get('scoring', {})

    TARGET_UTILIZATION = calc_settings.get('target_utilization', 0.95)
    TARGET_ROTATION = max(1, calc_settings.get('target_rotation', 5))  # 目標回転数（最小1）
    MAX_UNITS = calc_settings.get('max_units', 2)  # 台数上限（デフォルト2台）

    # デバッグ: 設定値を表示（UIにも出力）
    debug_info = []
    debug_info.append(f"MAX_UNITS: {MAX_UNITS}")
    debug_info.append(f"入力: {params['daily_orders']}件×{params['pieces_per_order']}pcs, {params['working_hours']}h, peak={params['peak_ratio']}")
    debug_info.append(f"商品: {params['product_length']}x{params['product_width']}x{params['product_height']}mm")

    # 必要処理能力の計算
    daily_pieces = params['daily_orders'] * params['pieces_per_order']
    daily_orders = params['daily_orders']
    working_hours = params['working_hours']
    peak_ratio = params['peak_ratio']

    # 時間あたり必要処理能力
    required_pcs_per_hour = (daily_pieces / working_hours) * peak_ratio
    required_orders_per_hour = (daily_orders / working_hours) * peak_ratio

    debug_info.append(f"必要能力: {required_pcs_per_hour:.0f} pcs/h, {required_orders_per_hour:.0f} 件/h")

    # 機種選定ロジック
    selected_model = None
    best_score = float('-inf')  # 負のスコアでも選択できるように
    best_calculation = None

    for model_name, spec in PRODUCT_SPECS.items():
        # 物理制約チェック（L/W/H: mm、weight: g）
        # 入力の重量はkg、設定はgのため1000倍して比較
        # 長さと幅は回転を考慮（どちらの向きでも入ればOK）
        max_product = spec.get('maxProduct', {})
        product_weight_g = params['product_weight'] * 1000  # kg → g

        max_L = max_product.get('L', 9999)
        max_W = max_product.get('W', 9999)
        max_H = max_product.get('H', 9999)
        max_weight = max_product.get('weight', 9999)

        prod_L = params['product_length']
        prod_W = params['product_width']
        prod_H = params['product_height']

        # 回転なし: 長さ→L、幅→W
        fits_normal = (prod_L <= max_L) and (prod_W <= max_W)
        # 回転あり: 長さ→W、幅→L（90度回転）
        fits_rotated = (prod_L <= max_W) and (prod_W <= max_L)

        # どちらの向きでも入らない、または高さ・重量がオーバーなら除外
        if (not fits_normal and not fits_rotated) or prod_H > max_H or product_weight_g > max_weight:
            debug_info.append(f"{model_name}: SKIP(サイズ) max={max_L}x{max_W}x{max_H}mm")
            continue

        # 容器対応チェック
        container_config = get_container_model_config(
            model_name,
            params['container_type'],
            CONTAINER_MODEL_MATRIX
        )

        if not container_config or not container_config.get('supported'):
            debug_info.append(f"{model_name}: SKIP(容器非対応) {params['container_type']}")
            continue

        # 機種の処理能力
        processing_capacity = spec.get('processingCapacity', 1200)

        # 処理能力チェック: 1台で対応できない場合は複数台必要
        # 有効処理能力 = 処理能力 × 稼働率
        effective_capacity_per_unit = processing_capacity * TARGET_UTILIZATION

        # 必要台数の計算（処理能力ベース）
        units_by_capacity = np.ceil(required_pcs_per_hour / effective_capacity_per_unit)

        # 1件あたりの処理時間（秒）
        pieces_per_order = params['pieces_per_order']
        seconds_per_pcs = 3600 / processing_capacity
        seconds_per_order = pieces_per_order * seconds_per_pcs

        # 処理能力ベースの件数/時/台
        orders_per_hour_per_unit = effective_capacity_per_unit / pieces_per_order

        # 目標回転数を使用した間口数計算
        # 間口数 = 必要件数/時 ÷ 目標回転数
        # 目標回転数: 1間口が1時間に何件処理するかの目標値
        effective_rotation = TARGET_ROTATION
        min_ports_needed = np.ceil(required_orders_per_hour / effective_rotation)

        # 必要台数の計算（処理能力と間口数の両方を考慮）
        # 1台あたりの間口数上限
        total_ports = spec.get('totalPorts', 200)
        # 容器タイプごとのports_per_blockを優先（例：オリコン50Lは24間口/ブロック）
        ports_per_block = container_config.get('ports_per_block', spec.get('portsPerBlock', 40))

        # mini機種の場合は固定構成
        if 'mini' in model_name.lower():
            max_ports_per_unit = total_ports
            is_mini = True
        else:
            max_ports_per_unit = total_ports
            is_mini = False

        # 間口数による必要台数
        units_by_ports = np.ceil(min_ports_needed / max_ports_per_unit)

        # 最終的な必要台数（処理能力と間口数の大きい方）
        recommended_units = int(max(units_by_capacity, units_by_ports))

        # 台数上限チェック: 上限を超える場合はこの機種をスキップ
        if recommended_units > MAX_UNITS:
            debug_info.append(f"{model_name}: SKIP(台数超過) {recommended_units}台 > MAX={MAX_UNITS}")
            debug_info.append(f"  └ capacity:{int(units_by_capacity)}台, ports:{int(units_by_ports)}台")
            continue

        debug_info.append(f"{model_name}: PASS {recommended_units}台 <= MAX={MAX_UNITS}")
        debug_info.append(f"  └ 目標回転:{effective_rotation}回/h, 必要間口:{int(min_ports_needed)}口")

        # 1台あたりの間口数
        if recommended_units > 0:
            ports_per_unit = int(np.ceil(min_ports_needed / recommended_units))
        else:
            ports_per_unit = int(min_ports_needed)

        # 間口数を上限内に収める
        ports_per_unit = min(ports_per_unit, max_ports_per_unit)

        # ブロック数の計算
        if is_mini:
            num_blocks = spec.get('blocks', 2)
            num_intervals = total_ports
        else:
            # ブロック数 = 間口数 ÷ ブロックあたり間口数（切り上げ）
            num_blocks = int(np.ceil(ports_per_unit / ports_per_block))
            # ブロック数上限チェック
            blocks_config = spec.get('blocks', {})
            if isinstance(blocks_config, dict):
                max_blocks = blocks_config.get('max', 10)
                min_blocks = blocks_config.get('min', 1)
            else:
                max_blocks = 10
                min_blocks = 1
            num_blocks = max(min_blocks, min(num_blocks, max_blocks))
            # 実際の間口数
            num_intervals = num_blocks * ports_per_block

        # 稼働率の計算
        total_capacity = processing_capacity * recommended_units
        capacity_utilization = (required_pcs_per_hour / total_capacity) * 100

        # 実際の回転数
        actual_rotation = required_orders_per_hour / (num_intervals * recommended_units)

        # スコア計算（設定ファイルから読み込み）
        model_priority = scoring_settings.get('model_priority', {})
        mini_threshold = scoring_settings.get('mini_threshold_pcs', 3000)
        util_settings = scoring_settings.get('utilization', {})
        cost_penalty = scoring_settings.get('cost_penalty', {})

        score = 0

        # 機種優先度
        if 'mini' in model_name.lower():
            if daily_pieces <= mini_threshold:
                score += model_priority.get('mini_small', 150)
            else:
                score += model_priority.get('mini_large', 10)
        elif model_name == 'S':
            score += model_priority.get('S', 100)
        elif model_name == 'M':
            score += model_priority.get('M', 50)
        elif model_name == 'L':
            score += model_priority.get('L', 25)

        # 容器適合度
        if container_config.get('recommended'):
            score += scoring_settings.get('container_recommended_bonus', 20)

        # 稼働率適合度
        optimal_min = util_settings.get('optimal_min', 60)
        optimal_max = util_settings.get('optimal_max', 85)
        high_max = util_settings.get('high_max', 95)

        if optimal_min <= capacity_utilization <= optimal_max:
            score += util_settings.get('optimal_bonus', 15)
        elif optimal_max < capacity_utilization <= high_max:
            score += util_settings.get('high_bonus', 10)
        elif capacity_utilization > 100:
            score += util_settings.get('overload_penalty', -10)

        # コストペナルティ
        units_penalty = cost_penalty.get('units_penalty', 30)
        ports_penalty = cost_penalty.get('ports_penalty', 0.1)
        ports_baseline = cost_penalty.get('ports_baseline', 40)

        score -= (recommended_units - 1) * units_penalty
        score -= (num_intervals - ports_baseline) * ports_penalty

        if score > best_score:
            best_score = score
            selected_model = {
                'name': model_name,
                'spec': spec,
                'container_config': container_config,
                'score': score
            }
            best_calculation = {
                'num_intervals': num_intervals,
                'num_blocks': num_blocks,
                'recommended_units': recommended_units,
                'capacity_utilization': capacity_utilization,
                'actual_rotation': actual_rotation,
                'effective_rotation': effective_rotation,
                'min_ports_needed': min_ports_needed,
                'seconds_per_order': seconds_per_order,
                'orders_per_hour_per_unit': orders_per_hour_per_unit
            }

    if not selected_model:
        debug_info.append(f"=== 適合機種なし (MAX_UNITS={MAX_UNITS}) ===")
        # デバッグ情報をセッションに保存
        st.session_state['debug_info'] = debug_info
        return None

    debug_info.append(f"=== 選択: {selected_model['name']} (score={best_score}) ===")
    # デバッグ情報をセッションに保存
    st.session_state['debug_info'] = debug_info

    # 選択された機種の計算結果を使用
    spec = selected_model['spec']
    num_intervals = best_calculation['num_intervals']
    num_blocks = best_calculation['num_blocks']
    recommended_units = best_calculation['recommended_units']
    capacity_utilization = best_calculation['capacity_utilization']
    actual_capacity = spec.get('processingCapacity', 1200)

    # 設置寸法の計算
    dimensions = spec.get('dimensions', {})
    installation_length = dimensions.get('L', 10) * 1000  # m to mm
    installation_width = dimensions.get('W', 3) * 1000
    installation_height = dimensions.get('H', 2.5) * 1000

    # 代替案の生成（上位3つ）
    alternatives = []
    product_weight_g = params['product_weight'] * 1000  # kg → g

    for model_name, spec_alt in PRODUCT_SPECS.items():
        if model_name == selected_model['name']:
            continue

        # 物理制約チェック（回転考慮）
        max_product_alt = spec_alt.get('maxProduct', {})
        max_L_alt = max_product_alt.get('L', 9999)
        max_W_alt = max_product_alt.get('W', 9999)
        max_H_alt = max_product_alt.get('H', 9999)
        max_weight_alt = max_product_alt.get('weight', 9999)

        prod_L = params['product_length']
        prod_W = params['product_width']
        prod_H = params['product_height']

        # 回転を考慮した適合チェック
        fits_normal_alt = (prod_L <= max_L_alt) and (prod_W <= max_W_alt)
        fits_rotated_alt = (prod_L <= max_W_alt) and (prod_W <= max_L_alt)

        if ((fits_normal_alt or fits_rotated_alt) and
            prod_H <= max_H_alt and
            product_weight_g <= max_weight_alt):

            container_config_alt = get_container_model_config(
                model_name,
                params['container_type'],
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
        'required_capacity_per_hour': required_pcs_per_hour,
        'required_orders_per_hour': required_orders_per_hour,
        'actual_capacity': actual_capacity,
        'capacity_utilization': capacity_utilization,
        'recommended_units': recommended_units,
        'installation_length': installation_length,
        'installation_width': installation_width,
        'installation_height': installation_height,
        'alternatives': alternatives,
        'daily_pieces': daily_pieces,
        'effective_rotation': best_calculation['effective_rotation'],
        'actual_rotation': best_calculation['actual_rotation'],
        'min_ports_needed': best_calculation['min_ports_needed']
    }


def render_no_match_guidance(params):
    """適合機種がない場合のガイダンス表示"""
    st.markdown("""
    <style>
    .no-match-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #FF6B35;
    }
    .no-match-title {
        color: #333;
        margin: 0 0 1rem 0;
        font-size: 1.3rem;
    }
    .no-match-text {
        color: #555;
        margin: 0.5rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .solution-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    .solution-title {
        color: #333;
        font-weight: bold;
        margin: 0 0 0.3rem 0;
        font-size: 0.95rem;
    }
    .solution-desc {
        color: #666;
        margin: 0;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="no-match-section">
        <h3 class="no-match-title">🔍 OmniSorterの標準機種では適合が難しい条件です</h3>
        <p class="no-match-text">
            ご入力いただいた条件（商品サイズ・重量・処理能力）では、
            OmniSorterの標準ラインナップでの対応が難しい可能性があります。
        </p>
        <p class="no-match-text">
            しかし、<strong>諦めるのはまだ早いです！</strong><br>
            当社では以下のような代替ソリューションをご提案できる場合があります。
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 代替ソリューションの提案
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="solution-card">
            <p class="solution-title">🔧 カスタマイズ対応</p>
            <p class="solution-desc">
                標準機種をベースにした特注対応で、
                大型商品や重量物への対応が可能な場合があります。
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="solution-card">
            <p class="solution-title">🤝 パートナー製品のご紹介</p>
            <p class="solution-desc">
                OmniSorter以外の仕分けソリューションも含めて、
                最適な製品をご提案いたします。
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="solution-card">
            <p class="solution-title">📐 運用条件の見直し相談</p>
            <p class="solution-desc">
                作業時間の調整やピーク分散など、
                運用面での最適化をご提案できる場合があります。
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="solution-card">
            <p class="solution-title">🔄 複合ソリューション</p>
            <p class="solution-desc">
                前工程・後工程も含めた総合的な物流改善を
                トータルでご提案いたします。
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 入力条件の表示
    st.markdown("---")
    st.markdown("**📋 ご入力いただいた条件**")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        **運用条件**
        - 日次出荷: {params['daily_orders']:,} 件/日
        - 平均ピース数: {params['pieces_per_order']:.1f} pcs/件
        - 作業時間: {params['working_hours']} 時間/日
        """)
    with col2:
        st.markdown(f"""
        **商品サイズ**
        - 長さ: {params['product_length']} mm
        - 幅: {params['product_width']} mm
        - 高さ: {params['product_height']} mm
        """)
    with col3:
        st.markdown(f"""
        **その他**
        - 重量: {params['product_weight']} kg
        - 容器: {params['container_type']}
        - ピーク倍率: {params['peak_ratio']:.1f}倍
        """)

    # 問い合わせ誘導ボタン
    st.markdown("---")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    ">
        <h3 style="color: white; margin: 0 0 0.5rem 0; font-size: 1.2rem;">
            📞 まずはお気軽にご相談ください
        </h3>
        <p style="color: rgba(255,255,255,0.9); margin: 0 0 1rem 0; font-size: 0.9rem;">
            専門スタッフがお客様の課題をヒアリングし、最適なソリューションをご提案いたします。
        </p>
        <a href="#contact-form" style="
            background: white;
            color: #28a745;
            padding: 0.7rem 2rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
        ">
            📩 お問い合わせフォームへ
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 **ヒント**: 下記の問い合わせフォームから送信いただくと、入力条件が自動で送信されます。")


def render_results(result, params):
    """計算結果の表示"""
    if not result:
        render_no_match_guidance(params)
        return

    # 表示設定を取得
    display_settings = APP_SETTINGS.get('display', {})
    util_thresholds = display_settings.get('utilization_thresholds', {})
    target_util_display = display_settings.get('target_utilization_display', '60-85%')

    # ========================================
    # 推奨機種ヒーローセクション（コンパクト・レスポンシブ対応）
    # ========================================
    model_name = result['selected_model']['spec']['name']
    units = result['recommended_units']
    units_text = f" × {units}台" if units > 1 else ""

    # 機種画像の取得
    image_filename = result['selected_model']['spec'].get('image', '')
    image_data = get_model_image_base64(image_filename)

    # レスポンシブ対応CSS
    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0 1rem 0;
        box-shadow: 0 3px 10px rgba(255, 107, 53, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
    }
    .hero-image {
        flex-shrink: 0;
        width: 280px;
        height: 180px;
        object-fit: contain;
        border-radius: 8px;
        background: rgba(255,255,255,0.15);
        padding: 8px;
    }
    .hero-content {
        text-align: left;
        flex: 1;
        min-width: 200px;
    }
    .hero-label {
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .hero-title {
        color: white;
        margin: 0.3rem 0;
        font-size: 1.6rem;
        font-weight: bold;
        line-height: 1.2;
    }
    .hero-specs {
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    /* タブレット */
    @media (max-width: 768px) {
        .hero-section {
            flex-direction: column;
            padding: 1rem;
            gap: 0.8rem;
        }
        .hero-image {
            width: 220px;
            height: 140px;
        }
        .hero-content {
            text-align: center;
        }
        .hero-title {
            font-size: 1.3rem;
        }
        .hero-specs {
            font-size: 0.8rem;
        }
    }
    /* スマホ */
    @media (max-width: 480px) {
        .hero-section {
            padding: 0.8rem;
            gap: 0.6rem;
        }
        .hero-image {
            width: 180px;
            height: 110px;
        }
        .hero-title {
            font-size: 1.1rem;
        }
        .hero-specs {
            font-size: 0.75rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # 画像がある場合は画像付きレイアウト、ない場合はテキストのみ
    if image_data:
        st.markdown(f"""
        <div class="hero-section">
            <img src="{image_data}" alt="{model_name}" class="hero-image">
            <div class="hero-content">
                <p class="hero-label">推奨機種</p>
                <h2 class="hero-title">🤖 {model_name}{units_text}</h2>
                <p class="hero-specs">
                    処理能力 {result['actual_capacity']:,.0f} pcs/時<br>
                    {result['num_intervals']}間口/台 ｜ {result['num_blocks']}ブロック/台
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="hero-section" style="justify-content: center;">
            <div class="hero-content" style="text-align: center;">
                <p class="hero-label">推奨機種</p>
                <h2 class="hero-title">🤖 {model_name}{units_text}</h2>
                <p class="hero-specs">
                    処理能力 {result['actual_capacity']:,.0f} pcs/時 ｜ {result['num_intervals']}間口/台 ｜ {result['num_blocks']}ブロック/台
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 問い合わせボタン（ヒーローセクション直下・コンパクト）
    _, col_btn_center, _ = st.columns([1, 2, 1])
    with col_btn_center:
        st.markdown("""
        <a href="#contact-form" style="text-decoration: none; display: block;">
            <div style="
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                border-radius: 6px;
                padding: 0.6rem 1.5rem;
                text-align: center;
                cursor: pointer;
                box-shadow: 0 2px 6px rgba(40, 167, 69, 0.25);
            ">
                <span style="color: white; font-size: 0.95rem; font-weight: bold;">
                    📩 この結果で問い合わせる
                </span>
            </div>
        </a>
        """, unsafe_allow_html=True)

    # ========================================
    # 主要指標カード（3列・コンパクト）
    # ========================================
    # レスポンシブCSS for metric cards
    st.markdown("""
    <style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
        border-left: 3px solid;
    }
    .metric-label {
        color: #666;
        margin: 0;
        font-size: 0.75rem;
    }
    .metric-value {
        margin: 0.2rem 0;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .metric-unit {
        color: #888;
        margin: 0;
        font-size: 0.75rem;
    }
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.2rem;
        }
        .metric-label, .metric-unit {
            font-size: 0.7rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # 稼働率の色分け（設定ファイルから閾値を取得）
    util = result['capacity_utilization']
    danger_threshold = util_thresholds.get('danger', 95)
    warning_threshold = util_thresholds.get('warning', 85)

    if util > danger_threshold:
        util_color = "#dc3545"  # 赤
        util_status = "⚠️ 過負荷"
    elif util > warning_threshold:
        util_color = "#ffc107"  # 黄
        util_status = "△ 高負荷"
    else:
        util_color = "#28a745"  # 緑
        util_status = "✅ 適正"

    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-color: #FF6B35;">
            <p class="metric-label">日次処理量</p>
            <h3 class="metric-value" style="color: #333;">{result['daily_pieces']:,.0f}</h3>
            <p class="metric-unit">pcs/日</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-color: {util_color};">
            <p class="metric-label">稼働率 {util_status}</p>
            <h3 class="metric-value" style="color: {util_color};">{util:.1f}%</h3>
            <p class="metric-unit">目標: {target_util_display}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-color: #17a2b8;">
            <p class="metric-label">推奨台数</p>
            <h3 class="metric-value" style="color: #333;">{result['recommended_units']}</h3>
            <p class="metric-unit">台</p>
        </div>
        """, unsafe_allow_html=True)

    # ========================================
    # 詳細仕様（タブ形式）
    # ========================================
    tab1, tab2, tab3 = st.tabs(["📋 機種仕様", "📦 運用条件", "📐 設置情報"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**機種スペック**")
            spec_data = pd.DataFrame({
                "項目": ["処理能力", "間口数", "ブロック数"],
                "値": [
                    f"{result['actual_capacity']:,.0f} pcs/時",
                    f"{result['num_intervals']} 間口",
                    f"{result['num_blocks']} ブロック"
                ]
            })
            st.dataframe(spec_data, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("**対応商品サイズ**")
            max_prod = result['selected_model']['spec']['maxProduct']
            size_data = pd.DataFrame({
                "項目": ["最大長さ", "最大幅", "最大高さ", "最大重量"],
                "値": [
                    f"{max_prod['L']} mm",
                    f"{max_prod['W']} mm",
                    f"{max_prod['H']} mm",
                    f"{max_prod['weight'] / 1000:.0f} kg"
                ]
            })
            st.dataframe(size_data, use_container_width=True, hide_index=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**入力条件**")
            input_data = pd.DataFrame({
                "項目": ["日次出荷件数", "平均ピース数/件", "作業時間", "ピーク倍率"],
                "値": [
                    f"{params['daily_orders']:,} 件",
                    f"{params['pieces_per_order']:.1f} 個",
                    f"{params['working_hours']} 時間",
                    f"{params['peak_ratio']:.1f} 倍"
                ]
            })
            st.dataframe(input_data, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("**容器対応**")
            container_config = result['selected_model']['container_config']
            container_data = pd.DataFrame({
                "項目": ["容器タイプ", "対応状況", "推奨度"],
                "値": [
                    params['container_type'],
                    "✅ 対応" if container_config.get('supported') else "❌ 非対応",
                    "⭐ 推奨" if container_config.get('recommended') else "〇 可能"
                ]
            })
            st.dataframe(container_data, use_container_width=True, hide_index=True)

        # 計算内訳セクション
        st.markdown("---")
        st.markdown("**📊 計算内訳**")
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**処理能力計算**")
            required_orders = result.get('required_orders_per_hour', 0)
            calc_data = pd.DataFrame({
                "項目": ["必要処理能力", "必要件数/時", "目標回転数", "実回転数"],
                "値": [
                    f"{result['required_capacity_per_hour']:,.0f} pcs/時",
                    f"{required_orders:,.1f} 件/時",
                    f"{result.get('effective_rotation', 0)} 回転/時",
                    f"{result.get('actual_rotation', 0):.1f} 回転/時"
                ]
            })
            st.dataframe(calc_data, use_container_width=True, hide_index=True)

        with col4:
            st.markdown("**間口数計算**")
            min_ports = result.get('min_ports_needed', 0)
            ports_data = pd.DataFrame({
                "項目": ["理論最小間口数", "構成間口数", "推奨台数", "合計間口数"],
                "値": [
                    f"{min_ports:.0f} 間口",
                    f"{result['num_intervals']} 間口/台",
                    f"{result['recommended_units']} 台",
                    f"{result['num_intervals'] * result['recommended_units']} 間口"
                ]
            })
            st.dataframe(ports_data, use_container_width=True, hide_index=True)

        # 計算式の説明
        effective_rot = result.get('effective_rotation', 0)
        st.caption(f"""
        💡 **計算ロジック**:
        必要処理能力 = ({params['daily_orders']:,}件 × {params['pieces_per_order']:.1f}pcs) ÷ {params['working_hours']}h × {params['peak_ratio']:.1f} = {result['required_capacity_per_hour']:,.0f} pcs/時
        | 理論最小間口数 = {required_orders:.1f}件/時 ÷ 目標回転数({effective_rot}回転/時) = {min_ports:.0f}間口
        """)

    with tab3:
        st.markdown("**設置寸法（概算）**")
        install_data = pd.DataFrame({
            "項目": ["長さ", "幅", "高さ"],
            "寸法": [
                f"{result['installation_length']:,.0f} mm",
                f"{result['installation_width']:,.0f} mm",
                f"{result['installation_height']:,.0f} mm"
            ]
        })
        st.dataframe(install_data, use_container_width=True, hide_index=True)
        st.caption("※ 実際の設置寸法は現地調査により決定します")

    # 能力チャート
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        # 処理能力vs必要能力（複数台の場合は合計能力を表示）
        units = result['recommended_units']
        total_capacity = result['actual_capacity'] * units

        fig_capacity = go.Figure()

        fig_capacity.add_trace(go.Bar(
            x=["必要能力", "実能力"],
            y=[result['required_capacity_per_hour'], total_capacity],
            marker=dict(color=['#FFA500', '#FF6B35']),
            text=[f"{result['required_capacity_per_hour']:,.0f}", f"{total_capacity:,.0f}"],
            textposition='auto'
        ))

        # タイトルに台数を反映
        title_text = f"処理能力比較 (pcs/時)" if units == 1 else f"処理能力比較 (pcs/時) - {units}台合計"

        fig_capacity.update_layout(
            title=title_text,
            yaxis_title="処理能力",
            height=280,
            showlegend=False,
            margin=dict(t=40, b=30, l=40, r=20)
        )

        st.plotly_chart(fig_capacity, use_container_width=True)

        # 複数台の場合は注記を追加
        if units > 1:
            st.caption(f"※ 実能力は {result['actual_capacity']:,.0f} pcs/時 × {units}台 = {total_capacity:,.0f} pcs/時")

    with col2:
        # 稼働率ゲージ（ステータス表示付き）
        util_value = result['capacity_utilization']

        # ステータス判定
        if util_value > danger_threshold:
            gauge_status = "⚠️ 過負荷"
            status_color = "#dc3545"
        elif util_value > warning_threshold:
            gauge_status = "△ 高負荷"
            status_color = "#ffc107"
        elif util_value >= 60:
            gauge_status = "✅ 適正"
            status_color = "#28a745"
        else:
            gauge_status = "△ 低稼働"
            status_color = "#6c757d"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=util_value,
            number={'suffix': '%', 'font': {'size': 32}},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"稼働率<br><span style='font-size:0.8em;color:{status_color}'>{gauge_status}</span>"},
            gauge={
                'axis': {'range': [None, 120]},
                'bar': {'color': "#FF6B35"},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, warning_threshold], 'color': "lightgreen"},
                    {'range': [warning_threshold, danger_threshold], 'color': "yellow"},
                    {'range': [danger_threshold, 120], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': danger_threshold
                }
            }
        ))

        fig_gauge.update_layout(height=280, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # 代替案
    if result['alternatives']:
        st.markdown("---")
        st.subheader("💡 代替機種案")

        for i, alt in enumerate(result['alternatives'], 1):
            with st.expander(f"代替案 {i}: {alt['spec']['name']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("処理能力", f"{alt['spec'].get('processingCapacity', 1200):,.0f} pcs/時")
                with col2:
                    max_prod = alt['spec'].get('maxProduct', {})
                    st.metric("最大寸法", f"{max_prod.get('L', 0)}×{max_prod.get('W', 0)}mm")
                with col3:
                    container_status = "✅ 推奨" if alt['container_config'].get('recommended') else "〇 可能"
                    st.metric("容器対応", container_status)

    # まとめ仕分けモードの提案（複数台の場合）
    if result['recommended_units'] > 1:
        st.markdown("---")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin: 0.5rem 0;
            color: white;
        ">
            <h4 style="margin: 0 0 0.3rem 0; color: white; font-size: 1rem;">💡 1台で対応できる可能性があります</h4>
            <p style="margin: 0; opacity: 0.95; font-size: 0.85rem;">
                現在 <strong>{result['recommended_units']}台</strong> 推奨ですが、
                <strong>「まとめ仕分けモード」</strong>で<strong>1台運用</strong>が可能な場合があります。
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📦 まとめ仕分けモードとは？", expanded=False):
            st.markdown("""
            **生産性をさらにアップするブースト機能**です。同一SKUの商品を複数個同時に仕分けできます。

            | 機能 | 説明 |
            |------|------|
            | **複数個を同時投入** | 同一SKUを重ねて流す |
            | **ボール単位の仕分け** | バケットに入れて仕分け |

            **例**: 1投入で平均4pcs以上まとめれば、処理能力が**4倍**に。
            """)

            # 1台で対応できる場合のシミュレーション
            required_pcs_h = result['required_capacity_per_hour']
            model_capacity = result['actual_capacity']
            batch_mode_max = display_settings.get('batch_mode_max_pcs', 10)

            # 1台で対応するために必要なpcs/投入
            # 機種の処理能力（投入回数/h）に対して必要なpcs/hを達成するための倍率
            if model_capacity > 0:
                effective_capacity = model_capacity * 0.85  # 稼働率考慮
                needed_pcs_per_input = np.ceil(required_pcs_h / effective_capacity)

                if needed_pcs_per_input <= batch_mode_max and needed_pcs_per_input > 1:
                    st.success(f"""
                    📊 **1台で運用するには**: 1投入で同一SKUを平均 **{int(needed_pcs_per_input)}pcs以上** まとめて投入できれば対応可能です。
                    （必要処理能力: {required_pcs_h:,.0f} pcs/h ÷ 有効能力: {effective_capacity:,.0f} 投入/h = {needed_pcs_per_input:.1f} pcs/投入）
                    """)

    # 注意事項
    if result['capacity_utilization'] > danger_threshold:
        st.warning(f"""
        ⚠️ **注意**: 稼働率が{danger_threshold}%を超えています（{result['capacity_utilization']:.1f}%）

        - 推奨台数: {result['recommended_units']}台での運用を検討してください
        - またはより大型の機種への変更をご検討ください
        """)

    st.caption("""
    💡 **ご注意**: この試算は簡易的な目安です。正確な仕様には現地調査が必要です。お見積り・デモ見学は下記フォームからどうぞ。
    """)


def main():
    """メイン関数"""
    # アプリ初期化
    initialize_app()

    # カスタムCSS（レスポンシブ対応）
    st.markdown("""
    <style>
    .main .block-container {
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 0.8rem;
        border-radius: 0.5rem;
    }
    /* タブのパディング調整 */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 0.5rem;
    }
    /* データフレームのコンパクト化 */
    .stDataFrame {
        font-size: 0.85rem;
    }
    /* スマホ対応 */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # ヘッダー（センタリング）
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h1 style="margin: 0; font-size: 2rem;">🤖 OmniSorter おすすめ試算ツール</h1>
        <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 0.95rem;">
            OmniSorterの機種と仕様を簡易的に試算します。<br>
            あなたの業務にあうOmniSorterを簡単に見つけます！
        </p>
    </div>
    """, unsafe_allow_html=True)

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
            # 計算結果を保存（Noneの場合も保存して、no-match guidanceを表示）
            st.session_state['last_result'] = result
            st.session_state['last_params'] = params
            st.session_state['calculation_attempted'] = True

    # 結果表示（計算が実行された場合のみ）
    if st.session_state.get('calculation_attempted') and 'last_params' in st.session_state:
        render_results(st.session_state.get('last_result'), st.session_state['last_params'])

        # デバッグ情報表示（非表示）
        # if 'debug_info' in st.session_state:
        #     with st.expander("🔧 計算デバッグ情報", expanded=False):
        #         for line in st.session_state['debug_info']:
        #             st.text(line)

    # 問い合わせフォーム（アンカー付き）
    st.markdown("---")
    st.markdown('<div id="contact-form"></div>', unsafe_allow_html=True)
    st.markdown("---")
    # 試算結果があれば問い合わせフォームに渡す
    inquiry_params = st.session_state.get('last_params', None)
    inquiry_result = st.session_state.get('last_result', None)
    render_contact_form(params=inquiry_params, result=inquiry_result)

    # フッター
    st.markdown("---")
    st.caption("© 2026 XXX Co., Ltd. All rights reserved.")


if __name__ == "__main__":
    main()
