from enum import Enum
from uuid import UUID


class PolicyType(Enum):

    DEFAULT_POLICY = UUID("a8dfdffc-27eb-45cc-9432-f3e6ffea3d58")
    ALLOW = UUID("2d98e317-d7a3-40f0-b360-ea3e84bda75f")
    BLOCK = UUID("e484c126-7e84-4e51-85e4-3fd4e4f87759")


class DefaultPolicyValues(Enum):

    ALLOW_ALL = "ALLOW_ALL"
    BLOCK_ALL = "BLOCK_ALL"


class DataSource(Enum):

    PI_HOLE = UUID("9ec62265-5475-4311-ba73-cc0d03eb6db0")


class ExternalSystemType(Enum):

    PI_HOLE_API = UUID("cb656898-15dc-441d-b860-de3d054a0647")