from dependency_injector import containers, providers

from feature_forge.domain.container import DomainContainer


class Container(containers.DeclarativeContainer):

    domain = providers.Container(
        DomainContainer
    )
