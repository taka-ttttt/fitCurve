import pandas as pd
import numpy as np
import streamlit as st
from streamlit.runtime.state import SessionStateProxy
from typing import Any
from enum import Enum

from .models.raw_data import RawData
from .models.stress_strain_curve import StressStrainCurve
from .models.fit_settings import FitSettings
from .models.ludwik_law import LudwikLaw
from .models.swift_law import SwiftLaw

from .services.fit_curve import fit_ludwik_curve, fit_swift_curve, fit_voce_curve


class Storage:
    """セッション状態を管理するクラス"""
    
    # キー定義
    class Key(Enum):
        RAW_DATA = "key_raw_data"
        SS_CURVE = "key_ss_curve"
        FIT_SETTINGS = "key_fit_settings"
        FIT_RESULT = "key_fit_result"
        LUDWIK_LAW = "key_ludwik_law"
        SWIFT_LAW = "key_swift_law"
        VOCE_LAW = "key_voce_law"
        EXPORT_LUDWIK_DATA = "key_export_ludwik_data"
        EXPORT_SWIFT_DATA = "key_export_swift_data"
        EXPORT_VOCE_DATA = "key_export_voce_data"
    
    def __init__(self, state: SessionStateProxy):
        self.state = state
        # 必要に応じて初期化
        self._initialize_keys()
    
    def _initialize_keys(self):
        """必要なキーを初期化"""
        for key in self.Key:
            if key not in self.state:
                self.state[key] = None
    
    def init_state(self, key: Key, value: Any) -> None:
        """キーを初期化"""
        if key not in self.state:
          self.state[key] = None

    def set_state(self, key: Key, value: Any, *, do_init: bool = False) -> None:
        """セッションに値を保存"""
        if do_init:
            self.init_state(key, value)
        
        self.state[key] = value
    
    def get_state(self, key: str) -> Any:
        """セッションから値を取得"""
        return self.state.get(key, None)
    
    # イベントハンドラ
    def on_file_uploaded(self, uploaded_file: str) -> None:
        """ファイルアップロード処理"""
        if uploaded_file is None:
            return
            
        try:
            df = pd.read_csv(uploaded_file)
            raw_data = RawData(df=df)
            self.set_state(self.Key.RAW_DATA, raw_data, do_init=True)
        except Exception as e:
            # エラー処理
            pass
    
    def on_raw_data_columns_selected(self, epsilon_col, sigma_col, is_percent, young_modulus, yield_stress) -> None:
        """カラム選択処理"""
        raw_data = self.get_state(self.Key.RAW_DATA)
        if raw_data is None:
            return
            
        # 生データの更新
        raw_data.epsilon_column = epsilon_col
        raw_data.sigma_column = sigma_col
        raw_data.is_strain_percent = is_percent
        raw_data.young_modulus = young_modulus
        raw_data.yield_stress = yield_stress
        self.set_state(self.Key.RAW_DATA, raw_data, do_init=True) 
        
        # 曲線データを作成して保存
        try:
            curve = StressStrainCurve(
                nominal_strain=raw_data.strain_col,
                nominal_stress=raw_data.stress_col,
                young_modulus=raw_data.young_modulus,
                yield_stress=raw_data.yield_stress
            )
            self.set_state(self.Key.SS_CURVE, curve, do_init=True)
        except Exception as e:
            # エラー処理
            pass
        
    def fit_curve_with_settings(self, settings: FitSettings) -> None:
        """フィッティング処理"""
        # 設定の保存
        try:
            self.set_state(self.Key.FIT_SETTINGS, settings, do_init=True)
        except Exception as e:
            # エラー処理
            st.error(f"フィッティング設定の保存に失敗しました: {e}")
            pass
        
        # フィッティング
        ss_curve = self.get_state(self.Key.SS_CURVE)
        if ss_curve is None:
            return
        
        try:
            fitted_ludwik_curve = fit_ludwik_curve(ss_curve, settings)
            self.set_state(self.Key.LUDWIK_LAW, fitted_ludwik_curve, do_init=True)
        except Exception as e:
            # エラー処理
            st.error(f"Ludwik則のフィッティングに失敗しました: {e}")
            pass

        try:
            fitted_swift_curve = fit_swift_curve(ss_curve, settings)
            self.set_state(self.Key.SWIFT_LAW, fitted_swift_curve, do_init=True)
        except Exception as e:
            # エラー処理
            st.error(f"Swift則のフィッティングに失敗しました: {e}")
            pass

        try:
            fitted_voce_curve = fit_voce_curve(ss_curve, settings)
            self.set_state(self.Key.VOCE_LAW, fitted_voce_curve, do_init=True)
        except Exception as e:
            # エラー処理
            st.error(f"Voce則のフィッティングに失敗しました: {e}")
            pass


    def update_export_data(self, export_ludwik_data: pd.DataFrame, export_swift_data: pd.DataFrame, export_voce_data: pd.DataFrame) -> None:
        """エクスポートデータの更新"""
        if export_ludwik_data is None or export_swift_data is None or export_voce_data is None:
            return
        self.set_state(self.Key.EXPORT_LUDWIK_DATA, export_ludwik_data, do_init=True)
        self.set_state(self.Key.EXPORT_SWIFT_DATA, export_swift_data, do_init=True)
        self.set_state(self.Key.EXPORT_VOCE_DATA, export_voce_data, do_init=True)
