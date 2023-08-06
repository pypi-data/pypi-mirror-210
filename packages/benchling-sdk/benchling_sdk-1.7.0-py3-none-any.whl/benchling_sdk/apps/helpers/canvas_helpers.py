from __future__ import annotations

from typing import cast, Dict, Generic, List, Optional, Type, TypeVar, Union

from benchling_api_client.v2.beta.models.button_ui_block import ButtonUiBlock
from benchling_api_client.v2.beta.models.canvas import Canvas
from benchling_api_client.v2.beta.models.canvas_create import CanvasCreate
from benchling_api_client.v2.beta.models.canvas_update import CanvasUpdate
from benchling_api_client.v2.beta.models.chip_ui_block import ChipUiBlock
from benchling_api_client.v2.beta.models.dropdown_ui_block import DropdownUiBlock
from benchling_api_client.v2.beta.models.markdown_ui_block import MarkdownUiBlock
from benchling_api_client.v2.beta.models.search_input_ui_block import SearchInputUiBlock
from benchling_api_client.v2.beta.models.section_ui_block import SectionUiBlock
from benchling_api_client.v2.beta.models.selector_input_ui_block import SelectorInputUiBlock
from benchling_api_client.v2.beta.models.text_input_ui_block import TextInputUiBlock
from benchling_api_client.v2.extensions import UnknownType
from typing_extensions import Protocol

from benchling_sdk.helpers.logging_helpers import log_stability_warning, StabilityLevel

log_stability_warning(StabilityLevel.ALPHA)

S = TypeVar("S", bound="_FilteredCanvasBuilderBlockStream")

_UiBlock = Union[
    ButtonUiBlock,
    ChipUiBlock,
    DropdownUiBlock,
    MarkdownUiBlock,
    SearchInputUiBlock,
    SectionUiBlock,
    SelectorInputUiBlock,
    TextInputUiBlock,
    UnknownType,
]

_UiBlockType = TypeVar(
    "_UiBlockType",
    bound=_UiBlock,
)


class DuplicateBlockIdError(Exception):
    """Error indicating that duplicate ids were present on blocks within a Canvas."""

    pass


class NoMatchingBlocksError(Exception):
    """
    Error indicating that blocks were expected, but none matched.

    Used to prevent requiring developers to handle Optional[_UiBlock] for type safety.
    """

    pass


