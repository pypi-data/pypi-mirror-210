from dependency_injector import containers, providers

from feature_forge.domain.dag_builder import DAGBuilder
from feature_forge.domain.dataset_model_builder import DatasetModelBuilder
from feature_forge.domain.feature_validator import FeatureValidator
from feature_forge.domain.pipeline_builder import PipelineBuilder
from feature_forge.domain.pipeline_runner import PipelineRunner


class DomainContainer(containers.DeclarativeContainer):

    pipeline_builder = providers.Factory(
        PipelineBuilder,
        providers.Factory(DatasetModelBuilder),
        providers.Factory(DAGBuilder),
        providers.Factory(FeatureValidator)
    )

    pipeline_runner = providers.Factory(
        PipelineRunner
    )