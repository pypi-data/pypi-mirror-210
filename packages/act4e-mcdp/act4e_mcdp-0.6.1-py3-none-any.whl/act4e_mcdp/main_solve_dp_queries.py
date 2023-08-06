import argparse
import glob
import os
import sys
from importlib import import_module

import yaml

from . import logger
from .loading import load_repr1, parse_yaml_value
from .primitivedps import PrimitiveDP
from .solution_interface import DPSolverInterface, Interval, LowerSet, UpperSet


def import_from_string(dot_path: str) -> object:
    module_path, _, name = dot_path.rpartition(".")
    module = import_module(module_path)
    return getattr(module, name)


__all__ = ["solve_dp_queries_main"]


def solve_dp_queries_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--queries-dir", help="Where the queries are", required=True)
    parser.add_argument("-o", "--output", help="Output summary", default="output_summary.yaml")
    parser.add_argument("--solver", help="Model source (file or URL)", required=True)

    args = parser.parse_args()

    try:
        solver0 = import_from_string(args.solver)
    except Exception as e:
        logger.error("Could not import solver %r", args.solver, exc_info=e)
        sys.exit(1)

    solver: DPSolverInterface

    if isinstance(solver0, DPSolverInterface):
        solver = solver0
    else:
        # noinspection PyCallingNonCallable
        solver = solver0()  # type: ignore
    if not isinstance(solver, DPSolverInterface):
        msg = f"Expected a DPSolverInterface, got {solver!r}"
        raise ValueError(msg)

    queries_dir = args.queries_dir
    all_output = {}

    summary = {
        "failed": [],
        "succeeded": [],
        "comparison_not_implemented": [],
    }

    for fn in glob.glob(queries_dir + "/**/*.dp-queries.*.mcdpr1.yaml", recursive=True):
        data = yaml.load(open(fn).read(), Loader=yaml.SafeLoader)
        filename_rel = data["dp"]
        filename = os.path.join(os.path.dirname(fn), filename_rel)
        if not os.path.exists(filename):
            logger.error("File %r does not exist", filename)
            sys.exit(1)
        data_dp = yaml.load(open(filename).read(), Loader=yaml.SafeLoader)
        model = load_repr1(data_dp, PrimitiveDP)

        logger.info(f"query: {fn} {data} {model}")
        query = data["query"]
        approximated = data["approximated"]

        info_struct = {}
        if query == "FixFunMinRes":
            data_parsed = parse_yaml_value(model.F, data["value"])
            result: Interval[UpperSet] = load_repr1(data["result"], Interval)
            result.pessimistic.minimals = [parse_yaml_value(model.R, x) for x in result.pessimistic.minimals]
            result.optimistic.minimals = [parse_yaml_value(model.R, x) for x in result.optimistic.minimals]

            solution = solver.solve_dp_FixFunMinRes(model, data_parsed)
            if approximated:
                status = "comparison_not_implemented"
            else:
                ok = solution == result
                if ok:
                    status = "succeeded"
                else:
                    status = "failed"

            info_struct = {
                "testcase": fn,
                "query": repr(query),
                "value": repr(data_parsed),
                "result_expected": repr(result),
                "result_obtained": repr(solution),
                "status": status,
            }
            summary[status].append(fn)

        elif query == "FixResMaxFun":
            data_parsed = parse_yaml_value(model.R, data["value"])

            result: Interval[LowerSet] = load_repr1(data["result"], Interval)

            result.pessimistic.maximals = [parse_yaml_value(model.F, x) for x in result.pessimistic.maximals]
            result.optimistic.maximals = [parse_yaml_value(model.F, x) for x in result.optimistic.maximals]

            solution = solver.solve_dp_FixResMaxFun(model, data_parsed)
            if approximated:
                status = "comparison_not_implemented"
            else:
                ok = solution == result
                if ok:
                    status = "succeeded"
                else:
                    status = "failed"

            info_struct = {
                "testcase": fn,
                "query": repr(query),
                "value": repr(data_parsed),
                "result_expected": repr(result),
                "result_obtained": repr(solution),
                "status": status,
            }

            summary[status].append(fn)

        else:
            logger.error("Unknown query %r", query)
            sys.exit(1)

        all_output[fn] = info_struct

        # logger.info(yaml.dump(info_struct))

    fn_out = args.output
    dn = os.path.dirname(fn_out)
    if dn:
        os.makedirs(dn, exist_ok=True)
    with open(fn_out, "w") as f:
        f.write(yaml.dump(all_output, allow_unicode=True, default_flow_style=False))

    logger.info("Summary:\n" + yaml.dump(summary, allow_unicode=True, default_flow_style=False))

    logger.info("Find the summary at %r", fn_out)
