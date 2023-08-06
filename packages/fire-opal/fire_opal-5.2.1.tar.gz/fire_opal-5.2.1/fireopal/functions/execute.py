# Copyright 2023 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from typing import (
    Any,
    Dict,
    List,
)

from qctrlclient.core import print_warnings

from .base import fire_opal_workflow


@fire_opal_workflow("compile_and_run_workflow", formatter=print_warnings)
def execute(
    circuits: List[str],
    shot_count: int,
    credentials: Dict[str, Any],
    backend_name: str,
) -> Dict:
    """
    Execute a batch of `circuits` where `shot_count` measurements are taken per circuit.

    Parameters
    ----------
    circuits : List[str]
        A list of quantum circuits in the form of a QASM strings. You may use Qiskit to
        generate these strings.
    shot_count : int
        Number of bitstrings that are sampled from the final quantum state.
    credentials : Dict[str, Any]
        The credentials for running circuits on an IBM backend. This dictionary should
        contain key-value entries with keys `token`, `project`, `hub`, and `group`.
    backend_name : str
        The backend device name that should be used to run circuits.

    Returns
    -------
    Dict
        A dictionary containing probability mass functions and warnings.
    """
    return {
        "circuits": circuits,
        "shot_count": shot_count,
        "credentials": credentials,
        "backend_name": backend_name,
    }
