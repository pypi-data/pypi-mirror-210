import re

from lupin_grognard.core.commit.commit import Commit
from lupin_grognard.core.commit.commit_error import BodyError, ErrorCount
from lupin_grognard.core.commit.commit_reporter import CommitReporter
from lupin_grognard.core.config import (
    COMMIT_TYPE_MUST_HAVE_SCOPE,
    COMMIT_TYPE_MUST_NOT_HAVE_SCOPE,
    COMMIT_WITH_SCOPE,
    INITIAL_COMMIT,
    MIN_COMMIT_DESCR_LENTH,
    PATTERN,
    TITLE_FAILED,
)
from lupin_grognard.core.tools.utils import is_last_description_line_jama_reference


class CommitValidator(Commit):
    def __init__(
        self,
        commit: str,
        error_counter: ErrorCount,
        is_ci_mr_target_branch_main: bool = False,
    ):
        super().__init__(commit=commit)
        self.reporter = CommitReporter(commit=commit)
        self.error_counter = error_counter
        self.is_ci_mr_target_branch_main = is_ci_mr_target_branch_main

    def perform_checks(self, merge_option: bool) -> None:
        if merge_option:  # check merge commits have approvers
            if self._is_merge_commit(self.title):
                if not self._validate_commit_merge():
                    self.error_counter.increment_merge_error()
            else:
                if not self._validate_commit_title():
                    self.error_counter.increment_title_error()
                if not self._validate_body():
                    self.error_counter.increment_body_error()
        else:
            if not self._validate_commit_title():
                self.error_counter.increment_title_error()
            if not self._is_merge_commit(self.title):
                if not self._validate_body():
                    self.error_counter.increment_body_error()

    def _validate_commit_title(self) -> bool:
        if self._validate_commit_message(self.title, self.type, self.scope):
            self.reporter.display_valid_title_report()
            return True
        else:
            return False

    def _validate_body(self) -> bool:
        body_error = BodyError(
            is_conventional=[],
            descr_is_too_short=[],
            num_empty_line=0,
            jama=False,
        )
        # if target branch == main, the last line of the description must be a jama reference
        if self.is_ci_mr_target_branch_main:
            if not self.body or not self._is_last_description_line_jama_reference():
                if self.title not in INITIAL_COMMIT:
                    body_error.jama = True

        if self.body:
            for message in self.body:
                if self._is_conventional_commit_body_valid(message=message):
                    body_error.is_conventional.append(
                        message
                    )  # must not start with a conventional message
                if not self._is_commit_body_line_length_valid(message=message):
                    if message != "":
                        body_error.descr_is_too_short.append(message)
                    else:
                        body_error.num_empty_line += 1
        if any(
            [
                body_error.is_conventional,
                body_error.descr_is_too_short,
                body_error.num_empty_line > 0,
                body_error.jama,
            ]
        ):
            self.reporter.display_body_report(body_error=body_error)
            return False
        return True

    def _validate_commit_message(self, commit_msg: str, type: str, scope: str) -> bool:
        if self._is_special_commit(commit_msg=commit_msg):
            return True

        match type:
            case None:
                self.reporter.display_invalid_title_report(error_message=TITLE_FAILED)
                return False
            case match_type if (match_type := type) in COMMIT_WITH_SCOPE:
                return self._validate_commit_message_for_specific_type(
                    scope=scope, type=match_type
                )
            case _:
                return self._validate_commit_message_for_generic_type(
                    type=type, scope=scope
                )

    def _is_conventional_commit_body_valid(self, message: str) -> bool:
        """Checks if the line in the body of a commit message starts with a conventional commit"""
        return bool(re.match(PATTERN, message))

    def _is_commit_body_line_length_valid(self, message: str) -> bool:
        """Checks if the body line is not less than MIN_COMMIT_DESCR_LENTH"""
        return len(message) >= MIN_COMMIT_DESCR_LENTH

    def _is_last_description_line_jama_reference(self) -> bool:
        return is_last_description_line_jama_reference(body=self.body)

    def _is_special_commit(self, commit_msg: str) -> bool:
        """Checks if the commit is a Merge or in the list of initial commits"""
        return commit_msg.startswith("Merge") or commit_msg in INITIAL_COMMIT

    def _is_merge_commit(self, commit_msg: str) -> bool:
        return commit_msg.startswith("Merge")

    def _validate_commit_merge(self) -> bool:
        self.reporter.display_merge_report(approvers=self.approvers)
        if len(self.approvers) < 1:
            return False
        return True

    def _validate_commit_message_for_specific_type(self, scope: str, type: str) -> bool:
        """
        Validates the scope for a COMMIT_WITH_SCOPE list.
        If the scope is (change) then the commit title and description
        must not contain the words 'remove' or 'removed'
        """
        if scope is None or scope not in ["(add)", "(change)", "(remove)"]:
            self.reporter.display_invalid_title_report(
                error_message=COMMIT_TYPE_MUST_HAVE_SCOPE.format(type=type)
            )
            return False
        else:
            if scope == "(change)":
                return self._validate_change_scope_without_remove_word()
            return True

    def _contains_remove_words(self, text: str) -> bool:
        """Checks if the text contains the words 'remove' or 'removed'"""
        words = text.lower().split(" ")
        return any(str in words for str in ["remove", "removed"])

    def _validate_change_scope_without_remove_word(self):
        """
        Validate that a commit with the scope (change) does not contain the words
        'remove' and 'removed' in the title or description
        """
        full_text = self.title + " " + " ".join(self.body) if self.body else self.title
        if self._contains_remove_words(text=full_text):
            self.reporter.display_invalid_title_report(
                error_message=(
                    "Found a commit message that talks about removing something while given "
                    "scope is 'change': change scope to 'remove' or update the commit description"
                )
            )
            return False
        return True

    def _validate_commit_message_for_generic_type(self, type, scope: str) -> bool:
        """Validates other commit types do not contain a scope"""
        if scope is None:
            return True
        else:
            error_message = COMMIT_TYPE_MUST_NOT_HAVE_SCOPE.format(type, type)
            self.reporter.display_invalid_title_report(error_message=error_message)
            return False
