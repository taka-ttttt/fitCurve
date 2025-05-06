from pydantic import BaseModel, Field
from typing import Tuple


class FitSettings(BaseModel):
    """フィッティングの設定を管理するモデル"""
    fit_range: Tuple[float, float]
    initial_guess: Tuple[float, float] = Field(default=(1.0, 0.2))
    max_iterations: int = Field(default=1000)
    
    def validate_range(self) -> bool:
        """範囲が有効かどうか検証"""
        start, end = self.fit_range
        return start < end and start >= 0