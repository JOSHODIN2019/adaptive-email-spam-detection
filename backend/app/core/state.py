from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.ml.adaptive_model import AdaptiveModelService
from app.ml.drift_monitor import DriftMonitor
from app.ml.static_inference import StaticSVMService
from app.storage.prediction_store import PredictionStore


@dataclass
class AppState:
    settings: Settings
    static_service: StaticSVMService
    adaptive_service: AdaptiveModelService
    drift_monitor: DriftMonitor
    prediction_store: PredictionStore


def build_app_state() -> AppState:
    settings = get_settings()
    static_service = StaticSVMService(settings)
    adaptive_service = AdaptiveModelService(settings)
    drift_monitor = DriftMonitor(settings)

    static_service.load()
    adaptive_service.load()
    drift_monitor.load()

    return AppState(
        settings=settings,
        static_service=static_service,
        adaptive_service=adaptive_service,
        drift_monitor=drift_monitor,
        prediction_store=PredictionStore(),
    )
