# This file is currently not used but serves as mock for advanced options.

from dataclasses import field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic.dataclasses import dataclass


class EncoderType(str, Enum):
    NULL = 'null'
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    MULTI_CATEGORICAL = "multi_categorical"


@dataclass
class EncoderConfig:
    type: EncoderType
    params: Dict[str, Any]


@dataclass
class ColumnEncoderConfig:
    table: str
    col: str
    encoder: Union[EncoderConfig, List[EncoderConfig]]


class TrainerMode(str, Enum):
    AUTO_TRAINER = 'AUTO_TRAINER'
    MANUAL_TRAINER = 'MANUAL_TRAINER'


@dataclass
class TrainerConfig:
    channels: int = 128
    num_layers: int = 2
    aggr: List[str] = field(
        default_factory=lambda: ['sum', 'mean', 'min', 'max', 'std'])
    num_pre_mp_layers: int = 2
    num_post_mp_layers: int = 2
    dropout: float = 0.0
    batch_size: int = 512
    lr: float = 0.001
    num_neighbors: List[int] = field(default_factory=lambda: [-1, -1, 20, 10])


@dataclass
class AutoTrainerModelSpace:
    channels: List[int] = field(default_factory=lambda: [64, 128, 256])
    dropout: List[float] = field(default_factory=lambda: [0.0, 0.5])


@dataclass
class AutoTrainerOptimSpace:
    lr: List[float] = field(default_factory=lambda: [0.001, 0.1])
    weight_decay: List[float] = field(default_factory=lambda: [1e-5, 1e-3])


@dataclass
class AutoTrainerOptions:
    metrics: List[str] = field(default_factory=lambda: ['auroc', 'auprc'])
    num_trials: int = 8
    trial_early_stopping: Dict = field(
        default_factory=lambda: {'min_epoch': 3})
    searcher: str = 'bayesian'
    num_ensembles: int = 3

    trainer_cfg: TrainerConfig = TrainerConfig()
    model_space: AutoTrainerModelSpace = AutoTrainerModelSpace()
    optim_space: AutoTrainerOptimSpace = AutoTrainerOptimSpace()


@dataclass
class EncoderOption:
    table: str
    col: str


@dataclass
class AdvancedTrainingOptions:
    custom_encoders: List[ColumnEncoderConfig] = field(default_factory=list)
    trainer_mode: TrainerMode = TrainerMode.AUTO_TRAINER
    manual_trainer_cfg: Optional[TrainerConfig] = None
    auto_trainer_options: AutoTrainerOptions = AutoTrainerOptions()
