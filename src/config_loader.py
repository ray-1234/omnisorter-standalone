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

    required_fields = ['name', 'dimensions', 'maxProduct', 'capacity', 'priority']
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

        # capacity チェック
        if 'capacity' in spec:
            if 'min' not in spec['capacity'] or 'max' not in spec['capacity']:
                errors.append(f"{prefix}: capacity には min と max が必要です")
            elif spec['capacity']['min'] > spec['capacity']['max']:
                errors.append(f"{prefix}: capacity.min は capacity.max 以下である必要があります")

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
    file_path: Optional[Path] = None,
    fallback_to_default: bool = True
) -> Dict[str, Any]:
    """
    機種スペックを読み込む

    Args:
        file_path: 設定ファイルのパス (省略時はデフォルト)
        fallback_to_default: 読み込み失敗時にデフォルト値を返すか

    Returns:
        機種スペック辞書
    """
    from src.omnisorter_common import get_default_omnisorter_specs

    path = file_path or SPECS_FILE

    try:
        data = _load_yaml_file(path)
        valid, errors = _validate_omnisorter_specs(data)

        if not valid:
            error_msg = "\n".join(errors)
            if fallback_to_default:
                print(f"警告: スペック設定にエラーがあります。デフォルト値を使用します。\n{error_msg}")
                return get_default_omnisorter_specs()
            raise ConfigValidationError(f"スペック設定のバリデーションエラー:\n{error_msg}")

        return data['models']

    except ConfigLoadError as e:
        if fallback_to_default:
            print(f"警告: {str(e)} - デフォルト値を使用します。")
            return get_default_omnisorter_specs()
        raise


def load_container_model_matrix(
    file_path: Optional[Path] = None,
    specs: Optional[Dict[str, Any]] = None,
    fallback_to_default: bool = True
) -> Dict[str, Any]:
    """
    容器マトリクスを読み込む

    Args:
        file_path: 設定ファイルのパス (省略時はデフォルト)
        specs: 機種スペック (バリデーション用、省略時は読み込み済みのものを使用)
        fallback_to_default: 読み込み失敗時にデフォルト値を返すか

    Returns:
        容器マトリクス辞書
    """
    from src.omnisorter_common import get_default_container_model_matrix

    path = file_path or MATRIX_FILE

    try:
        data = _load_yaml_file(path)

        # バリデーション用の機種IDリストを取得
        if specs is None:
            specs = load_omnisorter_specs(fallback_to_default=True)
        model_ids = list(specs.keys())

        valid, errors = _validate_container_matrix(data, model_ids)

        if not valid:
            error_msg = "\n".join(errors)
            if fallback_to_default:
                print(f"警告: マトリクス設定にエラーがあります。デフォルト値を使用します。\n{error_msg}")
                return get_default_container_model_matrix()
            raise ConfigValidationError(f"マトリクス設定のバリデーションエラー:\n{error_msg}")

        return data['matrix']

    except ConfigLoadError as e:
        if fallback_to_default:
            print(f"警告: {str(e)} - デフォルト値を使用します。")
            return get_default_container_model_matrix()
        raise


def reload_all_configs() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    全ての設定を再読み込みする

    Returns:
        (機種スペック, 容器マトリクス) のタプル
    """
    specs = load_omnisorter_specs()
    matrix = load_container_model_matrix(specs=specs)
    return specs, matrix


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
        'matrix_exists': MATRIX_FILE.exists()
    }
