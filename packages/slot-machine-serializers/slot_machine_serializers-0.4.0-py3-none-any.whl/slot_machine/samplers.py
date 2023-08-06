"""Sampler classes."""

from __future__ import annotations

__all__ = [
    "Sampler",
    # Sampler types
    "ScalarSampler",
    "MappingSampler",
    "SequenceSampler",
    # Scalar Samplers
    "SampleUniform",
    "SampleRange",
    # Sequence Samplers
    "Choose",
    "ChooseInteger",
    "ChooseFloat",
    # Mapping Samplers
    "SampleNormal",
]

from abc import ABC, abstractclassmethod

import random
import yaml

from typing_extensions import Self

from .serializers import SlotsLoader


class Sampler(ABC):
    """Base class for samplers."""

    def __init_subclass__(cls) -> None:
        SlotsLoader.add_constructor(f"!{cls.__name__}", cls._construct_yaml)

    @abstractclassmethod
    def _construct_yaml(cls, loader: yaml.Loader, node: yaml.nodes.Node) -> Self:
        """Construct the sampler from YAML."""
        pass

    @abstractclassmethod
    def get_sample(cls, **kwargs):
        """Get the sample."""
        pass


class ScalarSampler(Sampler):
    """Define scalar sampler."""

    @classmethod
    def _construct_yaml(cls, loader: yaml.Loader, node: yaml.nodes.Node) -> Self:
        value = loader.construct_scalar(node)
        return cls.get_sample(value=value)


class MappingSampler(Sampler):
    """Define mapping sampler."""

    @classmethod
    def _construct_yaml(cls, loader: yaml.Loader, node: yaml.nodes.Node) -> Self:
        mapping = loader.construct_mapping(node)
        return cls.get_sample(**mapping)


class SequenceSampler(Sampler):
    """Define list sampler."""

    @classmethod
    def _construct_yaml(cls, loader: yaml.Loader, node: yaml.nodes.Node) -> Self:
        sequence = loader.construct_sequence(node)
        return cls.get_sample(sequence)


class SampleUniform(ScalarSampler):
    """Sample from uniform distribution."""

    @classmethod
    def get_sample(cls, value: str) -> float:
        """Get the sample."""
        return random.uniform(*map(float, value.split("..")))


class SampleRange(ScalarSampler):
    """Sample from range distribution."""

    @classmethod
    def get_sample(cls, value: str) -> int:
        """Get the sample."""
        split = value.split("..")

        if not 1 < len(split) <= 3:
            raise ValueError(f"Invalid range: {value}")

        return random.randrange(*map(int, split))


class Choose(SequenceSampler):
    """Sample from choices."""

    @classmethod
    def get_sample(cls, values: list) -> int:
        """Get the sample."""
        return random.choice(values)


class ChooseInteger(SequenceSampler):
    """Sample from integer choices."""

    @classmethod
    def get_sample(cls, values: list) -> int:
        """Get the sample."""
        return random.choice(list(map(int, values)))


class ChooseFloat(SequenceSampler):
    """Sample from float choices."""

    @classmethod
    def get_sample(cls, values: list) -> float:
        """Get the sample."""
        return random.choice(list(map(float, values)))


class SampleNormal(MappingSampler):
    """Sample from normal distribution."""

    @classmethod
    def get_sample(cls, **kwargs) -> float:
        """Get the sample."""
        return random.normalvariate(**kwargs)
