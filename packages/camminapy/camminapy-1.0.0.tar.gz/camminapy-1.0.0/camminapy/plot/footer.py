import datetime
import os
import pwd
from typing import Any

import altair as alt
from git import Repo  # type: ignore


class Footer:
    """Add `.properties(title=Footer(repo).create())` to your plot to create a footer.

    IMPORTANT: As of now, this kills the original title.

    Workaround:
    Add `.properties(title={"text": "ACTUAL PLOT TITLE", **Footer().subtitle()})`
    Then it is not a footer but a subtitle.
    """

    def __init__(self, path: str | None = None):
        if path is None:
            path = os.getcwd()
        self.path = path
        self.repo = Repo(self.path)

    def get_username(self) -> str:
        """Returns the username."""
        return pwd.getpwuid(os.getuid())[0]

    def get_path(self) -> str:
        """Returns the path to the repo."""
        return self.path

    def get_time(self) -> str:
        """Returns the current time."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_git_status(self) -> str:
        """Returns git information."""
        commit = str(self.repo.head.commit)
        is_dirty = self.repo.is_dirty
        n = str(len(self.repo.untracked_files))

        return f"""{commit}, {"dirty," if is_dirty else ""} {n} untracked files"""

    def create_list(self) -> list[str]:
        """Creates a list of strings containing the footer content."""
        return [
            self.get_time(),
            self.get_username(),
            self.get_path(),
            self.get_git_status(),
        ]

    def create_joined(self) -> str:
        """Creates the string for the footer."""
        return ", ".join(self.create_list())

    def create(self, one_line=True) -> alt.TitleParams:
        """Creates an `alt.TitleParams` object with footer information.

        Add `.properties(title=Footer().create())` to your plot to create a footer.
        """
        if one_line:
            text = self.create_joined()
        else:
            text = self.create_list()
        return alt.TitleParams(
            text=text,
            baseline="bottom",
            orient="bottom",
            anchor="end",
            fontWeight="lighter",
            fontSize=10,
            color="grey",
            dy=20,
        )

    def subtitle(self) -> dict[str, Any]:
        """Creates subtitle information in dictionary form.

        Use via `.properties(title={"text": "ACTUAL PLOT TITLE", **Footer().subtitle()})`
        """
        return {
            "subtitle": self.create_joined(),
            "subtitleFontSize": 8,
            "subtitleFontWeight": "lighter",
            "subtitleColor": "gray",
        }
