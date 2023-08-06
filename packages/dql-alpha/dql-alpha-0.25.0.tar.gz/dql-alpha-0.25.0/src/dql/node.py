from datetime import datetime
from typing import Any, Dict, List, Optional

import attrs

from dql.utils import time_to_str


class DirType:
    FILE = 0
    DIR = 1
    ROOT = 2
    TAR_FILE = 3  # TAR archive member
    TAR_DIR = 4
    TAR_ARCHIVE = 5


class DirTypeGroup:
    """
    Groups of DirTypes for selecting storage nodes or dataset entries.

    When filtering with FILE and DIR together or alternatively when
    using SUBOBJ_FILE and SUBOBJ_DIR together, we achieve a
    filesystem-compatible view of a storage location. Such a view
    avoids path conflicts and could be downloaded as a directory tree.

    FILE, DIR
      The respective types which appear on the indexed filesystem or
      object store as a file or directory. This excludes subobjects.

    SUBOBJ_FILE, SUBOBJ_DIR
      The respective types that we want to consider to be a file or
      directory when including subobjects which are generated from other
      files. In this case, we treat tar archives as directories so tar
      subobjects (TAR_FILE) can be viewed under the directory tree of
      the parent tar archive.

    OBJ
      All object types, including regular files and subobjects. These
      are the entries that should be copied to a dataset.
    """

    FILE = (DirType.FILE, DirType.TAR_ARCHIVE)
    DIR = (DirType.DIR, DirType.ROOT)
    SUBOBJ_FILE = (DirType.FILE, DirType.TAR_FILE)
    SUBOBJ_DIR = (DirType.DIR, DirType.ROOT, DirType.TAR_DIR, DirType.TAR_ARCHIVE)
    OBJ = (DirType.FILE, DirType.TAR_FILE, DirType.TAR_ARCHIVE)


DIRTYPE_DIRS = (DirType.DIR, DirType.ROOT, DirType.TAR_DIR)


@attrs.define
class Node:
    id: int = 0
    dir_type: Optional[int] = None
    parent_id: Optional[int] = None
    name: Optional[str] = None
    checksum: str = ""
    etag: str = ""
    version: Optional[str] = None
    is_latest: bool = True
    last_modified: Optional[datetime] = None
    size: int = 0
    owner_name: str = ""
    owner_id: str = ""
    path_str: str = ""
    anno: Optional[str] = None
    valid: bool = True
    random: int = -1
    sub_meta: Optional[str] = None
    partial_id: int = 0

    @property
    def basename(self):
        # Note: differs from self.name only for TAR sub-objects
        return self.name.rsplit("/", 1)[-1]

    @property
    def is_dir(self) -> bool:
        return self.dir_type in DIRTYPE_DIRS

    @property
    def is_container(self) -> bool:
        return self.dir_type in DirTypeGroup.SUBOBJ_DIR

    @property
    def is_downloadable(self) -> bool:
        return bool(not self.is_dir and self.name)

    def sql_schema(self):
        return ",".join(["?"] * len(self))

    def append_to_file(self, fd, path: str):
        fd.write(f"- name: {path}\n")
        fd.write(f"  etag: {self.etag}\n")
        checksum = self.checksum
        if checksum:
            fd.write(f"  checksum: {self.checksum}\n")
        version = self.version
        if version:
            fd.write(f"  version: {self.version}\n")
        fd.write(f"  last_modified: '{time_to_str(self.last_modified)}'\n")
        size = self.size
        fd.write(f"  size: {self.size}\n")
        return size

    def get_metafile_data(self, path: str):
        data: Dict[str, Any] = {
            "name": path,
            "etag": self.etag,
        }
        checksum = self.checksum
        if checksum:
            data["checksum"] = checksum
        version = self.version
        if version:
            data["version"] = version
        data["last_modified"] = time_to_str(self.last_modified)
        data["size"] = self.size
        return data

    @property
    def full_path(self) -> str:
        if self.is_dir and self.path_str:
            return self.path_str + "/"
        return self.path_str


@attrs.define
class NodeWithPath:
    n: Node
    path: List[str] = []

    def append_to_file(self, fd):
        return self.n.append_to_file(fd, "/".join(self.path))

    def get_metafile_data(self):
        return self.n.get_metafile_data("/".join(self.path))

    @property
    def full_path(self) -> str:
        path = "/".join(self.path)
        if self.n.is_dir and path:
            path += "/"
        return path


TIME_FMT = "%Y-%m-%d %H:%M"


def long_line_str(name: str, timestamp: Optional[datetime], owner: str) -> str:
    if timestamp is None:
        time = "-"
    else:
        time = timestamp.strftime(TIME_FMT)
    return f"{owner: <19} {time: <19} {name}"
