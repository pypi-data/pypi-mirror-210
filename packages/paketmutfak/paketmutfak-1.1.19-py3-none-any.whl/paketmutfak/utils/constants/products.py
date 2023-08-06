from dataclasses import dataclass


@dataclass
class PlatformProductFormat:
    id: str
    name: str
    platform_id: str
    description: str
    title: str
    price: str
    pm_restaurant_id: str
    options: list
    status: bool


@dataclass
class PlatformProductOptionFormat:
    id: str
    type: str
    name: str
    description: str
    price: str
    title: str


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
