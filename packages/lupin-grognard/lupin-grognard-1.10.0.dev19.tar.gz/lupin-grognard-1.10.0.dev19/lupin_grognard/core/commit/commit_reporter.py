from typing import List

from emoji import emojize

from lupin_grognard.core.commit.commit import Commit
from lupin_grognard.core.commit.commit_error import BodyError
from lupin_grognard.core.config import EMOJI_CHECK, EMOJI_CROSS


class CommitReporter(Commit):
    def __init__(self, commit: str):
        super().__init__(commit=commit)

    def display_valid_title_report(self) -> None:
        print(emojize(f"{EMOJI_CHECK} Commit {self.hash[:6]}: {self.title}"))

    def display_invalid_title_report(self, error_message) -> None:
        print(emojize(f"{EMOJI_CROSS} Commit {self.hash[:6]}: {self.title}"))
        print(f"   {error_message}")

    def display_body_report(self, body_error: BodyError) -> None:
        print(emojize(f"{EMOJI_CROSS} Error in message discription:"))

        for message in body_error.is_conventional:
            print(f"    The line can't start with a conventional commit: '{message}'")
        for message in body_error.descr_is_too_short:
            print(f"    Text is too short in the commit description: '{message}'")

        if body_error.num_empty_line == 1:
            print("    Found an empty line in the commit description")
        elif body_error.num_empty_line > 1:
            print(
                f"    Found {body_error.num_empty_line} empty lines in the commit description"
            )

        if body_error.jama:
            print(
                (
                    "    The last line of the commit description must starts with 'JAMA-' followed by the project "
                    "ID in JAMA of the SW Requirement attached to this commit, for example 'JAMA-SmlPrep-SUBSR-139'"
                )
            )

    def display_merge_report(self, approvers: List[str]):
        if len(approvers) > 1:
            many_approvers = ", ".join(approvers[:-1]) + " and " + approvers[-1]
            print(
                emojize(
                    f"{EMOJI_CHECK} Merge commit {self.hash[:6]}: Approvers: {many_approvers}"
                )
            )
        elif len(approvers) == 1:
            print(
                emojize(
                    f"{EMOJI_CHECK} Merge commit {self.hash[:6]}: Approver: {approvers[0]}"
                )
            )
        else:
            print(
                emojize(
                    f"{EMOJI_CROSS} Merge commit {self.hash[:6]}: No approver found"
                )
            )
        print(f"   - Merged on {self.author_date} by {self.author}, {self.author_mail}")
        print(
            f"   - Closes issue: {self.closes_issues if self.closes_issues else 'Not found'}"
        )
        print(f"   - Commit title: {self.title}")
