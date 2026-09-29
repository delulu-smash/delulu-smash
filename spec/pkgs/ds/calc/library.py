from pydantic import BaseModel


class Damage(BaseModel):
    freshness_bonus: float
    damage: float
    target_damage: float
    attack_hitlag: int
    target_hitlag: int

class Knockback(BaseModel):
    total_kb: float
    launch_angle: float
    hitstun: int
    faf: int
    hit_advantage: int
    is_tumble: bool
    can_jab_lock: bool

class HitData(BaseModel):
    damage: Damage
    knockback: Knockback


# ds/calc/core
from ds.calc.model import HitData

def get_hit_data(attacker:str, target:str, attack:str, hitbox: int| None = None,damage: float| None = None, hitlag: float | None = None) -> HitData:
    """
    gives the hit data from given attack hitting target

    If `attack`= 'custom', allow to specify additional parameters like `damage`, `hitlag`,...
    Otherwise, will fetch relevant data for that attack (eg damage, hitlag, etc...)
    if `attack` != 'custom', must specify `hitbox`

    Parameters
    ----------
    attacker : str
        character performing the attack (must match data-> char.parquet's id)
    target : str
        character being hit by the attack (must match data-> char.parquet's id)
    attack : str
        name of the attack (eg 'jab', 'ftilt')
    hitbox : int | None, optional
        hitbox index of the attack, required if attack != 'custom'
    damage : float | None, optional
        damage of the attack, by default None
    hitlag : float | None, optional
        hitlag of the attack, by default None

    Returns
    -------
    HitData
        hit data of the attack
    """.