from dataclasses import asdict, dataclass
from enum import Enum

from radon.metrics import mi_visit
from radon.raw import analyze
from radon.visitors import Class, ComplexityVisitor, Function


@dataclass
class RawMetrics:
    lines_of_code: int
    logical_lines_of_code: int
    source_lines_of_code: int
    comments: int
    single_comments: int
    multi: int
    blank: int

    def to_dict(self):
        return asdict(self)


@dataclass
class BlockMetrics:
    complexity: int
    name: str
    fullname: str
    block_type: str


class BlockType(Enum):
    FUNCTION = "Function"
    METHOD = "Method"
    CLASS = "Class"
    UNKNOWN = "Unknown"


def get_maintainability_index(filepath: str) -> float:
    with open(filepath, "r") as f:
        code = f.read()
    return mi_visit(code, True)


def get_complexity(filepath: str) -> int:
    """
    Get the total complexity of a file
    """
    with open(filepath, "r") as f:
        code = f.read()
    return ComplexityVisitor.from_code(code).total_complexity


def _get_block_type(block) -> BlockType:
    """
    Get the type of a block.
    """
    if isinstance(block, Function):
        if block.is_method:
            return BlockType.METHOD
        return BlockType.FUNCTION
    if isinstance(block, Class):
        return BlockType.CLASS
    return BlockType.UNKNOWN


def get_block_complexity(filepath: str) -> list[BlockMetrics]:
    with open(filepath, "r") as f:
        code = f.read()
    blocks = ComplexityVisitor.from_code(code).blocks
    return [
        BlockMetrics(
            complexity=block.complexity,
            name=block.name,
            fullname=block.fullname,
            block_type=_get_block_type(block),
        )
        for block in blocks
    ]


def get_raw_metrics(filepath: str) -> RawMetrics:
    with open(filepath, "r") as f:
        code = f.read()
    raw = analyze(code)
    return RawMetrics(
        lines_of_code=raw.loc,
        logical_lines_of_code=raw.lloc,
        source_lines_of_code=raw.sloc,
        comments=raw.comments,
        single_comments=raw.single_comments,
        multi=raw.multi,
        blank=raw.blank,
    ).to_dict()
