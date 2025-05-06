from pydantic import BaseModel, ConfigDict
import pandas as pd
import numpy as np
from scipy import optimize

from typing import Tuple, Dict


class SwiftLaw(BaseModel):
    """
    Swift硬化則のデータモデル
    # σ = c * (α + εp)^n
    σ = σ0 * (1 + εp/α)^n
    """
    # c: float
    yield_stress: float
    alpha: float
    n: float
    
    def get_stress(self, strain: float) -> float:
        """指定されたひずみにおける応力を計算"""
        return self.yield_stress * (1 + strain / self.alpha) ** self.n

    def get_strain(self, stress: float) -> float:
        """指定された応力におけるひずみを計算"""
        return self.alpha * ((stress / self.yield_stress) ** (1 / self.n) - 1)

    @staticmethod
    def swift_law_function(x, alpha, n, yield_stress):
        """カーブフィッティング用の関数"""
        return yield_stress * (1 + x / alpha) ** n
    
    def fit_to_data(self, strain_data, stress_data, initial_guess=(0.01, 0.3), max_iterations=1000) -> None:
        """データからパラメータをフィッティング"""       
        params, covariance = optimize.curve_fit(
            lambda x, alpha, n: self.swift_law_function(x, alpha, n, self.yield_stress),
            strain_data,
            stress_data,
            p0=initial_guess,
            maxfev=max_iterations
        )
        # パラメータをモデルに設定
        self.alpha = float(params[0])
        self.n = float(params[1])

    # def get_stress(self, strain: float) -> float:
    #     """指定されたひずみにおける応力を計算"""
    #     return self.c * (self.alpha  + strain) ** self.n
    
    # def get_strain(self, stress: float) -> float:
    #     """指定された応力におけるひずみを計算"""
    #     return (stress / self.c) ** (1 / self.n) - self.alpha
    
    # @staticmethod
    # def swift_law_function(x, c, alpha, n):
    #     """カーブフィッティング用の関数"""
    #     return c * (alpha + x) ** n
                    
    # def fit_to_data(self, strain_data, stress_data, initial_guess=(1.0, 0.01, 0.3), max_iterations=1000) -> None:
    #     """データからパラメータをフィッティング"""
    #     # c, alpha, nに対する下限と上限を設定
    #     # alphaは0以上の制約を設定
    #     bounds = ([0, 0, 0], [np.inf, np.inf, np.inf])
        
    #     params, covariance = optimize.curve_fit(
    #         lambda x, c, alpha, n: self.swift_law_function(x, c, alpha, n),
    #         strain_data,
    #         stress_data,
    #         p0=initial_guess,
    #         bounds=bounds,
    #         maxfev=max_iterations
    #     )
    #     # パラメータをモデルに設定
    #     self.c = float(params[0])
    #     self.alpha = float(params[1])
    #     self.n = float(params[2])
                    
    def calculate_r_squared(self, x, y):
        """決定係数R²を計算"""
        y_pred = self.swift_law_function(x, self.alpha, self.n, self.yield_stress)
        # y_pred = self.swift_law_function(x, self.c, self.alpha, self.n)
        residuals = y - y_pred
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        return 1 - (ss_res / ss_tot)

    def get_plot_data(
            self,
            strain_range: Tuple[float, float],
            num_points: int = 100,
            detail_range: Tuple[float, float] = (0.0, 0.05),
            detail_points: int = 50
    ) -> pd.DataFrame:
        """
        プロット用のデータを取得
        ・strain_range で全体範囲を指定
        ・detail_range で詳細範囲を指定
        ・detail_points で詳細範囲のポイント数を指定
        """
        # 全体範囲のデータを生成（詳細範囲を除く）
        strain_before = np.linspace(strain_range[0], detail_range[0], 
                                   int(num_points * (detail_range[0] - strain_range[0]) / 
                                      (strain_range[1] - strain_range[0])))
        
        # 詳細範囲のデータを生成
        strain_detail = np.linspace(detail_range[0], detail_range[1], detail_points)
        
        # 詳細範囲の後のデータを生成
        strain_after = np.linspace(detail_range[1], strain_range[1], 
                                  int(num_points * (strain_range[1] - detail_range[1]) / 
                                     (strain_range[1] - strain_range[0])))
        
        # 3つの配列を結合
        strain = np.concatenate([strain_before, strain_detail, strain_after])
        
        # 重複した境界値を削除（オプション）
        strain = np.unique(strain)
        
        # 応力を計算
        stress = self.get_stress(strain)
        return pd.DataFrame({"strain": strain, "stress": stress})
    
    model_config = ConfigDict(arbitrary_types_allowed=True)