class _CanvasBuilderUiBlock(Generic[_UiBlockType]):
    """Internal UI block wrapper for CanvasBuilder."""

    _block: _UiBlockType
    _builder: CanvasBuilder

    def __init__(self, block: _UiBlockType, builder: CanvasBuilder):
        self._block = block
        self._builder = builder

    @classmethod
    def from_api_model(
        cls, block: _UiBlockType, builder: CanvasBuilder
    ) -> _CanvasBuilderUiBlock[_UiBlockType]:
        """Create a _CanvasBuilderUiBlock from an underlying API model."""
        return cls(block, builder)

    def to_api_model(self) -> _UiBlockType:
        """Convert to the underlying API model."""
        return self._block

    def children(self) -> _CanvasBuilderBlockStream:
        """
        Return children for blocks when applicable, such as for section blocks.

        If not applicable, returns an empty canvas block stream with no blocks.
        """
        model = self.to_api_model()
        if isinstance(model, SectionUiBlock):
            # MyPy can't recognize the type narrowing when we check .children below
            section_block = cast(SectionUiBlock, model)
            child_blocks = [
                _CanvasBuilderUiBlock.from_api_model(block, self._builder) for block in section_block.children
            ]
            # Pass reference to parent block (self)
            return _CanvasBuilderBlockStream(self._builder, child_blocks, child_blocks, self)
        return _CanvasBuilderBlockStream(self._builder, [], [])

    def replace(self, new_blocks: List[_UiBlock]) -> None:
        """Replace block with provided new_blocks."""
        parent = self._parent_block()
        model = cast(_UiBlock, self.to_api_model())
        if parent:
            self.insert_after(new_blocks)
            # Keeps MyPy happy; SectionUiBlock is not valid for .children of SectionUiBlock
            assert not isinstance(model, SectionUiBlock)
            parent.children.remove(model)
        else:
            self.insert_after(new_blocks)
            # noinspection PyProtectedMember
            self._builder._source_canvas.blocks.remove(model)

    def remove(self) -> None:
        """Remove block."""
        parent = self._parent_block()
        model = cast(_UiBlock, self.to_api_model())
        if parent:
            # Keeps MyPy happy; SectionUiBlock is not valid for .children of SectionUiBlock
            assert not isinstance(model, SectionUiBlock)
            parent.children.remove(model)
        else:
            # noinspection PyProtectedMember
            self._builder._source_canvas.blocks.remove(model)

    def insert_after(self, new_blocks: List[_UiBlock]) -> None:
        """Insert new_blocks after block."""
        self._nested_insert(new_blocks, 1)

    def insert_before(self, new_blocks: List[_UiBlock]) -> None:
        """Insert new_blocks before block."""
        self._nested_insert(new_blocks, 0)

    def _nested_insert(self, new_blocks: List[_UiBlock], offset: int) -> None:
        """
        Nested insert.

        This is used to handle the case that an insert is being performed and it's contextual within
        another block.

        For instance, the children of a SectionUiBlock.
        """
        parent_block = self._parent_block()
        if parent_block:
            child_blocks = parent_block.children
            # Using list() to solve "List" is invariant creates a copy which means this stops working
            self._insert(new_blocks, offset, child_blocks, self.to_api_model())  # type: ignore
            parent_block.children = child_blocks
            parent_builder_block = _CanvasBuilderUiBlock.from_api_model(parent_block, self._builder)
            parent_builder_block.insert_after([parent_block])
            # noinspection PyProtectedMember
            self._builder._source_canvas.blocks.remove(parent_builder_block.to_api_model())
        else:
            # noinspection PyProtectedMember
            self._insert(new_blocks, offset, self._builder._source_canvas.blocks, self.to_api_model())

    @staticmethod
    def _insert(
        new_blocks: List[_UiBlock], offset: int, blocks: List[_UiBlock], target_block: _UiBlock
    ) -> None:
        """Insert new_blocks before block as a side effect."""
        index = blocks.index(target_block)
        for count, new_block in enumerate(new_blocks):
            blocks.insert(index + count + offset, new_block)

    def _parent_block(self) -> Optional[SectionUiBlock]:
        # noinspection PyProtectedMember
        for parent_block in self._builder._source_canvas.blocks:
            if isinstance(parent_block, SectionUiBlock):
                if self.to_api_model() in parent_block.children:
                    return parent_block
        return None


class _CanvasBuilderFilter(Protocol):
    def __call__(self, block: _UiBlockType) -> bool:
        """Return True if the UiBlock matches specified conditions."""
        pass


