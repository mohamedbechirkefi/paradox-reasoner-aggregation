# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Versioned JSON schemas for configs and results. Results are validated at
export (before writing) and at import (before any report is built); invalid
documents raise ``SchemaError`` (fail closed)."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import jsonschema

__all__ = [
    "RESULT_SCHEMA_VERSION",
    "CONFIG_SCHEMA",
    "RESULT_SCHEMA",
    "SchemaError",
    "validate_config",
    "validate_result",
    "canonical_json",
    "sha256_json",
    "load_result",
]

RESULT_SCHEMA_VERSION = "1.0.0"


class SchemaError(ValueError):
    pass


_prob = {"type": "number", "minimum": 0, "maximum": 1}
_seeds = {"type": "array", "items": {"type": "integer", "minimum": 0}, "minItems": 1, "uniqueItems": True}
_scenario = {
    "type": "object",
    "required": ["id", "p_easy", "h", "p_hard"],
    "additionalProperties": False,
    "properties": {"id": {"type": "string", "minLength": 1}, "p_easy": _prob, "h": _prob, "p_hard": {"oneOf": [_prob, {"type": "null"}]}},
}

_common_cfg = {
    "schema_version": {"const": RESULT_SCHEMA_VERSION},
    "experiment_id": {"type": "string", "pattern": "^(EXP-[0-9]{3}|SMOKE|PROBE-[A-Z0-9-]+)$"},
    "label": {"enum": ["exploratory", "confirmatory"]},
    "kind": {"enum": ["aggregation", "validation", "dependence"]},
    "description": {"type": "string"},
    "seed_entropy": {"type": "integer", "minimum": 0},
    "n_seeds": {"type": "integer", "minimum": 1, "maximum": 100},
    "seeds": _seeds,
}

CONFIG_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "PARADOX experiment config",
    "type": "object",
    "required": ["schema_version", "experiment_id", "label", "kind", "seed_entropy", "n_seeds"],
    "allOf": [
        {
            "if": {"properties": {"kind": {"const": "aggregation"}}},
            "then": {
                "required": ["scenarios", "lambdas", "budgets", "delib_budgets", "rules", "n_items", "w", "delta", "tau"],
                "properties": {
                    "scenarios": {"type": "array", "items": _scenario, "minItems": 1},
                    "lambdas": {"type": "array", "items": _prob, "minItems": 1},
                    "budgets": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 31}, "minItems": 1},
                    "delib_budgets": {"type": "array", "items": {"type": "integer", "minimum": 2, "maximum": 62, "multipleOf": 2}},
                    "rules": {"type": "array", "items": {"enum": ["SINGLE", "MV", "CW", "SEQ", "DELIB"]}, "minItems": 1, "contains": {"const": "SINGLE"}},
                    "n_items": {"type": "integer", "minimum": 1},
                    "w": _prob,
                    "delta": {"type": "number"},
                    "tau": {"type": "number", "minimum": 0},
                },
            },
        },
        {
            "if": {"properties": {"kind": {"const": "validation"}}},
            "then": {
                "required": ["ns", "items_per_seed", "tolerance_se", "common_shock", "mixture", "bahadur"],
                "properties": {
                    "ns": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 31}, "minItems": 1},
                    "items_per_seed": {"type": "integer", "minimum": 1},
                    "tolerance_se": {"type": "number", "exclusiveMinimum": 0},
                    "common_shock": {"type": "object", "required": ["ps", "lambdas"]},
                    "mixture": {"type": "object", "required": ["scenarios", "lambdas"]},
                    "bahadur": {"type": "object", "required": ["ps", "cs"]},
                },
            },
        },
        {
            "if": {"properties": {"kind": {"const": "dependence"}}},
            "then": {
                "required": ["ps", "rs", "ns", "items_per_seed", "models"],
                "properties": {
                    "ps": {"type": "array", "items": _prob, "minItems": 1},
                    "rs": {"type": "array", "items": _prob, "minItems": 1},
                    "ns": {"type": "array", "items": {"type": "integer", "minimum": 1}, "minItems": 1},
                    "items_per_seed": {"type": "integer", "minimum": 1},
                    "models": {"type": "array", "items": {"enum": ["common_shock", "bahadur", "mixture", "beta"]}, "minItems": 1},
                },
            },
        },
    ],
    "properties": _common_cfg,
}

