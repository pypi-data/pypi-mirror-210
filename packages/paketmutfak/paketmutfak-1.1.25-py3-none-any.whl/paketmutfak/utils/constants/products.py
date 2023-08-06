from dataclasses import dataclass
from typing import Union, List


@dataclass
class PlatformOption:
    name: str
    platform_product_id: str
    platform_option_id: str
    price: str
    type: str
    pm_restaurant_id: str
    platform_name: str
    id: str


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
class PMProductExtraIngredients:
    id: str
    name: str
    price: float


@dataclass
class PMProductRemovedIngredients:
    id: str
    name: str


@dataclass
class PMOption:
    option_id: str
    product_id: str
    category_name: str
    name: str
    quantity: int
    price: float
    options: List['PMOption']


@dataclass
class PMProduct:
    id: str
    name: str
    note: str
    price: float
    hash_id: str
    options: List[PMOption]
    quantity: int
    unit_price: float
    extra_ingredients: List[PMProductExtraIngredients]
    removed_ingredients: List[PMProductRemovedIngredients]



