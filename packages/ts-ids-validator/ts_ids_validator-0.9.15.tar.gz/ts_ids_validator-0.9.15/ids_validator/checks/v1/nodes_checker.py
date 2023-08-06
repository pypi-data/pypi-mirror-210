from ids_validator.checks.rules_checker import RuleBasedChecker
from ids_validator.checks.v1.rules.related_files import RULES as RELATED_FILES_RULES
from ids_validator.checks.v1.rules.samples import samples_rules
from ids_validator.checks.v1.rules.systems import systems_rules
from ids_validator.checks.v1.rules.users import users_rules


class V1SystemNodeChecker(RuleBasedChecker):
    rules = systems_rules


class V1SampleNodeChecker(RuleBasedChecker):
    rules = samples_rules


class V1UserNodeChecker(RuleBasedChecker):
    rules = users_rules


class V1RelatedFilesChecker(RuleBasedChecker):
    """
    Check that the related files schema matches the template from the schema conventions
    """

    rules = RELATED_FILES_RULES