_record = {
    "type": "object",
    "required": ["record_id"],
    "properties": {"record_id": {"type": "string", "pattern": "^(RUN|CELL)-[0-9]{4,}(-[A-Za-z0-9]+)*$"}},
}

_agg_record = {
    "type": "object",
    "required": ["record_id", "scenario", "lambda", "seed", "n_items", "runtime_s", "invariants", "excluded", "exclusion_reason", "metrics"],
    "properties": {
        "invariants": {"type": "object", "additionalProperties": {"type": "boolean"}},
        "excluded": {"type": "boolean"},
        "metrics": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": [
                    "rule", "budget", "n_reasoners", "calls_per_item", "messages_per_item", "accuracy", "brier", "ece",
                    "disagreement_share", "pairwise_disagreement", "accuracy_per_call", "tie_share", "delta_vs_single",
                ],
                "properties": {
                    "rule": {"enum": ["SINGLE", "MV", "CW", "SEQ", "DELIB"]},
                    "accuracy": _prob, "brier": _prob, "ece": _prob, "disagreement_share": _prob,
                    "pairwise_disagreement": _prob, "tie_share": _prob,
                    "delta_vs_single": {"type": "number", "minimum": -1, "maximum": 1},
                },
            },
        },
    },
}

RESULT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "PARADOX result document",
    "type": "object",
    "required": [
        "schema_version", "experiment_id", "label", "kind", "created_utc", "config", "config_sha256",
        "code_revision", "seeds", "records", "summary", "claims_boundary",
    ],
    "properties": {
        "schema_version": {"const": RESULT_SCHEMA_VERSION},
        "experiment_id": _common_cfg["experiment_id"],
        "label": _common_cfg["label"],
        "kind": _common_cfg["kind"],
        "created_utc": {"type": "string"},
        "config": {"type": "object"},
        "config_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "code_revision": {"type": "string", "minLength": 1},
        "seeds": _seeds,
        "records": {"type": "array", "items": _record},
        "summary": {"type": "array", "items": {"type": "object"}},
        "claims_boundary": {"type": "string", "minLength": 1},
    },
    "allOf": [
        {"if": {"properties": {"kind": {"const": "aggregation"}}}, "then": {"properties": {"records": {"items": _agg_record}}}},
    ],
}


def validate_config(cfg: dict) -> dict:
    try:
        jsonschema.validate(cfg, CONFIG_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise SchemaError(f"invalid config: {exc.message} at {list(exc.absolute_path)}") from exc
    return cfg


def validate_result(doc: dict) -> dict:
    try:
        jsonschema.validate(doc, RESULT_SCHEMA)
        validate_config(doc["config"])
    except jsonschema.ValidationError as exc:
        raise SchemaError(f"invalid result document: {exc.message} at {list(exc.absolute_path)}") from exc
    if sha256_json(doc["config"]) != doc["config_sha256"]:
        raise SchemaError("config_sha256 does not match the embedded config")
    return doc


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def sha256_json(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode("ascii")).hexdigest()


def load_result(path: str | Path) -> dict:
    """Load and validate a result document; raises ``SchemaError`` on any defect."""
    p = Path(path)
    if not p.is_file():
        raise SchemaError(f"result file not found: {p}")
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SchemaError(f"malformed JSON in {p}: {exc}") from exc
    if not isinstance(doc, dict):
        raise SchemaError("result document must be a JSON object")
    return validate_result(copy.deepcopy(doc))
