#
#  MAKINAROCKS CONFIDENTIAL
#  ________________________
#
#  [2017] - [2023] MakinaRocks Co., Ltd.
#  All Rights Reserved.
#
#  NOTICE:  All information contained herein is, and remains
#  the property of MakinaRocks Co., Ltd. and its suppliers, if any.
#  The intellectual and technical concepts contained herein are
#  proprietary to MakinaRocks Co., Ltd. and its suppliers and may be
#  covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law. Dissemination
#  of this information or reproduction of this material is
#  strictly forbidden unless prior written permission is obtained
#  from MakinaRocks Co., Ltd.
#
import os
import warnings

from IPython.core.inputtransformer2 import TransformerManager

from . import info, mixins, utils


def format_with_black(code: str) -> str:
    """Format code with black."""
    # pylint:disable=broad-except,import-outside-toplevel
    try:
        import black

        code = black.format_str(code, mode=black.FileMode(line_length=119))
    except ImportError:
        warnings.showwarning(
            message="Failed to format the code. Try installing 'black' with a version later than '19.3b0'.",
            category=RuntimeWarning,
            filename="black",
            lineno=1,
        )
    except Exception:
        # Don't try any more formatting and return the converted code so far.
        pass

    return code


def format_with_isort(code: str) -> str:
    """Sort import statements with isort."""
    # pylint:disable=broad-except,import-outside-toplevel
    try:
        import isort

        code = isort.code(code)
    except ImportError:
        warnings.showwarning(
            message="Failed to sort import statements. Try installing 'isort' with a version later than '5.7'.",
            category=RuntimeWarning,
            filename="isort",
            lineno=1,
        )
    except Exception:
        # Don't try any more formatting and return the converted code so far.
        pass

    return code


def format_code(code: str) -> str:
    """normalize python code"""
    mgr = TransformerManager()
    code = mgr.transform_cell(code)
    code = "\n".join([line for line in code.split("\n") if line.strip() != ""])
    code = format_with_black(code=code)
    code = format_with_isort(code=code)
    return code


__all__ = ["info", "mixins", "utils"]


os.makedirs(utils.APP_TEMP_DIRECTORY, exist_ok=True)
os.makedirs(utils.APP_TEMP_DIRECTORY / "pipelines", exist_ok=True)
os.makedirs(utils.APP_TEMP_DIRECTORY / "executors", exist_ok=True)
