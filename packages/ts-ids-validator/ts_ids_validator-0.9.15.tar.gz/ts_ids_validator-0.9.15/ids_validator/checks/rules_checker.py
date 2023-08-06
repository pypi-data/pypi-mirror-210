from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

from pydash import get

from ids_validator.checks.abstract_checker import AbstractChecker, CheckResults
from ids_validator.ids_node import Node
from ids_validator.utils import Log


@dataclass
class BackwardCompatibleType:
    """Represents a type with one or more backward-compatible deprecated types.

    If a node's type matches the preferred type, no warnings or errors will be logged.
    If a node's type matches a deprecated type, a warning will be logged. This means
    validation will not fail for these types, but the user will be told that the type
    being used is deprecated.
    """

    preferred: Union[list, str]
    deprecated: Sequence[Union[list, str]]


@dataclass
class PropertyConstraints:
    """Represents the minimum properties which must be present in an object, plus
    extra properties which may or may not be present
    """

    minimum: Set[str]
    allowed_extra: Optional[Set[str]]


def types_match(
    node_type: Union[str, List[str]], expected_type: Union[str, List[str]]
) -> bool:
    """Determine whether two jsonschema types match, accounting for types which are a
    list of types, or a single type
    """
    if type(node_type) != type(expected_type):
        return False

    if isinstance(expected_type, list):
        node_type = sorted(node_type)
        expected_type = sorted(expected_type)

    return node_type == expected_type


def evaluate_property_constraints(
    properties: Set[str], minimum: Set[str], allowed_extra: Optional[Set[str]] = None
) -> Tuple[Set[str], Set[str]]:
    """
    Compare a set of properties against a minimum and maximum constraint, returning any
    missing properties or extra properties outside of these constraints.
    The maximum constraint is the union of `minimum` and `allowed_extra`.
    When `allowed_extra` is `None`, no upper bound is checked and the returned
    `extra_properties` will be an empty set.

    Returns (missing_properties, extra_properties).
    """
    extra_properties = set()
    # Check the upper bound of the allowed properties, if specified
    if allowed_extra is not None:
        max_allowed = minimum.union(allowed_extra)
        extra_properties = properties - max_allowed

    # Check the lower bound of the allowed properties
    missing_properties = minimum - properties

    return missing_properties, extra_properties


class RuleBasedChecker(AbstractChecker):
    rules: Dict[str, Any]

    def run(self, node: Node, context: dict = None) -> CheckResults:
        logs = []
        paths = list(self.rules.keys())
        if node.path in paths:
            checks = self.rules[node.path]
            if checks:
                logs += self.enforce_checks(node, checks)

        return logs

    @classmethod
    def enforce_checks(cls, node: Node, checks: dict) -> CheckResults:
        logs = []
        if "type" in checks:
            logs += cls.enforce_type(node, checks.get("type"))
        if "compatible_type" in checks:
            logs += cls.enforce_compatible_type(node, checks.get("compatible_type"))
        if "required" in checks:
            logs += cls.enforce_required(node, checks.get("required"))
        if "min_required" in checks:
            logs += cls.enforce_min_required(node, checks.get("min_required"))
        if "min_properties" in checks:
            minimum = set(checks["min_properties"])
            logs += cls.enforce_constrained_properties(node, minimum)
        if "constrained_properties" in checks:
            constraints: PropertyConstraints = checks["constrained_properties"]
            logs += cls.enforce_constrained_properties(
                node=node,
                minimum=constraints.minimum,
                allowed_extra=constraints.allowed_extra,
            )
        return logs

    @classmethod
    def enforce_type(cls, node: Node, type_: Union[List[str], str]) -> CheckResults:
        """Enforce that a node has a specific type"""
        logs = []

        # don't allow "null" if "const" is defined
        # schema will be enforced only when const is not
        # defined
        if "const" in node.data:
            is_valid, msg = node._check_const_type()
            if not is_valid:
                logs += [(msg, Log.CRITICAL.value)]
                return logs
            return logs

        if not types_match(node.type_, type_):
            logs += [(f"'type' must be {type_}", Log.CRITICAL)]

        return logs

    @classmethod
    def enforce_compatible_type(
        cls, node: Node, compatible_type: BackwardCompatibleType
    ) -> CheckResults:
        """Enforces that the node type matches a preferred or deprecated type.

        If the type matches the preferred type: no warnings or errors
        If the type matches a deprecated type: log a warning
        Otherwise the type isn't allowed: log a critical error
        """
        logs = []
        preferred_type = compatible_type.preferred
        deprecated_types = compatible_type.deprecated

        if "const" in node.data:
            is_valid, msg = node._check_const_type()
            if not is_valid:
                logs += [(msg, Log.CRITICAL.value)]
                return logs
            return logs

        if types_match(node.type_, preferred_type):
            return logs

        for deprecated_type in deprecated_types:
            if types_match(node.type_, deprecated_type):
                logs += [
                    (
                        f"'type' '{node.type_}' is deprecated but allowed for backward "
                        f"compatibility, please use `{preferred_type}` instead.",
                        Log.WARNING,
                    )
                ]
                return logs

        logs += [
            (
                f"'type' must be {preferred_type}, "
                f"or one of these deprecated types: {deprecated_types}",
                Log.CRITICAL,
            )
        ]

        return logs

    @classmethod
    def enforce_required(cls, node: Node, required: list) -> CheckResults:
        """Enforce that a node has specific required properties"""
        logs = []
        node_required = node.get("required")

        if set(node_required) != set(required):
            logs += [(f"'required' must be {required}", Log.CRITICAL.value)]

        return logs

    @classmethod
    def enforce_min_required(cls, node: Node, required: list) -> CheckResults:
        logs = []
        min_required = set(required)
        node_required = node.get("required", [])
        if not isinstance(node_required, list):
            logs += [(f"'required' must contain {min_required}", Log.CRITICAL.value)]
            return logs

        node_required = set(node_required)
        missing = min_required - node_required
        if missing:
            logs += [(f"'required' must contain {missing}", Log.CRITICAL.value)]

        return logs

    @classmethod
    def enforce_constrained_properties(
        cls, node: Node, minimum: Set[str], allowed_extra: Optional[Set[str]] = None
    ) -> CheckResults:
        """
        Enforce that at least a minimum set of properties are present.
        Optionally, if `allowed_extra` is not `None`, enforce that the properties don't
        exceed a maximum set of allowed properties (union of minimum and allowed_extra)
        """
        node_properties = get(node, "properties") or get(node, "items.properties") or {}
        node_properties = set(node_properties.keys())
        logs: CheckResults = []

        missing_properties, extra_properties = evaluate_property_constraints(
            node_properties,
            minimum,
            # Any node may contain "@link"
            allowed_extra.union({"@link"}) if allowed_extra is not None else None,
        )

        if extra_properties:
            message = (
                f"'properties' must contain {sorted(minimum)}, "
                f"and can optionally contain {sorted(allowed_extra)}. "
                f"Extra properties found: {sorted(extra_properties)}"
            )
            logs.append((message, Log.CRITICAL))

        if missing_properties:
            logs.append(
                (
                    f"'properties' must contain {sorted(missing_properties)}",
                    Log.CRITICAL,
                )
            )

        return logs
