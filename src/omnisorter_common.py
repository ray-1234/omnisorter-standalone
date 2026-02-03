"""OmniSorter関連の共通関数・定数を定義（修正版）"""
from typing import Dict


def get_omnisorter_specs() -> Dict:
    """
    OmniSorter仕様を取得（YAMLから読み込み）

    Returns:
        機種スペック辞書

    Raises:
        ConfigLoadError: 設定ファイルが見つからない場合
        ConfigValidationError: 設定が不正な場合
    """
    from src.config_loader import load_omnisorter_specs
    return load_omnisorter_specs()


def get_container_matrix() -> Dict:
    """
    容器×機種マトリクスを取得（YAMLから読み込み）

    Returns:
        容器マトリクス辞書

    Raises:
        ConfigLoadError: 設定ファイルが見つからない場合
        ConfigValidationError: 設定が不正な場合
    """
    from src.config_loader import load_container_model_matrix
    return load_container_model_matrix()


def get_app_settings() -> Dict:
    """
    アプリケーション設定を取得（YAMLから読み込み）

    Returns:
        アプリケーション設定辞書
    """
    from src.config_loader import load_app_settings
    return load_app_settings()


def safe_get_session_value(key, default_value):
    """セッション状態から値を安全に取得"""
    try:
        import streamlit as st
        if key not in st.session_state:
            st.session_state[key] = default_value
        return st.session_state[key]
    except:
        return default_value

def safe_set_session_value(key, value):
    """セッション状態に値を安全に設定"""
    try:
        import streamlit as st
        st.session_state[key] = value
        return True
    except:
        return False

def get_container_model_config(model_id, container_type, matrix=None):
    """指定された機種と容器タイプの構成情報を取得（安全版）"""
    if matrix is None:
        # 設定から取得を試行
        matrix = safe_get_session_value('container_model_matrix', None)
        if matrix is None:
            matrix = get_container_matrix()
    
    if model_id in matrix and container_type in matrix[model_id]:
        config = matrix[model_id][container_type]
        
        # 非対応の場合は明確にエラー情報を返す
        if not config.get('supported', True):
            return {
                'max_rows': 0, 'max_columns': 0, 'max_sides': 0,
                'ports_per_block': 0, 'default_blocks': 0,
                'recommended': False, 'supported': False,
                'note': config.get('note', '対応不可'),
                'configurable': config.get('configurable', False)
            }
        
        return config
    
    # フォールバック
    return {
        'max_rows': 4, 'max_columns': 4, 'max_sides': 2,
        'ports_per_block': 32, 'default_blocks': 3,
        'recommended': False, 'supported': True,
        'note': 'デフォルト構成（要確認）',
        'configurable': True
    }

def initialize_session_state_safely():
    """Session Stateを安全に初期化（修正版）"""
    try:
        import streamlit as st
        
        defaults = {
            # アプリ全体の状態
            'debug_logs': [],
            'analysis_count': 0,
            'admin_logged_in': False,
            'current_page': '📊 データ分析',
            'show_sidebar': True,
            
            # OmniSorter 固有の状態
            'daily_orders': 100,
            'pieces_per_order': 2.5,
            'daily_volume': 250,
            'product_length': 300,
            'product_width': 250,
            'product_height': 150,
            'product_weight': 1000,
            'required_ports': 80,
            'data_source': '手動入力',
            'has_detailed_analysis': False,
            'peak_ratio': 1.0,
            'working_hours': 8.0,
            
            # 計算結果の保存
            'calculation_results': None,
            'last_analysis_result': None,
            'analysis_data_available': False,
            
            # 設定関連
            'container_model_matrix': None,
            'omnisorter_specs': None,
            
            # 管理者関連
            'admin_user': '',
            'admin_page': ''
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
        
        # 設定の初期化（初回のみ）- YAMLから読み込み、失敗時はデフォルト値
        if st.session_state.get('container_model_matrix') is None:
            st.session_state['container_model_matrix'] = get_container_matrix()

        if st.session_state.get('omnisorter_specs') is None:
            st.session_state['omnisorter_specs'] = get_omnisorter_specs()
            
    except Exception as e:
        print(f"Session state initialization error: {str(e)}")

