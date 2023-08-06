from __future__ import annotations

from typing import TYPE_CHECKING

from .mixins import Hashable

if TYPE_CHECKING:
    from .types.backpack import Backpack as BackPackPayload

__all__ = ('Backpack',)


class Backpack(Hashable):

    __slots__ = (
        'id',
        'name',
        'blocks_armor_vest',
        'speed_penalty_percent',
        'cell_height',
        'cell_width',
        'weight',
        'banned_on_flea',
        'discard_limit',
        'max_stack_size',
    )

    def __init__(self, payload: BackPackPayload) -> None:
        self.name: str = payload['Name']
        self.id: str = payload['Item ID']
        self.blocks_armor_vest: bool = 'true' == payload['Blocks Armored Vest']

        self._update(payload)

    @property
    def image_url(self):
        return f'https://tarkov-changes.com/img/items/128/{self.id}.png'

    def _update(self, data: BackPackPayload) -> None:
        self.speed_penalty_percent: int = int(data['Speed Penalty (%)'])
        self.cell_height: int = int(data['Cell Height'])
        self.cell_width: int = int(data['Cell Width'])

        self.weight: float = float(data['Item Weight'])
        self.banned_on_flea: bool = data['Can be sold on flea market'] == 'false'
        self.discard_limit: int = int(data['Discard Limit'])
        self.max_stack_size: int = int(data['Max Stack Size'])
