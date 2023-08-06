from typing import Optional, List
from pathlib import Path
from .common import (
    Validateable,
    ReleaseType,
)
from .version import (
    Version,
)


class Release(Validateable):
    def __init__(self, inp: dict, version: Optional[Version]):
        self.release_type = ReleaseType[inp.get("release_type", "NONE")]
        self.release_main_branch = inp.get("release_main_branch", "main")
        self.release_current_branch = inp.get("release_current_branch")
        self.release_primary_build_file = inp.get(
            "release_primary_build_file", "./project.clj"
        )
        self.release_secondary_build_files = inp.get(
            "release_secondary_build_files", []
        )
        self.version = version

    def validate(self):
        result = []
        result += self.__validate_is_not_empty__("release_type")
        result += self.__validate_is_not_empty__("release_main_branch")
        result += self.__validate_is_not_empty__("release_current_branch")
        result += self.__validate_is_not_empty__("release_primary_build_file")
        result += self.__validate_is_not_empty__("version")
        try:
            Path(self.release_primary_build_file)
        except Exception as e:
            result.append(
                f"release_primary_build_file must be a valid path but was {e}"
            )
        for path in self.release_secondary_build_files:
            try:
                Path(path)
            except Exception as e:
                result.append(
                    f"release_secondary_build_file must be contain valid paths but was {e}"
                )
        if self.version:
            result += self.version.validate()
        if (
            self.release_type is not None
            and self.release_type != ReleaseType.NONE
            and self.release_main_branch != self.release_current_branch
        ):
            result.append(f"Releases are allowed only on {self.release_main_branch}")
        return result

    def build_files(self) -> List[str]:
        result = [self.release_primary_build_file]
        result += self.release_secondary_build_files
        return result
