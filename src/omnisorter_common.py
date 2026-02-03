"""OmniSorter関連の共通関数・定数を定義（修正版）"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


def get_omnisorter_specs() -> Dict:
    """
    OmniSorter仕様を取得（YAMLから読み込み、フォールバック付き）

    Returns:
        機種スペック辞書
    """
    try:
        from src.config_loader import load_omnisorter_specs
        return load_omnisorter_specs(fallback_to_default=True)
    except ImportError:
        # config_loader が利用できない場合はデフォルト値を返す
        return get_default_omnisorter_specs()


def get_container_matrix() -> Dict:
    """
    容器×機種マトリクスを取得（YAMLから読み込み、フォールバック付き）

    Returns:
        容器マトリクス辞書
    """
    try:
        from src.config_loader import load_container_model_matrix
        return load_container_model_matrix(fallback_to_default=True)
    except ImportError:
        # config_loader が利用できない場合はデフォルト値を返す
        return get_default_container_model_matrix()


def get_default_omnisorter_specs():
    """デフォルトのOmniSorter仕様を返す（統一版）"""
    return {
        'mini-cart': {
            'name': 'OmniSorter mini（カート式）',
            'dimensions': {'L': 5.6, 'W': 2.6, 'H': 2.2},
            'maxProduct': {'L': 400, 'W': 320, 'H': 150, 'weight': 5000},
            'capacity': {'min': 800, 'max': 1000},
            'blocks': 2,
            'ports': 80,
            'portsConfig': {'rows': 4, 'columns': 5, 'sides': 2},
            'robotSpeed': '全体で800-1000pcs/時',
            'powerRequirement': '3相200V, 50/60Hz, 約3.5kW',
            'features': ['省スペース', 'カート移動', '短納期導入'],
            'unitCapacity': 1000,
            'supportedContainers': ['標準トート'],
            'priority': 6
        },
        'mini-fixed': {
            'name': 'OmniSorter mini（固定式）',
            'dimensions': {'L': 5.6, 'W': 2.6, 'H': 2.2},
            'maxProduct': {'L': 400, 'W': 320, 'H': 180, 'weight': 5000},
            'capacity': {'min': 800, 'max': 1000},
            'blocks': 2,
            'ports': 60,
            'portsConfig': {'rows': 3, 'columns': 5, 'sides': 2},
            'robotSpeed': '全体で800-1000pcs/時',
            'powerRequirement': '3相200V, 50/60Hz, 約3.5kW',
            'features': ['省スペース', '固定式安定性', '短納期導入'],
            'unitCapacity': 1000,
            'supportedContainers': ['オリコン30L', 'オリコン40L', 'オリコン50L'],
            'priority': 5
        },
        'S': {
            'name': 'OmniSorter Sサイズ（標準機）',
            'dimensions': {'L': 11.7, 'W': 3.4, 'H': 2.5},
            'maxProduct': {'L': 400, 'W': 320, 'H': 200, 'weight': 5000},
            'capacity': {'min': 1200, 'max': 1500},
            'capacity_by_blocks': {
                1: {'min': 800, 'max': 1000},
                2: {'min': 1000, 'max': 1200},
                3: {'min': 1200, 'max': 1500}
            },
            'blocks': {'min': 1, 'max': 10},
            'portsPerBlock': {'rows': 4, 'columns': 5, 'sides': 2},
            'robotSpeed': '1台あたり1200-1500pcs/時（3ブロック以上推奨）',
            'powerRequirement': '3相200V, 50/60Hz, 約7.5kW（4ブロック時）',
            'features': ['コンパクト設置', '高速仕分け', '拡張性'],
            'unitCapacity': 1500,
            'supportedContainers': ['標準トート', 'オリコン30L', 'オリコン40L', 'オリコン50L'],
            'priority': 4
        },
        'M': {
            'name': 'OmniSorter Mサイズ（標準機）',
            'dimensions': {'L': 13.0, 'W': 4.4, 'H': 2.5},
            'maxProduct': {'L': 500, 'W': 410, 'H': 200, 'weight': 5000},
            'capacity': {'min': 1200, 'max': 1500},
            'capacity_by_blocks': {
                1: {'min': 800, 'max': 1000},
                2: {'min': 1000, 'max': 1200},
                3: {'min': 1200, 'max': 1500}
            },
            'blocks': {'min': 1, 'max': 10},
            'portsPerBlock': {'rows': 5, 'columns': 5, 'sides': 2},
            'robotSpeed': '1台あたり1200-1500pcs/時（3ブロック以上推奨）',
            'powerRequirement': '3相200V, 50/60Hz, 約9.0kW（4ブロック時）',
            'features': ['中型商品対応', '高処理能力', '柔軟性'],
            'unitCapacity': 1500,
            'supportedContainers': ['標準トート', 'オリコン30L', 'オリコン40L', 'オリコン50L'],
            'priority': 2
        },
        'L': {
            'name': 'OmniSorter Lサイズ（標準機）',
            'dimensions': {'L': 14.7, 'W': 6.1, 'H': 2.5},
            'maxProduct': {'L': 750, 'W': 500, 'H': 200, 'weight': 8000},
            'capacity': {'min': 1200, 'max': 1500},
            'capacity_by_blocks': {
                1: {'min': 800, 'max': 1000},
                2: {'min': 1000, 'max': 1200},
                3: {'min': 1200, 'max': 1500}
            },
            'blocks': {'min': 1, 'max': 10},
            'portsPerBlock': {'rows': 4, 'columns': 4, 'sides': 2},
            'robotSpeed': '1台あたり1200-1500pcs/時（3ブロック以上推奨）',
            'powerRequirement': '3相200V, 50/60Hz, 約12.0kW（4ブロック時）',
            'features': ['大型商品対応', '重量物対応', '高耐久性'],
            'unitCapacity': 1500,
            'supportedContainers': ['標準トート', 'オリコン30L', 'オリコン40L', 'オリコン50L'],
            'priority': 1
        }
    }

def get_default_container_model_matrix():
    """デフォルトの容器×機種マトリクスを返す（管理者設定可能版）"""
    return {
        'mini-cart': {
            '標準トート': {
                'max_rows': 4,
                'max_columns': 5,
                'max_sides': 2,
                'ports_per_block': 40,
                'default_blocks': 2,
                'recommended': True,
                'supported': True,
                'note': 'カート式標準構成',
                'configurable': True
            },
            'オリコン30L': {
                'max_rows': 0,
                'max_columns': 0,
                'max_sides': 0,
                'ports_per_block': 0,
                'default_blocks': 0,
                'recommended': False,
                'supported': False,
                'note': 'カート式では対応不可',
                'configurable': False
            },
            'オリコン40L': {
                'max_rows': 0,
                'max_columns': 0,
                'max_sides': 0,
                'ports_per_block': 0,
                'default_blocks': 0,
                'recommended': False,
                'supported': False,
                'note': 'カート式では対応不可',
                'configurable': False
            },
            'オリコン50L': {
                'max_rows': 0,
                'max_columns': 0,
                'max_sides': 0,
                'ports_per_block': 0,
                'default_blocks': 0,
                'recommended': False,
                'supported': False,
                'note': 'カート式では対応不可',
                'configurable': False
            }
        },
        'mini-fixed': {
            '標準トート': {
                'max_rows': 0,
                'max_columns': 0,
                'max_sides': 0,
                'ports_per_block': 0,
                'default_blocks': 0,
                'recommended': False,
                'supported': False,
                'note': '固定式ではトート標準対応不可',
                'configurable': False
            },
            'オリコン30L': {
                'max_rows': 3,
                'max_columns': 5,
                'max_sides': 2,
                'ports_per_block': 30,
                'default_blocks': 2,
                'recommended': True,
                'supported': True,
                'note': '固定式標準構成',
                'configurable': True
            },
            'オリコン40L': {
                'max_rows': 3,
                'max_columns': 4,
                'max_sides': 2,
                'ports_per_block': 24,
                'default_blocks': 2,
                'recommended': True,
                'supported': True,
                'note': '中型容器対応',
                'configurable': True
            },
            'オリコン50L': {
                'max_rows': 3,
                'max_columns': 4,
                'max_sides': 2,
                'ports_per_block': 24,
                'default_blocks': 2,
                'recommended': False,
                'supported': True,
                'note': '大型容器・制約あり',
                'configurable': True
            }
        },
        'S': {
            '標準トート': {
                'max_rows': 5,
                'max_columns': 5,
                'max_sides': 2,
                'ports_per_block': 50,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'S型標準構成',
                'configurable': True
            },
            'オリコン30L': {
                'max_rows': 5,
                'max_columns': 5,
                'max_sides': 2,
                'ports_per_block': 50,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'S型・30L対応',
                'configurable': True
            },
            'オリコン40L': {
                'max_rows': 4,
                'max_columns': 4,
                'max_sides': 2,
                'ports_per_block': 32,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'S型・40L対応',
                'configurable': True
            },
            'オリコン50L': {
                'max_rows': 3,
                'max_columns': 4,
                'max_sides': 2,
                'ports_per_block': 24,
                'default_blocks': 4,
                'recommended': False,
                'supported': True,
                'note': 'S型・50L制約あり',
                'configurable': True
            }
        },
        'M': {
            '標準トート': {
                'max_rows': 5,
                'max_columns': 5,
                'max_sides': 2,
                'ports_per_block': 50,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'M型標準構成',
                'configurable': True
            },
            'オリコン30L': {
                'max_rows': 5,
                'max_columns': 5,
                'max_sides': 2,
                'ports_per_block': 50,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'M型・30L対応',
                'configurable': True
            },
            'オリコン40L': {
                'max_rows': 4,
                'max_columns': 5,
                'max_sides': 2,
                'ports_per_block': 40,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'M型・40L対応',
                'configurable': True
            },
            'オリコン50L': {
                'max_rows': 4,
                'max_columns': 4,
                'max_sides': 2,
                'ports_per_block': 32,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'M型・50L対応',
                'configurable': True
            }
        },
        'L': {
            '標準トート': {
                'max_rows': 4,
                'max_columns': 4,
                'max_sides': 2,
                'ports_per_block': 32,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'L型標準構成（4×4制限）',
                'configurable': True
            },
            'オリコン30L': {
                'max_rows': 4,
                'max_columns': 4,
                'max_sides': 2,
                'ports_per_block': 32,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'L型・30L対応',
                'configurable': True
            },
            'オリコン40L': {
                'max_rows': 4,
                'max_columns': 4,
                'max_sides': 2,
                'ports_per_block': 32,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'L型・40L対応',
                'configurable': True
            },
            'オリコン50L': {
                'max_rows': 4,
                'max_columns': 4,
                'max_sides': 2,
                'ports_per_block': 32,
                'default_blocks': 4,
                'recommended': True,
                'supported': True,
                'note': 'L型・50L対応',
                'configurable': True
            }
        }
    }

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
            matrix = get_default_container_model_matrix()
    
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

def extract_omnisorter_insights(analysis_result):
    """分析結果からOmniSorter用のインサイトを抽出（安全版）"""
    insights = {
        'dailyOrders': 0,
        'avgPiecesPerOrder': 1.0,
        'maxLength': 300,
        'maxWidth': 250,
        'maxHeight': 150,
        'maxWeight': 1000,
        'recommendations': [],
        'peakRatio': 1.0,
        'peakDailyOrders': 0,
        'totalRecords': 0,
        'hasDetailedAnalysis': False
    }
    
    if not analysis_result or analysis_result.get('status') != 'success':
        return insights
    
    try:
        # 強化された日別サマリーから詳細分析
        enhanced_summary = analysis_result.get('enhanced_daily_summary', {})
        
        if enhanced_summary and enhanced_summary.get('data_overview'):
            overview = enhanced_summary['data_overview']
            insights['totalRecords'] = overview.get('total_rows', 0)
            insights['hasDetailedAnalysis'] = True
        
        daily_summaries = enhanced_summary.get('daily_summaries', {})
        
        if daily_summaries:
            # 最初の温度帯のサマリーを使用
            main_summary_key = list(daily_summaries.keys())[0]
            daily_data = daily_summaries[main_summary_key]
            
            if daily_data:
                daily_df = pd.DataFrame(daily_data)
                # 統計行を除外
                data_rows = daily_df[~daily_df['日付'].isin(['平均', '合計', '最大'])].copy()
                
                if len(data_rows) > 0:
                    # 件数データから日次出荷件数を計算
                    if '件数' in data_rows.columns:
                        insights['dailyOrders'] = int(data_rows['件数'].mean())
                        
                        # ピーク比率の計算
                        if len(data_rows) > 1:
                            max_orders = data_rows['件数'].max()
                            avg_orders = data_rows['件数'].mean()
                            insights['peakRatio'] = max_orders / avg_orders if avg_orders > 0 else 1
                            insights['peakDailyOrders'] = int(max_orders)
                    
                    # 平均ピース数の計算
                    if '総出荷数' in data_rows.columns and '件数' in data_rows.columns:
                        total_pieces = data_rows['総出荷数'].sum()
                        total_orders = data_rows['件数'].sum()
                        if total_orders > 0:
                            insights['avgPiecesPerOrder'] = round(total_pieces / total_orders, 2)
        
        # ABC分析から商品サイズの推定
        abc_summary = analysis_result.get('abc_summary', [])
        if abc_summary:
            total_skus = len(abc_summary)
            
            # SKU数に基づく商品サイズ推定
            if total_skus > 1000:
                # 多品種小物（EC系）
                insights.update({
                    'maxLength': 300, 'maxWidth': 200, 'maxHeight': 120, 'maxWeight': 800
                })
                insights['recommendations'].append('多品種小物（EC系）：mini版推奨')
            elif total_skus > 100:
                # 中規模
                insights.update({
                    'maxLength': 400, 'maxWidth': 300, 'maxHeight': 150, 'maxWeight': 1500
                })
                insights['recommendations'].append('中規模品揃え：mini版またはS型推奨')
            else:
                # 少品種大型（BtoB系）
                insights.update({
                    'maxLength': 500, 'maxWidth': 400, 'maxHeight': 180, 'maxWeight': 3000
                })
                insights['recommendations'].append('少品種大型（BtoB系）：標準機推奨')
        
        # 業務パターンの推定
        avg_pieces = insights['avgPiecesPerOrder']
        if avg_pieces < 2:
            insights['recommendations'].append('EC型（小ロット高頻度）：mini版カート式を推奨')
        elif avg_pieces < 5:
            insights['recommendations'].append('EC型（中ロット）：mini版またはS型を推奨')
        elif avg_pieces > 15:
            insights['recommendations'].append('BtoB型（大ロット）：標準機（S/M/L型）を推奨')
        
        # ピーク変動の分析
        if insights['peakRatio'] > 2:
            insights['recommendations'].append(f"ピーク変動大（平均の{insights['peakRatio']:.1f}倍）：余裕のある設計を推奨")
        elif insights['peakRatio'] > 1.5:
            insights['recommendations'].append(f"ピーク変動あり（平均の{insights['peakRatio']:.1f}倍）：適切な間口数設計が重要")
        
    except Exception as e:
        print(f"OmniSorter分析中にエラー: {str(e)}")
    
    return insights

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

def handle_omnisorter_error(error, context="OmniSorter処理"):
    """OmniSorter関連エラーの統一ハンドリング（安全版）"""
    try:
        import streamlit as st
        
        error_message = f"{context}中にエラーが発生しました: {str(error)}"
        
        # デバッグログに記録
        if 'debug_logs' not in st.session_state:
            st.session_state['debug_logs'] = []
        st.session_state['debug_logs'].append(f"ERROR: {error_message}")
        
        # ユーザーに分かりやすいメッセージを表示
        st.error(error_message)
        st.info("エラーが続く場合は、ページを再読み込みしてください。")
        
    except Exception as display_error:
        print(f"Error displaying error message: {str(display_error)}")
    
    return None

def validate_container_config(model_id, container_type, config):
    """容器構成の妥当性をチェック（安全版）"""
    validation_results = []
    
    try:
        # 基本的なバリデーション
        if config.get('max_rows', 0) < 0:
            validation_results.append("段数は0以上である必要があります")
        
        if config.get('max_columns', 0) < 0:
            validation_results.append("列数は0以上である必要があります")
        
        if config.get('max_sides', 0) not in [0, 1, 2]:
            validation_results.append("面数は0、1、または2である必要があります")
        
        if config.get('default_blocks', 0) < 0:
            validation_results.append("デフォルトブロック数は0以上である必要があります")
        
        # 物理的制約のチェック
        total_ports = (config.get('max_rows', 0) * 
                      config.get('max_columns', 0) * 
                      config.get('max_sides', 0))
        
        if config.get('supported', False) and total_ports == 0:
            validation_results.append("対応可能な場合、間口数は1以上である必要があります")
        
        # 機種固有の制約チェック
        if model_id == 'mini-cart' and container_type != '標準トート':
            if config.get('supported', False):
                validation_results.append("mini-cart はトート標準のみ対応可能です")
        
        if model_id == 'mini-fixed' and container_type == '標準トート':
            if config.get('supported', False):
                validation_results.append("mini-fixed はトート標準に対応できません")
        
    except Exception as e:
        validation_results.append(f"バリデーション中にエラー: {str(e)}")
    
    return validation_results

def get_physical_constraints():
    """物理的制約情報を返す（安全版）"""
    return {
        'mini-cart': {
            'max_total_ports': 80,
            'supported_containers': ['標準トート'],
            'fixed_configuration': True,
            'notes': 'カート式は構成が固定されています'
        },
        'mini-fixed': {
            'max_total_ports': 60,
            'supported_containers': ['オリコン30L', 'オリコン40L', 'オリコン50L'],
            'fixed_configuration': True,
            'notes': '固定式は構成が固定されています'
        },
        'S': {
            'max_total_ports': 800,
            'supported_containers': ['標準トート', 'オリコン30L', 'オリコン40L', 'オリコン50L'],
            'fixed_configuration': False,
            'max_rows_per_block': 5,
            'max_columns_per_block': 5,
            'notes': 'ブロック構成により拡張可能'
        },
        'M': {
            'max_total_ports': 1000,
            'supported_containers': ['標準トート', 'オリコン30L', 'オリコン40L', 'オリコン50L'],
            'fixed_configuration': False,
            'max_rows_per_block': 5,
            'max_columns_per_block': 5,
            'notes': 'ブロック構成により拡張可能'
        },
        'L': {
            'max_total_ports': 640,
            'supported_containers': ['標準トート', 'オリコン30L', 'オリコン40L', 'オリコン50L'],
            'fixed_configuration': False,
            'max_rows_per_block': 4,
            'max_columns_per_block': 4,
            'notes': '4×4制限により間口数に上限あり'
        }
    }

def get_recommended_configuration(daily_orders, avg_pieces_per_order, product_specs=None):
    """推奨構成を算出する（安全版）"""
    recommendations = []
    
    try:
        # 処理量の計算
        daily_volume = daily_orders * avg_pieces_per_order
        
        # 設定から機種仕様を取得
        specs = safe_get_session_value('omnisorter_specs', get_default_omnisorter_specs())
        matrix = safe_get_session_value('container_model_matrix', get_default_container_model_matrix())
        
        # 処理量に基づく基本推奨
        if daily_volume <= 2000:
            # 小規模：mini版推奨
            for model in ['mini-cart', 'mini-fixed']:
                if model in specs:
                    model_spec = specs[model]
                    supported_containers = model_spec.get('supportedContainers', [])
                    for container in supported_containers:
                        config = get_container_model_config(model, container, matrix)
                        if config['supported']:
                            recommendations.append({
                                'model': model,
                                'container': container,
                                'score': 90 if config['recommended'] else 70,
                                'reason': f'小規模運用に最適（{daily_volume:.0f}pcs/日）',
                                'config': config
                            })
        
        elif daily_volume <= 8000:
            # 中規模：S型またはmini版
            for model in ['S', 'mini-cart', 'mini-fixed']:
                if model in specs:
                    model_spec = specs[model]
                    supported_containers = model_spec.get('supportedContainers', [])
                    for container in supported_containers:
                        config = get_container_model_config(model, container, matrix)
                        if config['supported']:
                            score = 85 if model == 'S' else 75
                            if config['recommended']:
                                score += 10
                            recommendations.append({
                                'model': model,
                                'container': container,
                                'score': score,
                                'reason': f'中規模運用に適合（{daily_volume:.0f}pcs/日）',
                                'config': config
                            })
        
        else:
            # 大規模：標準機推奨
            for model in ['M', 'L', 'S']:
                if model in specs:
                    model_spec = specs[model]
                    supported_containers = model_spec.get('supportedContainers', [])
                    for container in supported_containers:
                        config = get_container_model_config(model, container, matrix)
                        if config['supported']:
                            score = 95 if model in ['M', 'L'] else 80
                            if config['recommended']:
                                score += 5
                            recommendations.append({
                                'model': model,
                                'container': container,
                                'score': score,
                                'reason': f'大規模運用に対応（{daily_volume:.0f}pcs/日）',
                                'config': config
                            })
        
        # 商品仕様による調整
        if product_specs:
            length = product_specs.get('length', 300)
            width = product_specs.get('width', 250)
            height = product_specs.get('height', 150)
            weight = product_specs.get('weight', 1000)
            
            # 大型商品の場合はM/L型を優遇
            if length > 400 or width > 300 or weight > 3000:
                for rec in recommendations:
                    if rec['model'] in ['M', 'L']:
                        rec['score'] += 15
                        rec['reason'] += '（大型商品対応）'
                    elif rec['model'].startswith('mini'):
                        rec['score'] -= 20
                        rec['reason'] += '（商品サイズ制約あり）'
        
        # スコア順にソート
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
    except Exception as e:
        print(f"推奨構成計算でエラー: {str(e)}")
        # エラー時は基本的な推奨を返す
        recommendations = [{
            'model': 'S',
            'container': '標準トート',
            'score': 70,
            'reason': 'デフォルト推奨（詳細計算失敗）',
            'config': get_container_model_config('S', '標準トート')
        }]
    
    return recommendations[:5]  # 上位5つを返す

def export_container_matrix_config():
    """現在の容器マトリクス設定をエクスポート（安全版）"""
    try:
        import json
        
        matrix = safe_get_session_value('container_model_matrix', get_default_container_model_matrix())
        
        # エクスポート用のデータ構造
        export_data = {
            'version': '1.0',
            'export_date': pd.Timestamp.now().isoformat(),
            'container_model_matrix': matrix,
            'metadata': {
                'total_models': len(matrix),
                'total_combinations': sum(len(containers) for containers in matrix.values()),
                'supported_combinations': sum(
                    sum(1 for config in containers.values() if config.get('supported', False))
                    for containers in matrix.values()
                )
            }
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"エクスポートエラー: {str(e)}"

def import_container_matrix_config(import_data):
    """容器マトリクス設定をインポート（安全版）"""
    try:
        import json
        
        data = json.loads(import_data)
        
        # バージョンチェック
        if data.get('version') != '1.0':
            return False, "サポートされていないバージョンです"
        
        # データ構造の検証
        if 'container_model_matrix' not in data:
            return False, "無効なデータ形式です"
        
        new_matrix = data['container_model_matrix']
        
        # 基本的なバリデーション
        validation_errors = []
        for model_id, model_configs in new_matrix.items():
            for container_type, config in model_configs.items():
                errors = validate_container_config(model_id, container_type, config)
                validation_errors.extend(errors)
        
        if validation_errors:
            return False, f"設定にエラーがあります: {'; '.join(validation_errors[:5])}"
        
        # セッション状態を更新
        safe_set_session_value('container_model_matrix', new_matrix)
        
        return True, f"正常にインポートされました（{data['metadata']['total_combinations']}組み合わせ）"
        
    except json.JSONDecodeError:
        return False, "JSONの解析に失敗しました"
    except Exception as e:
        return False, f"インポートエラー: {str(e)}"

def get_configuration_summary():
    """現在の設定の概要を取得（安全版）"""
    try:
        matrix = safe_get_session_value('container_model_matrix', get_default_container_model_matrix())
        specs = safe_get_session_value('omnisorter_specs', get_default_omnisorter_specs())
        
        summary = {
            'models': list(specs.keys()),
            'containers': set(),
            'supported_combinations': 0,
            'recommended_combinations': 0,
            'total_combinations': 0
        }
        
        for model_id, model_configs in matrix.items():
            for container_type, config in model_configs.items():
                summary['containers'].add(container_type)
                summary['total_combinations'] += 1
                
                if config.get('supported', False):
                    summary['supported_combinations'] += 1
                
                if config.get('recommended', False):
                    summary['recommended_combinations'] += 1
        
        summary['containers'] = list(summary['containers'])
        
        return summary
        
    except Exception as e:
        return {
            'error': f"概要取得エラー: {str(e)}",
            'models': [],
            'containers': [],
            'supported_combinations': 0,
            'recommended_combinations': 0,
            'total_combinations': 0
        }