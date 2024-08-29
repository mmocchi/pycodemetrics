from enum import Enum

from pydantic import BaseModel
from radon.metrics import mi_visit
from radon.raw import analyze
from radon.visitors import Class, ComplexityVisitor, Function


class BlockType(Enum):
    FUNCTION = "Function"
    METHOD = "Method"
    CLASS = "Class"
    UNKNOWN = "Unknown"


class RawMetrics(BaseModel, frozen=True, extra="forbid"):
    """
    生のコードメトリクスを表すデータクラス。

    このクラスは、コードの行数やコメント数などの基本的なメトリクスを保持します。

    Attributes:
        lines_of_code (int): コードの総行数。
        logical_lines_of_code (int): 論理行数。
        source_lines_of_code (int): ソースコードの行数。
        comments (int): コメントの総数。
        single_comments (int): 単一行コメントの数。
        multi (int): 複数行コメントの数。
        blank (int): 空行の数。
    """

    lines_of_code: int
    logical_lines_of_code: int
    source_lines_of_code: int
    comments: int
    single_comments: int
    multi: int
    blank: int

    def to_dict(self) -> dict:
        return self.model_dump()


class BlockMetrics(BaseModel, frozen=True, extra="forbid"):
    """
    コードブロックのメトリクスを表すデータクラス。

    このクラスは、特定のコードブロックの循環的複雑度や名前などのメトリクスを保持します。

    Attributes:
        complexity (int): コードブロックの循環的複雑度。
        name (str): コードブロックの名前。
        fullname (str): コードブロックの完全な名前。
        block_type (BlockType): コードブロックの種類（関数、メソッド、クラスなど）。
    """

    complexity: int
    name: str
    fullname: str
    block_type: BlockType


def get_maintainability_index(code: str) -> float:
    """
    指定されたコードの保守性指数を計算します。

    この関数は、提供されたコード文字列を解析し、保守性指数を計算します。
    保守性指数は、コードの保守のしやすさを示す指標です。

    Args:
        code (str): 分析するソースコードを含む文字列。

    Returns:
        float: 計算された保守性指数。
    """
    return mi_visit(code, True)


def get_complexity(code: str) -> int:
    """
    指定されたコードの複雑度を計算します。

    この関数は、提供されたコード文字列を解析し、循環的複雑度を計算します。
    循環的複雑度は、コードの理解や保守の難易度を示す指標です。

    Args:
        code (str): 分析するソースコードを含む文字列。

    Returns:
        int: 計算された複雑度。
    """
    return ComplexityVisitor.from_code(code).total_complexity


def _get_block_type(block) -> BlockType:
    """
    指定されたコードブロックの種類を取得します。

    この関数は、提供されたコードブロックを解析し、その種類を判定します。
    種類は、関数、メソッド、クラスなどが含まれます。

    Args:
        block: 分析するコードブロック。

    Returns:
        BlockType: コードブロックの種類を示すBlockTypeオブジェクト。
    """
    if isinstance(block, Function):
        if block.is_method:
            return BlockType.METHOD
        return BlockType.FUNCTION
    if isinstance(block, Class):
        return BlockType.CLASS
    return BlockType.UNKNOWN


def get_block_complexity(code: str) -> list[BlockMetrics]:
    """
    指定されたコードの各ブロックの複雑度を計算します。

    この関数は、提供されたコード文字列を解析し、各コードブロックの複雑度を計算します。
    各ブロックの複雑度は、BlockMetricsオブジェクトのリストとして返されます。

    Args:
        code (str): 分析するソースコードを含む文字列。

    Returns:
        list[BlockMetrics]: 各コードブロックの複雑度を示すBlockMetricsオブジェクトのリスト。
    """
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


def get_raw_metrics(code: str) -> RawMetrics:
    """
    指定されたコードの基本メトリクスを計算します。

    この関数は、提供されたコード文字列を解析し、基本メトリクスを計算します。
    基本メトリクスには、行数、コメント行数、空行数などが含まれます。

    Args:
        code (str): 分析するソースコードを含む文字列。

    Returns:
        RawMetrics: 計算された基本メトリクスを含むRawMetricsオブジェクト。
    """
    raw = analyze(code)
    return RawMetrics(
        lines_of_code=raw.loc,
        logical_lines_of_code=raw.lloc,
        source_lines_of_code=raw.sloc,
        comments=raw.comments,
        single_comments=raw.single_comments,
        multi=raw.multi,
        blank=raw.blank,
    )
