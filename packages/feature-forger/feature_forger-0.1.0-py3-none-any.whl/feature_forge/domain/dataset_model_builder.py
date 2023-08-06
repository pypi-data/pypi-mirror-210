from typing import Type

import pandera

from feature_forge.domain.entities.dataset import Dataset


class DatasetModelBuilder:

    def build(self, dataset: Dataset) -> Type[pandera.DataFrameModel]:

        class DatasetModel(pandera.DataFrameModel):
            class Config:
                dtype = dataset.entity_model
                coerce = True

        return DatasetModel
