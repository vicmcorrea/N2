__all__ = ["run_bert_confirmatory"]


def __getattr__(name: str):
    if name == "run_bert_confirmatory":
        from stil_semantic_change.contextual.confirmatory import run_bert_confirmatory

        return run_bert_confirmatory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
