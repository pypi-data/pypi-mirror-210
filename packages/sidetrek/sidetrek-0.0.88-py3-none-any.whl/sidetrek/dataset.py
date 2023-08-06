from typing import Any, Dict, Optional, Union
import dataclasses
from torchdata.datapipes.iter import IterableWrapper, HuggingFaceHubReader
from sidetrek.types.dataset import SidetrekDataset, SidetrekIterDataPipe, SidetrekMapDataPipe


def build_dataset(
    io: str,
    source: str,
    # options: Dict = {},
) -> SidetrekDataset:
    # return SidetrekDataset(io=io, source=source, options=options)
    return SidetrekDataset(io=io, source=source)


def load_dataset(
    ds: SidetrekDataset,
    data_type: Union[str, None] = None,  # csv, images, etc.
    compression: Union[str, None] = None,  # zip, tar, etc.
    random_split: Union[Dict, None] = None,  # weights={"train": 0.5, "valid": 0.5}, seed=0, total_length=10, target: 'train'
    streaming: bool = True,
) -> Union[SidetrekIterDataPipe, SidetrekMapDataPipe]:
    # Handle io
    io = ds.io
    source = ds.source
    ds_dict = dataclasses.asdict(ds)
    ds_options = ds_dict.get("options", {})

    io_dp: SidetrekIterDataPipe
    if io == "upload":
        fsspec_options = ds_options.get("fsspec", {})
        fsspec_mode = fsspec_options.get("mode", "r") if compression is None else fsspec_options.get("mode", "rb")
        kwargs_for_open = fsspec_options.get("kwargs_for_open", {})
        storage_kwargs = fsspec_options.get("storage_kwargs", {})

        dp_s3_files = IterableWrapper([source]).list_files_by_fsspec()
        dp_s3_open_files = dp_s3_files.open_files_by_fsspec(mode=fsspec_mode, kwargs_for_open=kwargs_for_open, **storage_kwargs)
        dp_sharded_s3_files = dp_s3_open_files.shuffle().sharding_filter()
        io_dp = dp_sharded_s3_files

    if io == "http":
        http_options = ds_options.get("http", {})
        timeout = http_options.get("timeout", 120)
        request_kwargs = http_options.get("request_kwargs", {})

        dp_http_urls = IterableWrapper([source])
        sharded_http_urls = dp_http_urls.shuffle().sharding_filter()
        http_reader_dp = sharded_http_urls.read_from_http(timeout=timeout, **request_kwargs)
        io_dp = http_reader_dp

    if io == "hugging_face":
        hugging_face_options = ds_options.get("hugging_face", {})
        revision = hugging_face_options.get("revision", "main")

        # `source`: full Hugging Face dataset repo name - i.e. `owner/repo`
        huggingface_reader_dp = HuggingFaceHubReader(source, revision=revision)
        sharded_huggingface_reader_dp = huggingface_reader_dp.shuffle().sharding_filter()
        io_dp = sharded_huggingface_reader_dp

    if io == "gdrive":
        dp_gdrive_urls = IterableWrapper([source])
        sharded_gdrive_urls = dp_gdrive_urls.shuffle().sharding_filter()
        gdrive_reader_dp = sharded_gdrive_urls.read_from_gdrive(source, revision=revision)
        io_dp = gdrive_reader_dp

    # Handle compression
    decompressed_dp: SidetrekIterDataPipe
    if compression is None:
        decompressed_dp = io_dp
    else:
        if compression == "zip":
            decompressed_dp = io_dp.load_from_zip()

        if compression == "tar":
            if streaming == True:
                decompressed_dp = io_dp.load_from_tar(mode="r|")  # `r|` denotes streaming version (as opposed to the usual `r:`)
            else:
                decompressed_dp = io_dp.load_from_tar()

        if compression == "rar":
            decompressed_dp = io_dp.load_from_rar()

        if compression == "bz2":
            decompressed_dp = io_dp.load_from_bz2()

        if compression == "xz":
            decompressed_dp = io_dp.load_from_xz()

    # Handle data_types (e.g. csv, images, timeseries, audio, etc.)
    processed_dp: SidetrekIterDataPipe
    if data_type is None:
        processed_dp = decompressed_dp
    else:
        if data_type == "csv":
            csv_options = ds_options.get("csv", {})
            delimiter = csv_options.get("delimiter", ",")
            processed_dp = decompressed_dp.parse_csv(delimiter=delimiter)

    # Handle random_split
    split_dp: SidetrekIterDataPipe
    if random_split is None:
        split_dp = processed_dp
    else:
        split_dp = processed_dp.random_split(random_split)

    # Finally, handle streaming
    final_dp: Union[SidetrekIterDataPipe, SidetrekMapDataPipe]
    if streaming is True:
        final_dp = split_dp
    else:
        final_dp = split_dp.to_map_datapipe()

    return final_dp
