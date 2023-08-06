#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#
#

class DataHelperError(Exception):
  """Base class for all DataHelper errors."""


class PipelineError(DataHelperError):
  """An error in the pipeline object (e.g. a PValue not linked to it)."""


class PValueError(DataHelperError):
  """An error related to a PValue object (e.g. value is not computed)."""


class RunnerError(DataHelperError):
  """An error related to a Runner object (e.g. cannot find a runner to run)."""


class RuntimeValueProviderError(RuntimeError):
  """An error related to a ValueProvider object raised during runtime."""


class SideInputError(DataHelperError):
  """An error related to a side input to a parallel Do operation."""


class TransformError(DataHelperError):
  """An error related to a PTransform object."""