from typing import Optional
from .common import (
    Validateable,
)


class Version(Validateable):
    @classmethod
    def from_str(cls, input_str: str):
        snapshot_parsed = input_str.split("-")
        version_str = snapshot_parsed[0]
        suffix_str = None
        if len(snapshot_parsed) > 1:
            suffix_str = snapshot_parsed[1]
        version_no_parsed = [int(x) for x in version_str.split(".")]
        return cls(
            version_no_parsed,
            suffix_str,
            input_str,
        )

    def __init__(
        self,
        version_list: list,
        snapshot_suffix: Optional[str] = None,
        version_str: Optional[str] = None,
    ):
        self.version_list = version_list
        self.snapshot_suffix = snapshot_suffix
        self.version_string = version_str

    def __eq__(self, other):
        return other and self.to_string() == other.to_string()

    def __hash__(self) -> int:
        return self.to_string().__hash__()

    def is_snapshot(self):
        return self.snapshot_suffix is not None

    def to_string(self) -> str:
        version_no = ".".join([str(x) for x in self.version_list])
        if self.is_snapshot():
            return f"{version_no}-{self.snapshot_suffix}"
        return version_no

    def validate(self):
        result = []
        result += self.__validate_is_not_empty__("version_list")
        if self.version_list and len(self.version_list) < 3:
            result += ["version_list must have at least 3 levels."]
        if (
            self.version_list
            and self.version_string
            and self.to_string() != self.version_string
        ):
            result += [
                f"version_string not parsed correct. Input was {self.version_string} parsed was {self.to_string()}"
            ]
        return result

    def create_bump(self, snapshot_suffix: Optional[str] = None):
        new_version_list = self.version_list.copy()
        if self.is_snapshot():
            return Version(
                new_version_list, snapshot_suffix=self.snapshot_suffix, version_str=None
            )
        else:
            new_version_list[2] += 1
            return Version(
                new_version_list, snapshot_suffix=snapshot_suffix, version_str=None
            )

    def create_patch(self):
        new_version_list = self.version_list.copy()
        if self.is_snapshot():
            return Version(new_version_list, snapshot_suffix=None, version_str=None)
        else:
            new_version_list[2] += 1
            return Version(new_version_list, snapshot_suffix=None, version_str=None)

    def create_minor(self):
        new_version_list = self.version_list.copy()
        if self.is_snapshot() and new_version_list[2] == 0:
            return Version(new_version_list, snapshot_suffix=None, version_str=None)
        else:
            new_version_list[2] = 0
            new_version_list[1] += 1
            return Version(new_version_list, snapshot_suffix=None, version_str=None)

    def create_major(self):
        new_version_list = self.version_list.copy()
        if self.is_snapshot() and new_version_list[2] == 0 and new_version_list[1] == 0:
            return Version(new_version_list, snapshot_suffix=None, version_str=None)
        else:
            new_version_list[2] = 0
            new_version_list[1] = 0
            new_version_list[0] += 1
            return Version(new_version_list, snapshot_suffix=None, version_str=None)
