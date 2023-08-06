from dataclasses import dataclass
from typing import Type, List, Callable

import pandas as pd
from pydot import Dot

from feature_forge.domain.entities.dataset import Dataset
from feature_forge.domain.entities.entity_model import EntityModel


@dataclass
class Pipeline:
    dataset: Dataset
    entity: Type[EntityModel]
    flow: Callable[[pd.DataFrame], pd.DataFrame]
    graph: Dot
    requested_features: List[str]
    all_features: List[str]