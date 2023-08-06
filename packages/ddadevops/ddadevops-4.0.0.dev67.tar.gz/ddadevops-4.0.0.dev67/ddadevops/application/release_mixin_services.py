from typing import List
from pathlib import Path
from ..infrastructure import GitApi, BuildFileRepository
from ..domain import Version, Release, ReleaseType


class ReleaseService:
    def __init__(self, git_api: GitApi, build_file_repository: BuildFileRepository):
        self.git_api = git_api
        self.build_file_repository = build_file_repository

    @classmethod
    def prod(cls, base_dir: str):
        return cls(
            GitApi(),
            BuildFileRepository(base_dir),
        )

    def prepare_release(self, release: Release):
        match release.release_type:
            case ReleaseType.MAJOR:
                version = release.version.create_major()
            case ReleaseType.MINOR:
                version = release.version.create_minor()
            case ReleaseType.PATCH:
                version = release.version.create_patch()
            case ReleaseType.NONE:
                return
        message = f"release: {version.to_string()}"
        self.__set_version_and_commit__(version, release.build_files(), message)

    def tag_bump_and_push_release(self, release: Release):
        match release.release_type:
            case ReleaseType.MAJOR:
                release_version = release.version.create_major()
            case ReleaseType.MINOR:
                release_version = release.version.create_minor()
            case ReleaseType.PATCH:
                release_version = release.version.create_patch()
            case ReleaseType.NONE:
                return
        bump_version = release_version.create_bump("SNAPSHOT")
        release_message = f"release: {release_version.to_string()}"
        bump_message = f"bump version to: {bump_version.to_string()}"
        self.git_api.tag_annotated(release_version.to_string(), release_message, 0)
        self.__set_version_and_commit__(
            bump_version,
            release.build_files(),
            bump_message,
        )
        self.git_api.push()

    def __set_version_and_commit__(
        self, version: Version, build_file_ids: List[str], message: str
    ):
        for build_file_id in build_file_ids:
            build_file = self.build_file_repository.get(Path(build_file_id))
            build_file.set_version(version)
            self.build_file_repository.write(build_file)
            self.git_api.add_file(build_file.file_path)
        self.git_api.commit(message)
