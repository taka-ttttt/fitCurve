from pydantic import BaseModel, ConfigDict
import pandas as pd
import numpy as np

class StressStrainCurve(BaseModel):
    """応力ひずみ曲線のデータモデル"""
    nominal_strain: np.ndarray
    nominal_stress: np.ndarray
    young_modulus: float = 200000
    yield_stress: float = 300
    label_strain: str = "strain[-]"
    label_stress: str = "stress[MPa]"
    
    @property
    def true_strain(self) -> np.ndarray:
        """真ひずみを計算"""
        return np.log(1 + self.nominal_strain)
    
    @property
    def true_stress(self) -> np.ndarray:
        """真応力を計算"""
        return self.nominal_stress * (1 + self.nominal_strain)
    
    @property
    def elastic_strain(self) -> np.ndarray:
        """弾性ひずみを計算"""
        return self.true_stress / self.young_modulus

    @property
    def plastic_strain(self) -> np.ndarray:
        """
        塑性ひずみを計算
        降伏応力未満は0、降伏応力以上は真ひずみから弾性ひずみを引いた値を返す
        """
        result = np.zeros_like(self.true_strain)
        yield_indices = np.where(self.true_stress >= self.yield_stress)[0]
        
        if len(yield_indices) > 0:
            result[yield_indices] = self.true_strain[yield_indices] - self.elastic_strain[yield_indices]
        return result
    
    def get_nominal_data(self) -> pd.DataFrame:
        """公称ひずみ・公称応力データをデータフレームで取得"""
        return pd.DataFrame({
            f"nominal_{self.label_strain}": self.nominal_strain,
            f"nominal_{self.label_stress}": self.nominal_stress
        })
    
    def get_true_data(self) -> pd.DataFrame:
        """真ひずみ・真応力データをデータフレームで取得"""
        return pd.DataFrame({
            f"true_{self.label_strain}": self.true_strain,
            f"true_{self.label_stress}": self.true_stress
        })
    
    def get_plastic_data(self) -> pd.DataFrame:
        """
        塑性ひずみ・真応力データをデータフレームで取得
        - 塑性ひずみが0の要素は除外
        - 先頭行には塑性ひずみ0、真応力=降伏応力を設定
        """
        col_strain = f"plastic_{self.label_strain}"
        col_stress = f"true_{self.label_stress}"
        
        # 全データと非ゼロデータを取得
        all_data_df = pd.DataFrame({col_strain: self.plastic_strain, col_stress: self.true_stress})
        nonzero_plastic_df = all_data_df[all_data_df[col_strain] > 0]
        
        # 初期点を追加して返却
        initial_point_df = pd.DataFrame({col_strain: [0], col_stress: [self.yield_stress]})
        return pd.concat([initial_point_df, nonzero_plastic_df], ignore_index=True)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)