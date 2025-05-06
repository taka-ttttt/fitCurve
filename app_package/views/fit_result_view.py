import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from ..models.stress_strain_curve import StressStrainCurve
from ..models.ludwik_law import LudwikLaw
from ..models.swift_law import SwiftLaw
from ..storage import Storage


def render(storage: Storage):
    """
    ・フィッティング結果がなければ何もしない
    ・フィッティングした曲線をグラフ表示
    """
    # データの取得
    ss_curve = storage.get_state(storage.Key.SS_CURVE)
    fitted_ludwik_curve = storage.get_state(storage.Key.LUDWIK_LAW)
    fitted_swift_curve = storage.get_state(storage.Key.SWIFT_LAW)
    fitted_voce_curve = storage.get_state(storage.Key.VOCE_LAW)
    if fitted_ludwik_curve is None or ss_curve is None:
        return
    
    st.subheader("フィッティング結果")

    # グラフ表示
    # 元データ取得
    plastic_df = ss_curve.get_plastic_data()

    # フィッティング曲線のデータ取得
    strain_range = (0.0, 0.1)
    num_points = 20
    detail_range = (0.0, 0.05)
    detail_points = 50
    ludwik_df = fitted_ludwik_curve.get_plot_data(strain_range, num_points, detail_range, detail_points)
    swift_df = fitted_swift_curve.get_plot_data(strain_range, num_points, detail_range, detail_points)
    voce_df = fitted_voce_curve.get_plot_data(strain_range, num_points, detail_range, detail_points)

    plot_plastic_curve(plastic_df, ludwik_df, swift_df, voce_df)

    # フィッティング結果表示
    ludwik_result = (
        f"### Ludwik則\n"
        f"- **k** = {fitted_ludwik_curve.k:.3f}\n"
        f"- **n** = {fitted_ludwik_curve.n:.3f}\n"
        f"- **R²** = {fitted_ludwik_curve.calculate_r_squared(ss_curve.plastic_strain, ss_curve.true_stress):.3f}"
    )
    
    swift_result = (
        f"### Swift則\n"
        f"- **alpha** = {fitted_swift_curve.alpha:.3f}\n"
        f"- **n** = {fitted_swift_curve.n:.3f}\n"
        f"- **R²** = {fitted_swift_curve.calculate_r_squared(ss_curve.plastic_strain, ss_curve.true_stress):.3f}"
    )

    voce_result = (
        f"### Voce則\n"
        f"- **stress_infinite** = {fitted_voce_curve.stress_infinite:.3f}\n"
        f"- **h** = {fitted_voce_curve.h:.3f}\n"
        f"- **R²** = {fitted_voce_curve.calculate_r_squared(ss_curve.plastic_strain, ss_curve.true_stress):.3f}"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(ludwik_result)
    with col2:
        st.markdown(swift_result)
    with col3:
        st.markdown(voce_result)

    # CSVエクスポート設定
    st.subheader("CSVエクスポート設定")

    # ひずみ範囲
    all_strain_range = st.slider(
        "ひずみ範囲 (ε の範囲)",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 0.5),
        step=0.001,
        format="%.3f",
        key="export_strain_range"
    )

    # データ数
    num_points = st.number_input(
        "データ数",
        min_value=10,
        max_value=1000,
        value=20,
        step=1,
        key="export_num_points"
    )
    
    # 詳細データ範囲
    detail_strain_range = st.slider(
        "詳細データ範囲 (ε の範囲)",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 0.05),
        step=0.001,
        format="%.3f",
        key="export_detail_strain_range"
    )

    # 詳細データ数
    detail_points = st.number_input(
        "詳細データ数",
        min_value=10,
        max_value=1000,
        value=50,
        step=1,
        key="export_detail_points"
    )

    if st.button("データ設定の更新"):
        export_ludwik_df = fitted_ludwik_curve.get_plot_data(all_strain_range, num_points, detail_strain_range, detail_points)
        export_swift_df = fitted_swift_curve.get_plot_data(all_strain_range, num_points, detail_strain_range, detail_points)
        export_voce_df = fitted_voce_curve.get_plot_data(all_strain_range, num_points, detail_strain_range, detail_points)
        storage.update_export_data(export_ludwik_df, export_swift_df, export_voce_df)
        st.success("データ設定を更新しました")

    # エクスポートデータのプレビュー
    st.subheader("エクスポートデータのプレビュー")
    export_ludwik_df = storage.get_state(storage.Key.EXPORT_LUDWIK_DATA)
    export_swift_df = storage.get_state(storage.Key.EXPORT_SWIFT_DATA)
    export_voce_df = storage.get_state(storage.Key.EXPORT_VOCE_DATA)
    if export_ludwik_df is None or export_swift_df is None or export_voce_df is None:
        return
    
    # エクスポートデータのテーブル表示
    # st.dataframe(export_ludwik_df)
    # st.dataframe(export_swift_df)

    # エクスポートデータのグラフ表示
    plot_export_data(export_ludwik_df, export_swift_df, export_voce_df)

    # CSVダウンロード
    csv_ludwik = export_ludwik_df.to_csv(index=False)
    st.download_button(
        "Ludwik則のCSVダウンロード",
        csv_ludwik,
        file_name="ludwik_law_data.csv",
        mime="text/csv"
    )
    csv_swift = export_swift_df.to_csv(index=False)
    st.download_button(
        "Swift則のCSVダウンロード",
        csv_swift,
        file_name="swift_law_data.csv",
        mime="text/csv"
    )
    csv_voce = export_voce_df.to_csv(index=False)
    st.download_button(
        "Voce則のCSVダウンロード",
        csv_voce,
        file_name="voce_law_data.csv",
        mime="text/csv"
    )


