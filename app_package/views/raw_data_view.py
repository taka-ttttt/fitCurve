import streamlit as st

from ..models.raw_data import RawData
from ..storage import Storage

def render(storage: Storage):
    """
    ・アップロード済みデータ(RawData)がなければメッセージを出して何もしない
    ・生データからひずみ列と応力列、ひずみの単位、ヤング率、降伏応力を選択・入力させるUIを提供
    ・「設定を確定・更新」ボタンで選択情報にもとづきRawDataの内容を更新
    ・更新と同時に自動でSSカーブのデータ（StressStrainCurve）を作成して保存
    """
    raw_data = storage.get_state(storage.Key.RAW_DATA)
    if raw_data is None:
        st.info("まずは CSV ファイルをアップロードしてください。")
        return
    
    # データプレビュー
    st.subheader("データプレビュー")
    st.dataframe(raw_data.df.head())

    # 生データ情報の設定
    st.subheader("データの設定")
    
    cols = raw_data.df.columns.tolist()
    
    # 前回選択された値があれば、それをデフォルト値として使用
    default_epsilon = raw_data.epsilon_column if raw_data.epsilon_column else cols[0] if cols else None
    default_sigma = raw_data.sigma_column if raw_data.sigma_column else cols[1] if len(cols) > 1 else None
    
    epsilon_col = st.selectbox(
        "ひずみ列を選択", 
        cols, 
        index=cols.index(default_epsilon) if default_epsilon in cols else 0,
        key="data_epsilon_col"
    )
    
    sigma_col = st.selectbox(
        "応力列を選択", 
        cols, 
        index=cols.index(default_sigma) if default_sigma in cols else min(1, len(cols)-1),
        key="data_sigma_col"
    )

    is_strain_percent = st.checkbox(
        "ひずみの単位が[%]の場合はチェックを入れてください。",
        value=raw_data.is_strain_percent,
        key="data_is_strain_percent"
    )

    young_modulus = st.number_input(
        "ヤング率[MPa]を入力してください。",
        value=raw_data.young_modulus,
        key="data_young_modulus"
    )

    yield_stress = st.number_input(
        "降伏応力[MPa]を入力してください。",
        value=raw_data.yield_stress,
        key="data_yield_stress"
    )

    if st.button("設定を確定・更新"):
        storage.on_raw_data_columns_selected(epsilon_col, sigma_col, is_strain_percent, young_modulus, yield_stress)
        st.success("設定を保存・更新しました！")