class _FilteredCanvasBuilderBlockStream:
    """Internal Filtered UI block list wrapper for CanvasBuilder."""

    _builder: CanvasBuilder
    _blocks: List[_CanvasBuilderUiBlock]
    _selected_blocks: List[_CanvasBuilderUiBlock]
    _cursor: int

    def __init__(
        self,
        builder: CanvasBuilder,
        blocks: List[_CanvasBuilderUiBlock],
        selected_blocks: List[_CanvasBuilderUiBlock],
    ):
        self._builder = builder
        self._blocks = blocks
        self._selected_blocks = selected_blocks

    def __iter__(self):
        self._cursor = 0
        return self

    def __next__(self):
        if self._cursor >= len(self._blocks):
            raise StopIteration
        block = self._blocks[self._cursor]
        self._cursor += 1
        return block

    @classmethod
    def from_builder(cls: Type[S], builder: CanvasBuilder) -> S:
        """
        From Builder.

        Instantiate a new _FilteredCanvasBuilderBlockStream from a CanvasBuilder.
        """
        # noinspection PyProtectedMember
        blocks = [
            _CanvasBuilderUiBlock.from_api_model(block, builder)
            for block in builder._source_canvas.blocks
            if not isinstance(block, UnknownType)
        ]
        return cls(builder, blocks, blocks)

    def filter(self, filter_function: _CanvasBuilderFilter) -> _FilteredCanvasBuilderBlockStream:
        """
        Filter.

        Accept a predicate that evaluates if a UiBlock should be included in the result or not.
        Returns a new stream of blocks filtered to the predicate, which is further operable.
        """
        return _CanvasBuilderBlockStream(
            self._builder,
            self._blocks,
            [block for block in self._selected_blocks if filter_function(block.to_api_model())],
        )

    def get_by_id(self, block_id: str) -> _CanvasBuilderUiBlock:
        """
        Get a block by its id.

        Raises NoMatchingBlocksError if the block is not found. To match an id as an optional, use filter().
        """
        matched_block = self._block_by_id(block_id, self._blocks)
        if not matched_block:
            raise NoMatchingBlocksError(f'Could not find a block with id "{block_id}"')
        return matched_block

    def _block_by_id(
        self, block_id: str, blocks: List[_CanvasBuilderUiBlock]
    ) -> Optional[_CanvasBuilderUiBlock]:
        for block in blocks:
            api_block = block.to_api_model()
            if api_block.id == block_id:
                return block
            children = block.children()
            if children.count() > 0:
                child_block = self._block_by_id(block_id, list(children))
                if child_block:
                    return child_block
        return None

    def count(self) -> int:
        """Return a count of the elements in the list of blocks."""
        return len(self._selected_blocks)

    def first(self) -> _CanvasBuilderUiBlock:
        """Return the first block in the list."""
        if len(self._selected_blocks) < 1:
            raise NoMatchingBlocksError
        return self._selected_blocks[0]

    def last(self) -> _CanvasBuilderUiBlock:
        """Return the last block in the list."""
        if len(self._selected_blocks) < 1:
            raise NoMatchingBlocksError
        return self._selected_blocks[-1]

    def remove(self) -> None:
        """Remove blocks."""
        updated_blocks = [
            block.to_api_model() for block in self._blocks if block not in self._selected_blocks
        ]
        # noinspection PyProtectedMember
        self._builder._source_canvas.blocks = updated_blocks


class _CanvasBuilderBlockStream(_FilteredCanvasBuilderBlockStream):
    """
    Internal UI block list wrapper for CanvasBuilder.

    Possesses some additional operations unavailable to filtered block streams.
    """

    _parent: Optional[_CanvasBuilderUiBlock]

    def __init__(
        self,
        builder: CanvasBuilder,
        blocks: List[_CanvasBuilderUiBlock],
        selected_blocks: List[_CanvasBuilderUiBlock],
        parent: Optional[_CanvasBuilderUiBlock] = None,
    ):
        super().__init__(builder, blocks, selected_blocks)
        self._parent = parent

    def append(self, new_blocks: List[_UiBlock]) -> None:
        """
        Append new_blocks to the end of list of blocks.

        Only operates on unfiltered block streams. This can be a list of blocks on a Canvas, or children on a
        block such as SectionUiBlock.
        """
        if self._parent:
            if self.count() > 0:
                self.last().insert_after(new_blocks)
            else:
                self._parent.to_api_model().children.extend(new_blocks)
        else:
            # noinspection PyProtectedMember
            self._builder._source_canvas.blocks.extend(new_blocks)


