import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.optimize import curve_fit
import io

def power_law(x, K, n):
    """n乗硬化則の関数"""
    return K * (x ** n)

def main():
    st.title("材料引張試験データ n乗硬化則近似アプリ")
    
    # ファイルアップロード
    uploaded_file = st.file_uploader("CSVファイルをアップロード", type=['csv'])
    
    if uploaded_file is not None:
        # データ読み込み
        df = pd.read_csv(uploaded_file)
        
        # データ設定
        st.subheader("データ設定")
        col1, col2 = st.columns(2)
        
        with col1:
            # カラム選択
            strain_col = st.selectbox("ひずみの列を選択", df.columns)
            stress_col = st.selectbox("応力の列を選択", df.columns)
        
        with col2:
            # ひずみの単位選択
            strain_unit = st.radio(
                "ひずみデータの単位を選択してください",
                ["無次元 (0.01 = 1%)", "パーセント (1 = 1%)"],
                help="ひずみが百分率（%）で表されている場合は「パーセント」を選択してください"
            )
            
            # 真ひずみ・真応力への変換オプション
            convert_to_true = st.checkbox("公称ひずみ・応力を真ひずみ・真応力に変換する")

        # データの前処理
        working_df = df.copy()
        if strain_unit == "パーセント (1 = 1%)":
            working_df[strain_col] = df[strain_col] * 0.01
            st.info("ひずみデータを無次元化しました")
        
        if convert_to_true:
            working_df[strain_col] = np.log(1 + working_df[strain_col])
            working_df[stress_col] = df[stress_col] * (1 + working_df[strain_col])
            st.info("データを真ひずみ・真応力に変換しました")
        
        # グラフの作成
        if 'fig' not in st.session_state:
            st.session_state.fig = go.Figure()
        
        # グラフをクリア
        st.session_state.fig.data = []
        
        # 元データのプロット
        strain_display_factor = 100 if strain_unit == "パーセント (1 = 1%)" else 1
        plot_strain = working_df[strain_col] * strain_display_factor
        
        st.session_state.fig.add_trace(go.Scatter(
            x=plot_strain,
            y=working_df[stress_col],
            mode='markers',
            name='実験データ'
        ))
        
        # グラフの基本設定
        strain_type = "真ひずみ" if convert_to_true else "公称ひずみ"
        stress_type = "真応力" if convert_to_true else "公称応力"
        strain_unit_label = "%" if strain_unit == "パーセント (1 = 1%)" else ""
        
        st.session_state.fig.update_layout(
            xaxis_title=f"ひずみ ε ({strain_type}) {strain_unit_label}",
            yaxis_title=f"応力 σ ({stress_type}) (MPa)",
            title="応力-ひずみ曲線"
        )
        
        # グラフの表示
        st.plotly_chart(st.session_state.fig, use_container_width=True)

        # フィッティング範囲の設定
        st.subheader("フィッティング範囲の設定")
        strain_min, strain_max = st.slider(
            "ひずみの範囲を選択",
            float(working_df[strain_col].min() * strain_display_factor),
            float(working_df[strain_col].max() * strain_display_factor),
            (float(working_df[strain_col].min() * strain_display_factor), 
             float(working_df[strain_col].max() * strain_display_factor))
        )
        
        # 降伏応力の入力
        yield_stress = st.number_input(
            "降伏応力 (MPa)",
            min_value=0.0,
            value=0.0,
            help="データを弾性域と塑性域に分割するための降伏応力を入力してください"
        )
        
        # スライダーの値を実際のひずみ値に変換
        strain_min = strain_min / strain_display_factor
        strain_max = strain_max / strain_display_factor
        
        # フィッティングボタン
        if st.button("カーブフィッティング実行"):
            # フィッティング範囲のデータ抽出
            mask = (working_df[strain_col] >= strain_min) & (working_df[strain_col] <= strain_max)
            fit_data = working_df[mask]
            
            try:
                # カーブフィッティング
                popt, _ = curve_fit(
                    power_law,
                    fit_data[strain_col],
                    fit_data[stress_col],
                    p0=[100, 0.2]  # 初期値
                )
                K, n = popt
                
                # 結果をセッションステートに保存
                st.session_state.fitting_results = {
                    'K': K,
                    'n': n,
                    'strain_type': strain_type,
                    'stress_type': stress_type,
                    'yield_stress': yield_stress
                }
                
                # フィッティング曲線のプロット
                plot_strain_fit = np.linspace(strain_min, strain_max, 100) * strain_display_factor
                stress_fit = power_law(plot_strain_fit/strain_display_factor, K, n)
                
                st.session_state.fig.add_trace(go.Scatter(
                    x=plot_strain_fit,
                    y=stress_fit,
                    mode='lines',
                    name='近似曲線'
                ))
                
                # 降伏応力が指定されている場合は弾性域と塑性域を可視化
                if yield_stress > 0:
                    # 降伏応力に対応するひずみを近似的に求める（二分法など）
                    def find_yield_strain(stress_val, K, n, tol=1e-6):
                        # 二分法でひずみを求める
                        strain_low, strain_high = 0, 1.0
                        while strain_high - strain_low > tol:
                            strain_mid = (strain_low + strain_high) / 2
                            stress_mid = power_law(strain_mid, K, n)
                            if stress_mid < stress_val:
                                strain_low = strain_mid
                            else:
                                strain_high = strain_mid
                        return (strain_low + strain_high) / 2
                    
                    yield_strain = find_yield_strain(yield_stress, K, n)
                    
                    # 弾性域の近似線
                    elastic_strain = np.linspace(0, yield_strain, 50) * strain_display_factor
                    elastic_stress = power_law(elastic_strain/strain_display_factor, K, n)
                    
                    # 塑性域の近似線
                    plastic_strain = np.linspace(yield_strain, strain_max, 50) * strain_display_factor
                    plastic_stress = power_law(plastic_strain/strain_display_factor, K, n)
                    
                    st.session_state.fig.add_trace(go.Scatter(
                        x=elastic_strain,
                        y=elastic_stress,
                        mode='lines',
                        name='弾性域',
                        line=dict(color='green', width=3)
                    ))
                    
                    st.session_state.fig.add_trace(go.Scatter(
                        x=plastic_strain,
                        y=plastic_stress,
                        mode='lines',
                        name='塑性域',
                        line=dict(color='red', width=3)
                    ))
                    
                    # 降伏点を示す
                    st.session_state.fig.add_trace(go.Scatter(
                        x=[yield_strain * strain_display_factor],
                        y=[yield_stress],
                        mode='markers',
                        name='降伏点',
                        marker=dict(color='black', size=10)
                    ))
                
                # グラフを再表示
                st.plotly_chart(st.session_state.fig, use_container_width=True)
                
                # 塑性ひずみグラフの作成（降伏応力が設定されている場合のみ）
                if yield_stress > 0:
                    st.subheader("塑性ひずみグラフ")
                    
                    # 塑性ひずみの計算（降伏点より上のデータのみ）
                    # 塑性ひずみ = 全ひずみ - 弾性ひずみ
                    # 弾性ひずみ = 応力/ヤング率 ≈ 応力/（降伏応力/降伏ひずみ）
                    
                    # ヤング率の近似計算
                    young_modulus = yield_stress / yield_strain
                    
                    # 塑性ひずみをもつデータの抽出（応力が降伏応力以上）
                    plastic_data = working_df[working_df[stress_col] >= yield_stress].copy()
                    
                    if not plastic_data.empty:
                        # 塑性ひずみの計算
                        plastic_data['plastic_strain'] = plastic_data[strain_col] - plastic_data[stress_col] / young_modulus
                        
                        # 塑性ひずみグラフ用のfigureを作成
                        plastic_fig = go.Figure()
                        
                        # 実験データの塑性ひずみプロット
                        plastic_fig.add_trace(go.Scatter(
                            x=plastic_data['plastic_strain'] * strain_display_factor,
                            y=plastic_data[stress_col],
                            mode='markers',
                            name='実験データ（塑性ひずみ）'
                        ))
                        
                        # 塑性ひずみグラフの表示範囲設定
                        st.subheader("塑性ひずみグラフの表示範囲設定")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # X軸（塑性ひずみ）の範囲設定
                            plastic_strain_min, plastic_strain_max = st.slider(
                                "塑性ひずみの範囲",
                                0.0,
                                float(plastic_data['plastic_strain'].max() * strain_display_factor * 2),  # 最大値の2倍まで
                                (0.0, float(plastic_data['plastic_strain'].max() * strain_display_factor))
                            )
                            # スライダーの値を実際のひずみ値に変換
                            plastic_strain_min = plastic_strain_min / strain_display_factor
                            plastic_strain_max = plastic_strain_max / strain_display_factor
                        
                        with col2:
                            # Y軸（応力）の範囲設定
                            stress_min, stress_max = st.slider(
                                "応力の範囲",
                                0.0,
                                float(plastic_data[stress_col].max() * 1.2),  # 最大値の1.2倍まで
                                (0.0, float(plastic_data[stress_col].max() * 1.1))  # デフォルトは最大値の1.1倍まで
                            )
                        
                        # 元の近似曲線を降伏ひずみ分オフセット
                        plastic_strain_fit = np.linspace(plastic_strain_min, plastic_strain_max, 100)
                        plastic_stress_fit = power_law(plastic_strain_fit + yield_strain, K, n)
                        
                        # 近似曲線のプロット
                        plastic_fig.add_trace(go.Scatter(
                            x=plastic_strain_fit * strain_display_factor,
                            y=plastic_stress_fit,
                            mode='lines',
                            name='塑性ひずみに対する近似曲線'
                        ))
                        
                        # グラフのレイアウト設定
                        plastic_fig.update_layout(
                            xaxis_title=f"塑性ひずみ εp ({strain_type}) {strain_unit_label}",
                            yaxis_title=f"応力 σ ({stress_type}) (MPa)",
                            title="応力-塑性ひずみ曲線",
                            xaxis=dict(range=[plastic_strain_min * strain_display_factor, plastic_strain_max * strain_display_factor]),
                            yaxis=dict(range=[stress_min, stress_max])
                        )
                        
                        # 塑性ひずみグラフを表示
                        st.plotly_chart(plastic_fig, use_container_width=True)
                        
                        # 塑性ひずみに対する近似式の表示
                        st.write(f"塑性ひずみに対する近似式: σ({st.session_state.fitting_results['stress_type']}) = {K:.2f}・(εp({st.session_state.fitting_results['strain_type']}) + {yield_strain:.4f})^{n:.4f}")
                    else:
                        st.info("降伏応力以上のデータが存在しないため、塑性ひずみグラフを作成できません。")
            except Exception as e:
                st.error(f"フィッティングエラー: {e}")
        
        # フィッティング結果の表示（結果が存在する場合のみ）
        if 'fitting_results' in st.session_state:
            st.subheader("フィッティング結果")
            results = st.session_state.fitting_results
            st.write(f"K = {results['K']:.2f}")
            st.write(f"n = {results['n']:.4f}")
            st.write(f"近似式: σ({results['stress_type']}) = {results['K']:.2f}・ε({results['strain_type']})^{results['n']:.4f}")
            
            if results.get('yield_stress', 0) > 0:
                # 降伏ひずみを計算
                def find_yield_strain(stress_val, K, n, tol=1e-6):
                    strain_low, strain_high = 0, 1.0
                    while strain_high - strain_low > tol:
                        strain_mid = (strain_low + strain_high) / 2
                        stress_mid = power_law(strain_mid, K, n)
                        if stress_mid < stress_val:
                            strain_low = strain_mid
                        else:
                            strain_high = strain_mid
                    return (strain_low + strain_high) / 2
                
                yield_strain = find_yield_strain(results['yield_stress'], results['K'], results['n'])
                st.write(f"降伏応力 = {results['yield_stress']:.2f} MPa")
                st.write(f"降伏ひずみ = {yield_strain * strain_display_factor:.4f}{' %' if strain_unit == 'パーセント (1 = 1%)' else ''}")
            
            # CSVエクスポート設定
            st.subheader("CSVデータ出力設定")
            max_strain_export = st.number_input(
                "出力するひずみの最大値",
                min_value=float(strain_min * strain_display_factor),
                max_value=None,
                value=float(strain_max * strain_display_factor),
                help="近似式を使って計算するひずみの最大値を指定します"
            )
            # 入力値を実際のひずみ値に変換
            max_strain_export = max_strain_export / strain_display_factor
            
            # フィッティングデータのエクスポート用のデータ作成
            plot_strain_fit = np.linspace(strain_min, max_strain_export, 100) * strain_display_factor
            stress_fit = power_law(plot_strain_fit/strain_display_factor, 
                                 results['K'], results['n'])
            
            fit_df = pd.DataFrame({
                f'strain_{results["strain_type"]}': plot_strain_fit,
                f'stress_{results["stress_type"]}': stress_fit
            })
            
            csv = fit_df.to_csv(index=False)
            st.download_button(
                label="近似データをCSVでダウンロード",
                data=csv,
                file_name="fitting_result.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
