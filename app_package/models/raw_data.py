from pydantic import BaseModel, ConfigDict
from typing import Optional
import pandas as pd
import numpy as np


class RawData(BaseModel):
    """CSVから読み込んだ生データとカラム選択情報を保持するクラス"""
    df: pd.DataFrame
    epsilon_column: Optional[str] = None
    sigma_column: Optional[str] = None
    is_strain_percent: bool = False
    young_modulus: float = 200000
    yield_stress: float = 300

    @property
    def strain_col(self) -> np.ndarray:
        """ひずみの配列を取得（パーセント値の場合は変換）"""
        if not self.epsilon_column:
            return np.array([])
            
        if self.is_strain_percent:
            return self.df[self.epsilon_column].to_numpy() * 0.01
        else:
            return self.df[self.epsilon_column].to_numpy()
    
    @property
    def stress_col(self) -> np.ndarray:
        """応力の配列を取得"""
        if not self.sigma_column:
            return np.array([])
        return self.df[self.sigma_column].to_numpy()
    
    def is_ready(self) -> bool:
        """データが解析準備完了かどうか確認"""
        return (self.epsilon_column is not None and 
                self.sigma_column is not None and
                not self.df.empty)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)