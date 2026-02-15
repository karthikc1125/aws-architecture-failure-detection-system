class PipelineState:
    """
    Manages the state of the execution pipeline.
    """
    def __init__(self):
        self.input = None
        self.failures = []
        self.architecture = None
        self.review = None
