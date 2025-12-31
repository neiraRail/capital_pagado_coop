# src/utils/exceptions.py

class PipelineError(Exception):
    """Error base del pipeline."""


class IngestionError(PipelineError):
    pass


class DiffGenerationError(PipelineError):
    pass


class ConsolidationError(PipelineError):
    pass


class ReportingError(PipelineError):
    pass
