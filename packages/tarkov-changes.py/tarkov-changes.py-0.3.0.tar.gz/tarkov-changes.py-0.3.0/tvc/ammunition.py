from __future__ import annotations

from typing import TYPE_CHECKING

from .mixins import Hashable

if TYPE_CHECKING:
    from .types.ammunition import Ammunition as AmmunitionPayload

__all__ = ('Ammunition',)


class Ammunition(Hashable):

    __slots__ = (
        'id',
        'name',
        'caliber',
        'flesh_damage',
        'penetration_power',
        'armor_damage',
        'accuracy',
        'recoil',
        'frag_chance',
        'durability_burn',
        'stamina_burn_per_damage',
        'projectile_speed',
        'misfire_chance',
        'penetration_chance',
        'heavy_bleeding_delta',
        'light_bleeding_delta',
        'ballistic_coefficient',
        'cell_height',
        'cell_width',
        'weight',
        'max_stack_size',
        'discard_limit',
    )

    def __init__(self, payload: AmmunitionPayload) -> None:
        self.name: str = payload['Name']
        self.id: str = payload['Item ID']
        self.caliber: str = payload['Caliber']

        self._update(payload)

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.flesh_damage

    def __repr__(self) -> str:
        attrs = (
            ('id', self.id),
            ('name', self.name),
            ('flesh_damage', self.flesh_damage),
            ('caliber', self.caliber),
        )

        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def image_url(self):
        return f'https://tarkov-changes.com/img/items/128/{self.id}.png'

    def _update(self, data: AmmunitionPayload):
        self.flesh_damage: int = int(data['Flesh Damage'])
        self.penetration_power: int = int(data['Penetration Power'])
        self.armor_damage: int = int(data['Armor Damage'])
        self.accuracy: int = int(data['Accuracy'])
        self.recoil: int = int(data['Recoil'])
        self.frag_chance: float = float(data['Frag Chance'])
        self.durability_burn: float = float(data['Durability Burn'])
        self.stamina_burn_per_damage: float = float(data['Stamina Burn per Dmg'])
        self.projectile_speed: int = int(data['Projectile Speed'])
        self.misfire_chance: float = float(data['Misfire Chance'])
        self.penetration_chance: float = float(data['Penetration Chance'])
        self.heavy_bleeding_delta: float = float(data['Heavy Bleeding Delta'])
        self.light_bleeding_delta: float = float(data['Light Bleeding Delta'])
        self.ballistic_coefficient: float = float(data['Ballistic Coefficient'])
        self.cell_height: int = int(data['Cell Height'])
        self.cell_width: int = int(data['Cell Width'])
        self.weight: float = float(data['Item Weight'])
        self.max_stack_size: int = int(data['Max Stack Size'])
        self.discard_limit: int = int(data['Discard Limit'])
