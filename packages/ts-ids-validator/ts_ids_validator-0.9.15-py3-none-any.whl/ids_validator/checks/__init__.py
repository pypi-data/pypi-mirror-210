from ids_validator.checks.abstract_checker import AbstractChecker
from ids_validator.checks.generic import (
    AdditionalPropertyChecker,
    AthenaChecker,
    DatacubesChecker,
    ElasticsearchChecker,
    RequiredPropertiesChecker,
    RootNodeChecker,
    TypeChecker,
)
from ids_validator.checks.v1 import (
    V1ChildNameChecker,
    V1ConventionVersionChecker,
    V1RelatedFilesChecker,
    V1RootNodeChecker,
    V1SampleNodeChecker,
    V1SnakeCaseChecker,
    V1SystemNodeChecker,
    V1UserNodeChecker,
)
from ids_validator.convention_versions import Conventions

generic_checks = [
    AdditionalPropertyChecker(),
    DatacubesChecker(),
    RequiredPropertiesChecker(),
    RootNodeChecker(),
    TypeChecker(),
    ElasticsearchChecker(),
    AthenaChecker(),
]

v1_checks = generic_checks + [
    V1ChildNameChecker(),
    V1ConventionVersionChecker(),
    V1RootNodeChecker(),
    V1SnakeCaseChecker(),
    V1SampleNodeChecker(),
    V1SystemNodeChecker(),
    V1UserNodeChecker(),
    V1RelatedFilesChecker(),
]


checks_dict = {
    Conventions.GENERIC: generic_checks,
    Conventions.V1_0_0: v1_checks,
}
