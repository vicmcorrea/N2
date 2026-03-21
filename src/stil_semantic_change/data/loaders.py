from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pandas as pd

from stil_semantic_change.utils.config.schema import DatasetConfig
from stil_semantic_change.utils.periods import make_slice_id

logger = logging.getLogger(__name__)
CSV_CHUNK_SIZE = 1000


def parse_brpolicorpus_date(value: str) -> pd.Timestamp:
    return pd.to_datetime(value, format="%d/%m/%Y", errors="raise")


def parse_roda_viva_date(value: str) -> pd.Timestamp:
    return pd.to_datetime(value, format="%d/%m/%Y", errors="raise")


def _limit_files(files: list[Path], limit: int | None) -> list[Path]:
    return files[:limit] if limit is not None else files


def _iter_csv_chunks(
    file_path: Path,
    *,
    usecols: list[str],
    limit_rows: int | None,
) -> Iterator[pd.DataFrame]:
    if limit_rows is not None:
        yield pd.read_csv(
            file_path,
            usecols=usecols,
            nrows=limit_rows,
        )
        return

    yield from pd.read_csv(
        file_path,
        usecols=usecols,
        chunksize=CSV_CHUNK_SIZE,
    )


def iter_dataset_batches(cfg: DatasetConfig) -> Iterator[pd.DataFrame]:
    if cfg.kind == "brpolicorpus_floor":
        yield from iter_brpolicorpus_floor_batches(cfg)
        return
    if cfg.kind == "roda_viva":
        yield from iter_roda_viva_batches(cfg)
        return
    raise ValueError(f"Unsupported dataset kind: {cfg.kind}")


def iter_brpolicorpus_floor_batches(cfg: DatasetConfig) -> Iterator[pd.DataFrame]:
    files = _limit_files(sorted(cfg.raw_dir.glob(cfg.file_glob)), cfg.limit_files)
    required_columns = [
        cfg.date_column or "Data",
        cfg.text_column or "Discurso",
        "Apelido",
        "Estado",
        "Partido",
        "Sessao",
        "TipoSessaoTXT",
    ]

    for file_path in files:
        file_stem = file_path.stem
        row_offset = 0
        for frame in _iter_csv_chunks(
            file_path,
            usecols=required_columns,
            limit_rows=cfg.limit_rows_per_file,
        ):
            frame = frame.rename(
                columns={
                    cfg.date_column or "Data": "date_raw",
                    cfg.text_column or "Discurso": "text",
                    "Apelido": "speaker",
                    "Estado": "state",
                    "Partido": "party",
                    "Sessao": "session",
                    "TipoSessaoTXT": "session_type",
                }
            ).reset_index(drop=True)
            frame["raw_row_id"] = np.arange(row_offset, row_offset + len(frame), dtype=np.int64)
            row_offset += len(frame)
            frame = frame.dropna(subset=["date_raw", "text"]).reset_index(drop=True)
            if frame.empty:
                continue

            frame["date"] = frame["date_raw"].map(parse_brpolicorpus_date)
            frame["slice_id"] = frame["date"].map(lambda value: make_slice_id(value, cfg.freq))
            frame["doc_id"] = file_stem + ":" + frame["raw_row_id"].astype(str)
            frame["source_file"] = file_path.name
            frame["title"] = frame["session_type"].fillna("")
            yield frame[
                [
                    "doc_id",
                    "date",
                    "slice_id",
                    "text",
                    "source_file",
                    "speaker",
                    "state",
                    "party",
                    "session",
                    "title",
                ]
            ].copy()


def _load_roda_viva_metadata(metadata_dir: Path) -> dict[str, dict[str, object]]:
    metadata_by_file: dict[str, dict[str, object]] = {}
    for path in sorted(metadata_dir.glob("*_metadata.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        archive_name = str(payload["arquivo"])
        metadata_by_file[archive_name] = payload
    return metadata_by_file


def iter_roda_viva_batches(cfg: DatasetConfig) -> Iterator[pd.DataFrame]:
    if cfg.metadata_dir is None:
        raise ValueError("Roda Viva datasets require metadata_dir")

    metadata_by_file = _load_roda_viva_metadata(cfg.metadata_dir)
    files = _limit_files(sorted(cfg.raw_dir.glob(cfg.file_glob)), cfg.limit_files)

    for file_path in files:
        metadata = metadata_by_file.get(file_path.name)
        if metadata is None:
            logger.warning("Skipping %s because metadata is missing", file_path.name)
            continue
        file_stem = file_path.stem

        categories = [str(item) for item in metadata.get("categoria", [])]
        if cfg.category_filter and cfg.category_filter not in categories:
            continue

        row_offset = 0
        for frame in _iter_csv_chunks(
            file_path,
            usecols=["DATA", "ENTREVISTA", "ORDEM", "LOCUTOR", "FALA"],
            limit_rows=cfg.limit_rows_per_file,
        ):
            frame = frame.rename(
                columns={
                    "DATA": "date_raw",
                    "ENTREVISTA": "title",
                    "ORDEM": "turn_order",
                    "LOCUTOR": "speaker",
                    "FALA": "text",
                }
            ).reset_index(drop=True)
            frame["raw_row_id"] = np.arange(row_offset, row_offset + len(frame), dtype=np.int64)
            row_offset += len(frame)
            frame = frame.dropna(subset=["text"]).reset_index(drop=True)
            if frame.empty:
                continue

            date_value = str(metadata.get("data") or frame.loc[0, "date_raw"])
            parsed_date = parse_roda_viva_date(date_value)
            frame["date"] = parsed_date
            frame["slice_id"] = make_slice_id(parsed_date, cfg.freq)
            frame["source_file"] = file_path.name
            frame["categories"] = "|".join(categories)
            frame["doc_id"] = file_stem + ":" + frame["raw_row_id"].astype(str)
            yield frame[
                [
                    "doc_id",
                    "date",
                    "slice_id",
                    "text",
                    "source_file",
                    "speaker",
                    "title",
                    "turn_order",
                    "categories",
                ]
            ].copy()
