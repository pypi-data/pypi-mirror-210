from dataclasses import dataclass
from typing import Union

from paketmutfak.utils.functions.general import generate_uid


@dataclass
class PlatformOption:
    name: str
    platform_product_id: str
    platform_option_id: str
    price: str
    type: str
    pm_restaurant_id: str
    platform_name: str
    id: str = generate_uid()


@dataclass
class PlatformProduct:
    id: str
    platform_product_id: str
    name: str
    description: str
    price: str
    title: str
    pm_restaurant_id: str
    status: bool
    platform_name: str
    preparation_time: Union[str, None] = None


@dataclass
class PMProduct:
    id: str
    name: str
    note: str
    price: float
    hash_id: str
    options: list['PMProduct']
    quantity: float
    unit_price: float
    extra_ingredients: list['PMProductExtraIngredients']
    removed_ingredients: list


@dataclass
class PMProductExtraIngredients:
    id: str
    name: str
    price: float


@dataclass
class PMProductRemovedIngredients:
    id: str
    name: str
