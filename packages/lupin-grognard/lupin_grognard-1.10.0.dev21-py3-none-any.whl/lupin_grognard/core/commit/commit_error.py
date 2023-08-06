import sys
from dataclasses import dataclass
from typing import List

from lupin_grognard.core.config import (
    BODY_FAILED,
    FAILED,
    MERGE_FAILED,
    SUCCESS,
    TITLE_FAILED,
)
from lupin_grognard.core.tools.utils import warn


class ErrorCount:
    def __init__(self):
        self.body_error = 0
        self.title_error = 0
        self.merge_error = 0

    def increment_body_error(self):
        self.body_error += 1

    def increment_title_error(self):
        self.title_error += 1

    def increment_merge_error(self):
        self.merge_error += 1

    def error_report(self, permissive_mode: bool):
        if not (self.title_error + self.body_error + self.merge_error):
            print(SUCCESS)
        else:
            print(FAILED)
            print(
                f"Errors found: {self.title_error + self.body_error + self.merge_error}"
            )
            if self.title_error > 0:
                print(TITLE_FAILED)
            if self.body_error > 0:
                print(BODY_FAILED)
            if self.merge_error > 0:
                print(MERGE_FAILED)

            if permissive_mode:
                warn(msg="ignoring command failure because running in permissive mode")
                sys.exit(0)
            else:
                sys.exit(1)


@dataclass
class BodyError:
    """
    Encapsulates the errors related to commit message body validation.

    :attributes:
        is_conventional (List[str]): List of commit description lines that start with a conventional commit.
        descr_is_too_short (List[str]): List of commit description lines that are too short.
        num_empty_line (int): Number of empty lines in the commit message.
        jama (bool): Indicates if the last line of the commit description should start with a item JAMA.
    """

    is_conventional: List[str]
    descr_is_too_short: List[str]
    num_empty_line: int
    jama: bool
