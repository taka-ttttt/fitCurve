import numpy as np
from scipy import optimize
from ..models.raw_data import RawData
from ..models.stress_strain_curve import StressStrainCurve
from ..models.fit_settings import FitSettings
from ..models.ludwik_law import LudwikLaw
from ..models.swift_law import SwiftLaw
from ..models.voce_law import VoceLaw


def fit_ludwik_curve(
        base_curve: StressStrainCurve,
        settings: FitSettings,
) -> LudwikLaw:
    """応力ひずみ曲線にLudwik則をフィッティング"""
    # 範囲でデータをフィルタリング
    start, end = settings.fit_range
    mask = (base_curve.true_strain > start) & (base_curve.true_strain <= end)
    
    x_data = base_curve.true_strain[mask]
    y_data = base_curve.true_stress[mask]
    
    # LudwikLawのフィッティングメソッドを使用
    ludwik_law_model = LudwikLaw(yield_stress=base_curve.yield_stress, k=0.0, n=0.0)
    ludwik_law_model.fit_to_data(x_data, y_data, settings.initial_guess, settings.max_iterations)
    
    return ludwik_law_model


def fit_swift_curve(
        base_curve: StressStrainCurve,
        settings: FitSettings,
) -> SwiftLaw:
    """応力ひずみ曲線にSwift則をフィッティング"""
    start, end = settings.fit_range
    mask = (base_curve.true_strain > start) & (base_curve.true_strain <= end)
    
    x_data = base_curve.true_strain[mask]
    y_data = base_curve.true_stress[mask]
    
    # SwiftLawのフィッティングメソッドを使用
    swift_law_model = SwiftLaw(yield_stress=base_curve.yield_stress, alpha=0.0, n=0.0)
    # swift_law_model = SwiftLaw(c=0.0, alpha=0.0, n=0.0)
    swift_law_model.fit_to_data(x_data, y_data)
    
    return swift_law_model


def fit_voce_curve(
        base_curve: StressStrainCurve,
        settings: FitSettings,
) -> VoceLaw:
    """応力ひずみ曲線にVoce則をフィッティング"""
    start, end = settings.fit_range
    mask = (base_curve.true_strain > start) & (base_curve.true_strain <= end)
    
    x_data = base_curve.true_strain[mask]
    y_data = base_curve.true_stress[mask]
    
    # VoceLawのフィッティングメソッドを使用
    voce_law_model = VoceLaw(yield_stress=base_curve.yield_stress, stress_infinite=0.0, h=0.0)
    voce_law_model.fit_to_data(x_data, y_data)
    
    return voce_law_model
