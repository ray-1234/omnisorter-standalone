"""
OmniSorter 設定読み込みモジュール

YAML設定ファイルの読み込み、バリデーション、フォールバック処理を提供
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import yaml

# 設定ファイルのデフォルトパス
CONFIG_DIR = Path(__file__).parent.parent / "config"
SPECS_FILE = CONFIG_DIR / "omnisorter_specs.yaml"
MATRIX_FILE = CONFIG_DIR / "container_model_matrix.yaml"
APP_SETTINGS_FILE = CONFIG_DIR / "app_settings.yaml"


class ConfigLoadError(Exception):
    """設定読み込みエラー"""
    pass


class ConfigValidationError(Exception):
    """設定バリデーションエラー"""
    pass


def _load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    YAMLファイルを読み込む

    Args:
        file_path: YAMLファイルのパス

    Returns:
        読み込んだ辞書データ

    Raises:
        ConfigLoadError: ファイル読み込みエラー
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise ConfigLoadError(f"設定ファイルが見つかりません: {file_path}")
    except yaml.YAMLError as e:
        raise ConfigLoadError(f"YAML解析エラー: {file_path} - {str(e)}")


def _validate_omnisorter_specs(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    機種スペックデータのバリデーション

    Args:
        data: 読み込んだスペックデータ

    Returns:
        (成功フラグ, エラーメッセージのリスト)
    """
    errors = []

    if 'models' not in data:
        errors.append("'models' キーが存在しません")
        return False, errors

    required_fields = ['name', 'dimensions', 'maxProduct', 'processingCapacity', 'totalPorts', 'priority']
    dimension_fields = ['L', 'W', 'H']
    max_product_fields = ['L', 'W', 'H', 'weight']

    for model_id, spec in data['models'].items():
        prefix = f"機種 '{model_id}'"

        # 必須フィールドチェック
        for field in required_fields:
            if field not in spec:
                errors.append(f"{prefix}: 必須フィールド '{field}' がありません")

        # dimensions チェック
        if 'dimensions' in spec:
            for dim in dimension_fields:
                if dim not in spec['dimensions']:
                    errors.append(f"{prefix}: dimensions.{dim} がありません")
                elif not isinstance(spec['dimensions'][dim], (int, float)):
                    errors.append(f"{prefix}: dimensions.{dim} は数値である必要があります")

        # maxProduct チェック
        if 'maxProduct' in spec:
            for field in max_product_fields:
                if field not in spec['maxProduct']:
                    errors.append(f"{prefix}: maxProduct.{field} がありません")
                elif not isinstance(spec['maxProduct'][field], (int, float)):
                    errors.append(f"{prefix}: maxProduct.{field} は数値である必要があります")

        # processingCapacity チェック
        if 'processingCapacity' in spec:
            if not isinstance(spec['processingCapacity'], (int, float)):
                errors.append(f"{prefix}: processingCapacity は数値である必要があります")
            elif spec['processingCapacity'] <= 0:
                errors.append(f"{prefix}: processingCapacity は正の数である必要があります")

        # totalPorts チェック
        if 'totalPorts' in spec:
            if not isinstance(spec['totalPorts'], int):
                errors.append(f"{prefix}: totalPorts は整数である必要があります")
            elif spec['totalPorts'] <= 0:
                errors.append(f"{prefix}: totalPorts は正の整数である必要があります")

        # priority チェック
        if 'priority' in spec:
            if not isinstance(spec['priority'], int) or spec['priority'] < 1:
                errors.append(f"{prefix}: priority は1以上の整数である必要があります")

    return len(errors) == 0, errors


def _validate_container_matrix(data: Dict[str, Any], model_ids: List[str]) -> Tuple[bool, List[str]]:
    """
    容器マトリクスデータのバリデーション

    Args:
        data: 読み込んだマトリクスデータ
        model_ids: 有効な機種IDのリスト

    Returns:
        (成功フラグ, エラーメッセージのリスト)
    """
    errors = []

    if 'matrix' not in data:
        errors.append("'matrix' キーが存在しません")
        return False, errors

    required_config_fields = [
        'max_rows', 'max_columns', 'max_sides', 'ports_per_block',
        'default_blocks', 'recommended', 'supported'
    ]

    for model_id, containers in data['matrix'].items():
        if model_id not in model_ids:
            errors.append(f"マトリクスの機種ID '{model_id}' がスペック定義に存在しません")
            continue

        for container_type, config in containers.items():
            prefix = f"'{model_id}' - '{container_type}'"

            for field in required_config_fields:
                if field not in config:
                    errors.append(f"{prefix}: 必須フィールド '{field}' がありません")

            # 数値フィールドのチェック
            numeric_fields = ['max_rows', 'max_columns', 'max_sides', 'ports_per_block', 'default_blocks']
            for field in numeric_fields:
                if field in config and not isinstance(config[field], int):
                    errors.append(f"{prefix}: {field} は整数である必要があります")
                elif field in config and config[field] < 0:
                    errors.append(f"{prefix}: {field} は0以上である必要があります")

            # boolフィールドのチェック
            bool_fields = ['recommended', 'supported']
            for field in bool_fields:
                if field in config and not isinstance(config[field], bool):
                    errors.append(f"{prefix}: {field} は真偽値である必要があります")

    return len(errors) == 0, errors


