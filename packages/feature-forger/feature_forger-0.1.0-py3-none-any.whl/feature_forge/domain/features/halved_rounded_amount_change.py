from dataclasses import dataclass
from typing import Type, Tuple

import pandas as pd

from feature_forge.domain.entities.entity_model import EntityModel
from feature_forge.domain.entities.feature import Feature
from feature_forge.domain.entity_models.transaction import Transaction
from feature_forge.domain.features.rounded_amount_change import \
    TransactionRoundedAmountChange


@dataclass(frozen=True)
class TransactionHalfRoundedAmountChange(Feature):
    col_name: str = "transaction_half_rounded_amount_change"
    description: str = "half of the rounded difference between the withdrawal" \
                  " amount and the deposit amount"
    entity_model: Type[EntityModel] = Transaction
    dependencies: Tuple[Feature] = (TransactionRoundedAmountChange(),)

    def row_compute_fn(self, row: pd.Series):
        row[self.col_name] = row[TransactionRoundedAmountChange.col_name] / 2
        return row

    def table_compute_fn(self, data: pd.DataFrame):
        return self.row_compute_fn(data)