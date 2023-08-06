import argparse
import os
import sys
from importlib import import_module

import yaml

from . import logger
from .loading import load_repr1, parse_yaml_value
from .solution_interface import SolutionInterface
from .structures import NamedDP


def import_from_string(dot_path: str) -> object:
    module_path, _, name = dot_path.rpartition(".")
    module = import_module(module_path)
    return getattr(module, name)


__all__ = ["solve_main"]


def solve_main() -> None:
    queries = ["FixFunMinRes", "FixResMaxFun"]
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Model source (file or URL)", required=True)
    parser.add_argument("--query", help="query", default="FixFunMinRes", required=False)
    parser.add_argument("--data", help="data (YAML Format)", required=True)
    parser.add_argument("--solver", help="Model source (file or URL)", required=True)

    args = parser.parse_args()

    model_source = args.model
    try:
        solver0 = import_from_string(args.solver)
    except Exception as e:
        logger.error("Could not import solver %r", args.solver, exc_info=e)
        sys.exit(1)

    solver: SolutionInterface

    if isinstance(solver0, SolutionInterface):
        solver = solver0
    else:
        solver = solver0()  # type: ignore

    query = args.query

    if query not in queries:
        logger.error("Unknown query %r. Known: %r", query, queries)
        sys.exit(1)

    query_data = args.data

    if os.path.exists(model_source):
        model_source = open(model_source).read()
        data = yaml.load(model_source, Loader=yaml.SafeLoader)
    else:
        logger.error("URL not implemented yet: %r", model_source)
        sys.exit(1)

    model = load_repr1(data, NamedDP)
    logger.info("model: %s", model)

    yaml_query = yaml.load(query_data, Loader=yaml.SafeLoader)
    if not isinstance(yaml_query, dict):
        raise ValueError(f"Expected dict, got {yaml_query!r}")

    if query == "FixFunMinRes":
        found = set(yaml_query)
        expected = set(model.functionalities)
        if found != expected:
            msg = f"Expected {expected}, got {found}"
            raise ValueError(msg)

        value = {}
        for k, v in model.functionalities.items():
            value[k] = parse_yaml_value(v, yaml_query[k])

        logger.info("query: %s", value)

        solution = solver.solve_FixFunMinRes(model, value)

        logger.info("solution: %s", solution)

    elif query == "FixResMaxFun":
        found = set(yaml_query)
        expected = set(model.resources)
        if found != expected:
            msg = f"Expected {expected}, got {found}"
            raise ValueError(msg)

        value = {}
        for k, v in model.resources.items():
            value[k] = parse_yaml_value(v, yaml_query[k])

        logger.info("query: %s", value)

        solution = solver.solve_FixResMaxFun(model, value)

        logger.info("solution: %s", solution)

    else:
        raise ValueError(f"Unknown query {query}")
