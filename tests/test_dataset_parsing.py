from __future__ import annotations

import json

from stil_semantic_change.data.loaders import (
    iter_roda_viva_batches,
    parse_brpolicorpus_date,
    parse_roda_viva_date,
)
from stil_semantic_change.utils.config.schema import DatasetConfig


def test_parse_brpolicorpus_date() -> None:
    parsed = parse_brpolicorpus_date("28/12/2000")
    assert parsed.year == 2000
    assert parsed.month == 12
    assert parsed.day == 28


def test_parse_roda_viva_date() -> None:
    parsed = parse_roda_viva_date("01/06/1987")
    assert parsed.year == 1987
    assert parsed.month == 6
    assert parsed.day == 1


def test_roda_viva_category_filter(tmp_path) -> None:
    transcript_dir = tmp_path / "csv"
    metadata_dir = tmp_path / "metadata"
    transcript_dir.mkdir()
    metadata_dir.mkdir()

    transcript = transcript_dir / "debate.csv"
    transcript.write_text(
        "DATA,ENTREVISTA,ORDEM,LOCUTOR,FALA\n01/06/1987,Debate,1,Ana,Democracia e economia.\n",
        encoding="utf-8",
    )
    metadata = metadata_dir / "debate_metadata.json"
    metadata.write_text(
        json.dumps(
            {
                "arquivo": "debate.csv",
                "data": "01/06/1987",
                "categoria": ["economia", "política"],
            }
        ),
        encoding="utf-8",
    )

    cfg = DatasetConfig(
        kind="roda_viva",
        name="rv",
        raw_dir=transcript_dir,
        metadata_dir=metadata_dir,
        file_glob="*.csv",
        freq="yearly",
        category_filter="política",
    )
    batches = list(iter_roda_viva_batches(cfg))
    assert len(batches) == 1
    assert batches[0]["slice_id"].iloc[0] == "1987"

    cfg_no_match = DatasetConfig(
        kind="roda_viva",
        name="rv",
        raw_dir=transcript_dir,
        metadata_dir=metadata_dir,
        file_glob="*.csv",
        freq="yearly",
        category_filter="esporte",
    )
    assert list(iter_roda_viva_batches(cfg_no_match)) == []