def plot_plastic_curve(plastic_df: pd.DataFrame, ludwik_df: pd.DataFrame, swift_df: pd.DataFrame, voce_df: pd.DataFrame):
    """塑性ひずみ-真応力曲線のグラフを表示"""

    # グラフ設定
    fig, ax = plt.subplots(figsize=(10, 6))
    marker_size = 3
    line_width = 1.5
    
    # 塑性ひずみ-真応力曲線
    ax.plot(plastic_df[f"{plastic_df.columns[0]}"], 
            plastic_df[f"{plastic_df.columns[1]}"], 
            'o-', markersize=marker_size*2, linewidth=line_width*3, 
            color='gray', label="Experimental")
    
    ax.plot(ludwik_df[f"{ludwik_df.columns[0]}"], 
            ludwik_df[f"{ludwik_df.columns[1]}"], 
            '--', markersize=marker_size, linewidth=line_width, 
            color='blue', label="Ludwik")
    
    ax.plot(swift_df[f"{swift_df.columns[0]}"], 
            swift_df[f"{swift_df.columns[1]}"], 
            '--', markersize=marker_size, linewidth=line_width, 
            color='red', label="Swift")

    ax.plot(voce_df[f"{voce_df.columns[0]}"], 
            voce_df[f"{voce_df.columns[1]}"], 
            '--', markersize=marker_size, linewidth=line_width, 
            color='green', label="Voce")
            
    # 軸とグリッドの設定
    ax.set_xlabel(f"{plastic_df.columns[0]}")
    ax.set_ylabel(f"{plastic_df.columns[1]}")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # グラフ表示
    st.pyplot(fig)


def plot_export_data(export_ludwik_df: pd.DataFrame, export_swift_df: pd.DataFrame, export_voce_df: pd.DataFrame):
    """エクスポートデータのグラフを表示"""
    # グラフ設定
    fig, ax = plt.subplots(figsize=(10, 6))
    marker_size = 2
    line_width = 1
    
    # 塑性ひずみ-真応力曲線   
    ax.plot(export_ludwik_df["strain"], 
            export_ludwik_df["stress"], 
            'o-', markersize=marker_size, linewidth=line_width, 
            color='blue', label="Ludwik" )
    ax.plot(export_swift_df["strain"], 
            export_swift_df["stress"], 
            'o-', markersize=marker_size, linewidth=line_width, 
            color='red', label="Swift")
    ax.plot(export_voce_df["strain"], 
            export_voce_df["stress"], 
            'o-', markersize=marker_size, linewidth=line_width, 
            color='green', label="Voce")
            
    # 軸とグリッドの設定
    ax.set_xlabel(f"{export_ludwik_df.columns[0]}")
    ax.set_ylabel(f"{export_ludwik_df.columns[1]}")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # グラフ表示
    st.pyplot(fig)











    # 結果表示
    # if storage.get_state(storage.key_result_ready):
    #     result = storage.get_fit_result()
    #     st.markdown(f"- **k** = {result.k:.3f}  \n- **n** = {result.n:.3f}")

    #     # CSV ダウンロード
    #     df = pd.DataFrame({
    #         "parameter": ["k", "n"],
    #         "value": [result.k, result.n]
    #     })
    #     csv = df.to_csv(index=False)
    #     st.download_button(
    #         "結果を CSV ダウンロード",
    #         csv,
    #         file_name="fit_result.csv",
    #         mime="text/csv"
    #     )
