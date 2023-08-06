import json
import logging
import os

from dql.client.checksum import md5
from dql.node import DirType
from dql.nodes_thread_pool import NodesThreadPool

logger = logging.getLogger("dql")


class NodesFetcher(NodesThreadPool):
    def __init__(self, client, data_storage, file_path, max_threads, cache):
        super().__init__(max_threads)
        self.client = client
        self.data_storage = data_storage
        self.file_path = file_path
        self.cache = cache

    def done_task(self, done):
        updated_nodes = []
        for d in done:
            lst = d.result()
            for node, checksum in lst:
                self.data_storage.update_checksum(node, checksum)
                node.checksum = checksum
                updated_nodes.append(node)
        return updated_nodes

    def do_task(self, chunk):
        res = []
        for node in chunk:
            if self.cache.exists(node.checksum):
                self.increase_counter(node.size)
                continue

            pair = self.fetch(self.client.name, node.path_str, node)
            res.append(pair)
        return res

    def fetch(self, bucket, path, node):
        from dvc_data.hashfile.build import _upload_file
        from dvc_objects.fs.callbacks import Callback

        if node.dir_type == DirType.TAR_FILE:
            return self._fetch_from_tar(node)

        class _CB(Callback):
            def relative_update(  # pylint: disable=no-self-argument
                _, inc: int = 1  # noqa: disable=no-self-argument
            ):
                self.increase_counter(inc)

        _, obj = _upload_file(
            f"{bucket}/{path}",
            self.client.fs,
            self.cache,
            self.cache,
            callback=_CB(),
        )

        return node, obj.hash_info.value

    def _fetch_from_tar(self, node):
        assert node.path_str.endswith(node.name)
        tar_path = node.path_str[: -len(node.name) - 1]
        assert node.sub_meta is not None
        offset = json.loads(node.sub_meta)["offset"]
        with self.client.open(tar_path) as f:
            f.seek(offset)
            contents = f.read(node.size)
        checksum = md5(contents).hexdigest()
        dst = self.cache.oid_to_path(checksum)
        if not os.path.exists(dst):
            # Create the file only if it's not already in cache
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, mode="wb") as f:
                f.write(contents)
        self.increase_counter(node.size)
        return node, checksum
