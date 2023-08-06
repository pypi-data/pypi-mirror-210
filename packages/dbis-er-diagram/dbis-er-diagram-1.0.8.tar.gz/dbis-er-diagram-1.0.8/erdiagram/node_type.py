from enum import Enum

from typeguard import typechecked


class NodeType(Enum):
    """Enum for node types."""

    ENTITY: int = 1
    ATTRIBUTE: int = 2
    RELATION: int = 3
    IS_A: int = 4
    COMPOSED_ATTRIBUTE: int = 5

    @typechecked
    def __str__(self) -> str:
        return str(self.name)