class CanvasBuilder:
    """
    Canvas Builder.

    This class provides methods to help developers effectively work with Canvas UI Blocks.
    Working with the underlying API models directly can be clunky, as there is no native way to easily find
    blocks based on their attributes, and then operate on them. Some blocks, like SectionUiBlock, have nested
    children blocks, further complicating the unassisted experience.

    The goal of CanvasBuilder is to accept an existing Canvas, and easily change its contents (blocks), then
    send a resulting CanvasCreate or CanvasUpdate model to the API.

    Some block operations include:
        - Get by Id
        - Filtering by predicate
        - Remove
        - Replace
        - Insert After
        - Insert Before
        - Append

    Sample usage:
        ```
        canvas: Canvas = benchling.v2.beta.apps.get_canvas_by_id("canvas_id")
        builder = CanvasBuilder.from_canvas(canvas).blocks
            .filter(lambda block: isinstance(block, TextInputUiBlock))
            .remove()
        updated_canvas = benchling.v2.beta.apps.update_canvas("canvas_id", builder.to_update())
        ```
    """

    _source_canvas: Canvas

    def __init__(
        self,
        app_id: str,
        feature_id: str,
        resource_id: str,
        enabled: bool = True,
        session_id: Optional[str] = None,
        blocks: Optional[List[_UiBlock]] = None,
    ):
        """
        Init Canvas.

        Create a CanvasBuilder from scratch. Useful when a source Canvas is not already created.
        """
        self._source_canvas = Canvas(
            app_id=app_id,
            feature_id=feature_id,
            resource_id=resource_id,
            enabled=enabled,
            session_id=session_id,
            blocks=blocks if blocks else [],
        )

    @classmethod
    def from_canvas(cls, canvas: Canvas) -> CanvasBuilder:
        """
        From Canvas.

        Create a CanvasBuilder from an existing canvas. Preferred when a canvas already exists.
        """
        return cls(
            app_id=canvas.app_id,
            feature_id=canvas.feature_id,
            resource_id=canvas.resource_id,
            enabled=canvas.enabled,
            session_id=canvas.session_id,
            blocks=canvas.blocks,
        )

    def _set_enabled(self, value: bool) -> CanvasBuilder:
        return CanvasBuilder(
            app_id=self._source_canvas.app_id,
            feature_id=self._source_canvas.feature_id,
            resource_id=self._source_canvas.resource_id,
            enabled=value,
            session_id=self._source_canvas.session_id,
            blocks=self._source_canvas.blocks,
        )

    def disable(self) -> CanvasBuilder:
        """Set the canvas to disabled."""
        return self._set_enabled(False)

    def enable(self) -> CanvasBuilder:
        """Set the canvas to enabled."""
        return self._set_enabled(True)

    def inputs_to_dict(self) -> Dict[str, str]:
        """
        Read Inputs to dict.

        Return a dictionary of {block_id: block_value} for all blocks on the canvas with input values.
        Blocks that only have read attributes are omitted.

        Raise DuplicateBlockIdError if multiple blocks with the same id are found.
        """
        return self._values_from_blocks(self._source_canvas.blocks)

    def _values_from_blocks(
        self, blocks: List[_UiBlock], existing_keys: Optional[List[str]] = None
    ) -> Dict[str, str]:
        existing_keys = existing_keys if existing_keys else []
        values: Dict[str, str] = dict()
        for block in blocks:
            if not isinstance(block, UnknownType):
                if hasattr(block, "value"):
                    if block.id in existing_keys:
                        raise DuplicateBlockIdError(
                            f'More than one block with the id "{block.id}" already exists'
                        )
                    existing_keys.append(block.id)
                    # Ignore type error since we checked hasattr above
                    values[block.id] = block.value  # type: ignore
                elif isinstance(block, SectionUiBlock):
                    # Cast to appease MyPy
                    parent_block = cast(SectionUiBlock, block)
                    # list() prevents MyPy from complaining: "List" is invariant
                    child_values = self._values_from_blocks(list(parent_block.children), existing_keys)
                    values.update(child_values)
        return values

    def to_update(self) -> CanvasUpdate:
        """Return a CanvasUpdate API model from the current state of the canvas managed by CanvasBuilder."""
        return CanvasUpdate(
            feature_id=self._source_canvas.feature_id,
            resource_id=self._source_canvas.resource_id,
            enabled=self._source_canvas.enabled,
            session_id=self._source_canvas.session_id,
            blocks=self._source_canvas.blocks,
        )

    def to_create(self) -> CanvasCreate:
        """Return a CanvasCreate API model from the current state of the canvas managed by CanvasBuilder."""
        return CanvasCreate(
            app_id=self._source_canvas.app_id,
            feature_id=self._source_canvas.feature_id,
            resource_id=self._source_canvas.resource_id,
            enabled=self._source_canvas.enabled,
            session_id=self._source_canvas.session_id,
            blocks=self._source_canvas.blocks,
        )

    @property
    def blocks(self) -> _CanvasBuilderBlockStream:
        """
        Blocks.

        Return a stream of blocks which can be iterated and operated on to mutate the canvas
        stored by the builder.
        """
        return _CanvasBuilderBlockStream.from_builder(self)