def load_omnisorter_specs(
    file_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    機種スペックを読み込む

    Args:
        file_path: 設定ファイルのパス (省略時はデフォルト)

    Returns:
        機種スペック辞書

    Raises:
        ConfigLoadError: ファイル読み込みエラー
        ConfigValidationError: バリデーションエラー
    """
    path = file_path or SPECS_FILE

    data = _load_yaml_file(path)
    valid, errors = _validate_omnisorter_specs(data)

    if not valid:
        error_msg = "\n".join(errors)
        raise ConfigValidationError(f"スペック設定のバリデーションエラー:\n{error_msg}")

    return data['models']


def load_container_model_matrix(
    file_path: Optional[Path] = None,
    specs: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    容器マトリクスを読み込む

    Args:
        file_path: 設定ファイルのパス (省略時はデフォルト)
        specs: 機種スペック (バリデーション用、省略時は読み込み済みのものを使用)

    Returns:
        容器マトリクス辞書

    Raises:
        ConfigLoadError: ファイル読み込みエラー
        ConfigValidationError: バリデーションエラー
    """
    path = file_path or MATRIX_FILE

    data = _load_yaml_file(path)

    # バリデーション用の機種IDリストを取得
    if specs is None:
        specs = load_omnisorter_specs()
    model_ids = list(specs.keys())

    valid, errors = _validate_container_matrix(data, model_ids)

    if not valid:
        error_msg = "\n".join(errors)
        raise ConfigValidationError(f"マトリクス設定のバリデーションエラー:\n{error_msg}")

    return data['matrix']


def reload_all_configs() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    全ての設定を再読み込みする

    Returns:
        (機種スペック, 容器マトリクス) のタプル
    """
    specs = load_omnisorter_specs()
    matrix = load_container_model_matrix(specs=specs)
    return specs, matrix


def load_app_settings(file_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    アプリケーション設定を読み込む

    Args:
        file_path: 設定ファイルのパス (省略時はデフォルト)

    Returns:
        アプリケーション設定辞書
    """
    path = file_path or APP_SETTINGS_FILE

    # デフォルト設定（ファイルがない場合のフォールバック）
    defaults = {
        'calculation': {
            'target_utilization': 0.95,
            'target_rotation': 6
        },
        'scoring': {
            'model_priority': {'S': 100, 'M': 50, 'L': 25, 'mini_small': 150, 'mini_large': 10},
            'mini_threshold_pcs': 3000,
            'container_recommended_bonus': 20,
            'utilization': {
                'optimal_min': 60, 'optimal_max': 85, 'optimal_bonus': 15,
                'high_max': 95, 'high_bonus': 10, 'overload_penalty': -10
            },
            'cost_penalty': {'units_penalty': 30, 'ports_penalty': 0.1, 'ports_baseline': 40}
        },
        'ui_defaults': {
            'daily_orders': 1000,
            'pieces_per_order': 2.0,
            'working_hours': 8.0,
            'product_length': 300,
            'product_width': 200,
            'product_height': 150,
            'product_weight': 1.5,
            'peak_ratio_options': [1.0, 1.2, 1.5, 2.0, 2.5, 3.0]
        },
        'display': {
            'utilization_thresholds': {'warning': 85, 'danger': 95},
            'target_utilization_display': '60-85%',
            'batch_mode_max_pcs': 10
        }
    }

    if not path.exists():
        return defaults

    try:
        data = _load_yaml_file(path)
        # デフォルト値とマージ（ファイルの値を優先）
        def deep_merge(base, override):
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        return deep_merge(defaults, data)
    except ConfigLoadError:
        return defaults


def get_config_info() -> Dict[str, Any]:
    """
    設定ファイルの情報を取得

    Returns:
        設定ファイルの情報辞書
    """
    return {
        'config_dir': str(CONFIG_DIR),
        'specs_file': str(SPECS_FILE),
        'specs_exists': SPECS_FILE.exists(),
        'matrix_file': str(MATRIX_FILE),
        'matrix_exists': MATRIX_FILE.exists(),
        'app_settings_file': str(APP_SETTINGS_FILE),
        'app_settings_exists': APP_SETTINGS_FILE.exists()
    }
