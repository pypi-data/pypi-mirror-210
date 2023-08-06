from typing import Type, Tuple, runtime_checkable, Protocol, Optional, Callable

import pandas as pd
from pydantic.dataclasses import dataclass

from feature_forge.domain.entities.entity_model import EntityModel


class FeatureMeta(type):
    def __repr__(cls):
        return f'{cls.__name__}'


@dataclass(frozen=True)
class Feature:
    __metaclass__ = FeatureMeta
    col_name: str
    description: str
    entity_model: Type[EntityModel]
    dependencies: Tuple["Feature"]

    feature_name: Optional[str] = None
    row_level_function: Optional[Callable[[pd.Series], pd.Series]] = None
    table_level_function: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None

    @property
    def name(self) -> str:
        return self.feature_name if self.feature_name else self.__class__.__name__

    def row_compute_fn(self, row: pd.Series) -> pd.Series:
        if self.row_level_function:
            return self.row_level_function(row)
        raise NotImplementedError()

    def table_compute_fn(self, data: pd.DataFrame) -> pd.DataFrame:
        if self.table_level_function:
            return self.table_level_function(data)
        raise NotImplementedError()
