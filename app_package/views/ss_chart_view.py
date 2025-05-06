import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from ..models.stress_strain_curve import StressStrainCurve
from ..storage import Storage


def render(storage: Storage):
    """
    応力-ひずみ曲線グラフを表示する
    
    表示内容:
    - 公称応力-ひずみ曲線と真応力-ひずみ曲線のグラフ
    - 塑性ひずみ-真応力曲線のグラフ
    - 各データのテーブル表示
    """
    # データの取得
    ss_curve = storage.get_state(storage.Key.SS_CURVE)
    if ss_curve is None:
        st.info("まずは前処理済みのデータを用意してください。")
        return
    
    st.subheader("SSカーブ")

    # 公称・真応力-ひずみ曲線のグラフ表示
    plot_nominal_and_true_curves(ss_curve)
    
    # 公称・真応力-ひずみデータのテーブル表示
    display_nominal_and_true_data_table(ss_curve)
    
    # 塑性ひずみ-真応力曲線のグラフ表示
    plot_plastic_curve(ss_curve)
    
    # 塑性ひずみ-真応力データのテーブル表示
    display_plastic_data_table(ss_curve)


def plot_nominal_and_true_curves(ss_curve: StressStrainCurve):
    """公称および真応力-ひずみ曲線のグラフを表示"""
    # データ取得
    nominal_df = ss_curve.get_nominal_data()
    true_df = ss_curve.get_true_data()

    # グラフ設定
    fig, ax = plt.subplots(figsize=(10, 6))
    marker_size = 6
    line_width = 1.5

    # 公称応力-ひずみ曲線
    ax.plot(nominal_df[f"nominal_{ss_curve.label_strain}"], 
            nominal_df[f"nominal_{ss_curve.label_stress}"], 
            'o-', markersize=marker_size, linewidth=line_width, 
            color='blue', label="nominal")
    
    # 真応力-ひずみ曲線
    ax.plot(true_df[f"true_{ss_curve.label_strain}"], 
            true_df[f"true_{ss_curve.label_stress}"], 
            's-', markersize=marker_size, linewidth=line_width, 
            color='red', label="true")
    
    # 軸とグリッドの設定
    ax.set_xlabel(f"{ss_curve.label_strain}")
    ax.set_ylabel(f"{ss_curve.label_stress}")
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # グラフ表示
    st.pyplot(fig)


def display_nominal_and_true_data_table(ss_curve: StressStrainCurve):
    """公称および真応力-ひずみデータをテーブル表示"""
    nominal_df = ss_curve.get_nominal_data()
    true_df = ss_curve.get_true_data()
    
    combined_df = pd.DataFrame({
        f"nominal {ss_curve.label_strain}": nominal_df[f"nominal_{ss_curve.label_strain}"],
        f"nominal {ss_curve.label_stress}": nominal_df[f"nominal_{ss_curve.label_stress}"],
        f"true {ss_curve.label_strain}": true_df[f"true_{ss_curve.label_strain}"],
        f"true {ss_curve.label_stress}": true_df[f"true_{ss_curve.label_stress}"],
    })
    st.dataframe(combined_df)


def plot_plastic_curve(ss_curve: StressStrainCurve):
    """塑性ひずみ-真応力曲線のグラフを表示"""
    # データ取得
    plastic_df = ss_curve.get_plastic_data()

    # グラフ設定
    fig, ax = plt.subplots(figsize=(10, 6))
    marker_size = 6
    line_width = 1.5
    
    # 塑性ひずみ-真応力曲線
    ax.plot(plastic_df[f"plastic_{ss_curve.label_strain}"], 
            plastic_df[f"true_{ss_curve.label_stress}"], 
            '^-', markersize=marker_size, linewidth=line_width, 
            color='green', label="plastic")

    # 軸とグリッドの設定
    ax.set_xlabel(f"{ss_curve.label_strain}")
    ax.set_ylabel(f"{ss_curve.label_stress}")
    ax.set_xlim(left=0)  # x軸の最小値を0に設定
    ax.set_ylim(bottom=0)  # y軸の最小値を0に設定
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # グラフ表示
    st.pyplot(fig)


def display_plastic_data_table(ss_curve: StressStrainCurve):
    """塑性ひずみ-真応力データをテーブル表示"""
    plastic_df = ss_curve.get_plastic_data()
    
    combined_df = pd.DataFrame({
        f"plastic {ss_curve.label_strain}": plastic_df[f"plastic_{ss_curve.label_strain}"],
        f"plastic {ss_curve.label_stress}": plastic_df[f"true_{ss_curve.label_stress}"],
    })
    st.dataframe(combined_df)
