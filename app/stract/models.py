from dataclasses import dataclass


@dataclass
class Platform:
    text: str
    value: str


@dataclass
class Field:
    text: str
    value: str


@dataclass
class Account:
    id: str
    name: str
    token: str
