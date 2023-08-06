from typing import cast

from s3fs import S3FileSystem

from .fsspec import DELIMITER, TIME_ZERO, FSSpecClient

UPDATE_CHUNKSIZE = 1000


class ClientS3(FSSpecClient):
    FS_CLASS = S3FileSystem
    PREFIX = "s3://"
    protocol = "s3"

    @classmethod
    def create_fs(cls, **kwargs) -> S3FileSystem:
        if "aws_anon" in kwargs:
            kwargs.setdefault("anon", kwargs.pop("aws_anon"))
        if "aws_endpoint_url" in kwargs:
            kwargs.setdefault("client_kwargs", {}).setdefault(
                "endpoint_url", kwargs.pop("aws_endpoint_url")
            )
        if "aws_key" in kwargs:
            kwargs.setdefault("key", kwargs.pop("aws_key"))
        if "aws_secret" in kwargs:
            kwargs.setdefault("secret", kwargs.pop("aws_secret"))
        if "aws_token" in kwargs:
            kwargs.setdefault("token", kwargs.pop("aws_token"))

        # We want to use newer v4 signature version since regions added after
        # 2014 are not going to support v2 which is the older one.
        # All regions support v4.
        kwargs.setdefault("config_kwargs", {}).setdefault("signature_version", "s3v4")

        return cast(S3FileSystem, super().create_fs(**kwargs))

    def url(self, path: str, expires: int = 3600) -> str:
        """
        Returns a signed URL of specific file in a bucket that lasts for some time,
        which is defined by expires argument.
        """
        full_path = self.get_full_path(path)
        # For some reason (probably because of caching) it figures out the right
        # bucket region when calling info before, otherwise it tries to guess it
        # which leads to random failures
        self.fs.info(full_path)
        return self.fs.url(full_path, expires=expires)

    async def _fetch_dir(self, dir_id, prefix, pbar, listing, data_storage, partial_id):
        if prefix:
            prefix = prefix.lstrip(DELIMITER) + DELIMITER
        files = []
        subdirs = set()
        subdir_names = set()
        ignore_count = 0
        pbar_updated = 0
        # pylint:disable-next=protected-access
        async for info in self.fs._iterdir(self.name, prefix=prefix, versions=True):
            full_path = info["name"]
            _, subprefix, _ = self.fs.split_path(info["name"])
            if info["type"] == "directory":
                name = full_path.split(DELIMITER)[-1]
                new_dir_id = await listing.insert_dir(
                    dir_id,
                    name,
                    TIME_ZERO,
                    subprefix,
                    partial_id,
                    data_storage=data_storage,
                )
                subdirs.add((new_dir_id, subprefix))
                subdir_names.add(name)
            else:
                files.append(self._dict_from_info(info, dir_id, subprefix, partial_id))
                pbar_update_count = len(files) - pbar_updated
                if pbar_update_count >= UPDATE_CHUNKSIZE:
                    pbar.update(pbar_update_count)
                    pbar_updated += pbar_update_count
        for f in files:
            if not f["name"] or f["name"] in subdir_names:
                # Set files that conflict with directories as not valid
                # Files without a name are of a prefix like "dir/" where the name
                # ends up being empty after the split on "/"
                # And the conflicting files have prefixes like "dir" where there is
                # also an "dir" directory, for example "dir/file1" as well.
                f["valid"] = False
                ignore_count += 1
        if files:
            await data_storage.insert_entries(files)
            await data_storage.update_last_inserted_at()
            pbar_update_count = len(files) - pbar_updated
            pbar.update(pbar_update_count)
        pbar.update(len(subdirs))
        return subdirs, ignore_count

    @staticmethod
    def clean_s3_version(ver):
        return ver if ver != "null" else ""

    def _dict_from_info(self, v, parent_id, path, partial_id):
        return {
            "is_dir": False,
            "parent_id": parent_id,
            "path": path,
            "name": v.get("Key", "").split(DELIMITER)[-1],
            # 'expires': expires,
            "checksum": "",
            "etag": v.get("ETag", "").strip('"'),
            "version": ClientS3.clean_s3_version(v.get("VersionId", "")),
            "is_latest": v.get("IsLatest", True),
            "last_modified": v.get("LastModified", ""),
            "size": v.get("Size", ""),
            # 'storage_class': v.get('StorageClass'),
            "owner_name": v.get("Owner", {}).get("DisplayName", ""),
            "owner_id": v.get("Owner", {}).get("ID", ""),
            "anno": None,
            "partial_id": partial_id,
        }
