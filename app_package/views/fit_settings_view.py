import streamlit as st

from ..models.fit_settings import FitSettings
from ..storage import Storage


def render(storage: Storage):
    """
    ・アップロード済みデータがなければ何もしない
    ・フィット範囲スライダー、初期推定値入力などを提供
    ・「フィッティング実行」ボタンでstorage.on_fit_settings_changed を呼び出す
    """
    # データの取得
    ss_curve = storage.get_state(storage.Key.SS_CURVE)
    if ss_curve is None:
        return

    st.subheader("フィッティング設定")

    # フィット範囲
    strain_min = float(ss_curve.plastic_strain.min())
    strain_max = float(ss_curve.plastic_strain.max())
    default_min = 0.0
    default_max = strain_max
    step = 0.001
    
    lo, hi = st.slider(
        "フィット範囲 (ε の範囲)",
        min_value=strain_min,
        max_value=strain_max,
        value=(default_min, default_max),
        step=step,
        format="%.3f",
        key="fit_range"
    )

    # 初期推定値
    k0 = st.number_input("初期推定 k", value=1.0, step=0.1, key="initial_k")
    n0 = st.number_input("初期推定 n", value=0.2, step=0.01, key="initial_n")

    # イテレーション回数制限
    max_iterations = st.number_input("イテレーション回数制限", value=1000, step=100, key="max_iterations")

    if st.button("フィッティング実行"):
        settings = FitSettings(
            fit_range=(lo, hi),
            initial_guess=(k0, n0),
            max_iterations=max_iterations
        )
        storage.fit_curve_with_settings(settings)
        st.success("フィッティングを実行しました！")