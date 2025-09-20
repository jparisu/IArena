import pytest
from dataclasses import dataclass

# Adjust the import below to your actual module path
from IArena.utils.YamlMixing import YamlMixing  # your class as provided (with the cls() fix)


# ---------- Example concrete dataclasses ----------

@dataclass(init=False)
class CommonConfig(YamlMixing):
    move_timeout_s: float = 5
    total_timeout_s: float = 10
    max_score: float = 1.0
    min_score: float = 0.0
    repetitions: int = 1


@dataclass(init=False)
class ExerciseConfig(YamlMixing):
    name: str = "sum_two_numbers"
    weight: float = 1.0
    hidden: bool = False


# Inherit from CommonConfig and extend it
@dataclass(init=False)
class AdvancedCommonConfig(CommonConfig):
    strict: bool = True
    seed: int = 42


# --------------------------- Tests ---------------------------

def test_update_applies_only_known_fields_and_ignores_unknown():
    cfg = CommonConfig()
    cfg.update({
        "move_timeout_s": 2.5,
        "max_score": 3.0,
        "unknown_key": 999,     # should be ignored
    })
    assert cfg.move_timeout_s == 2.5
    assert cfg.max_score == 3.0
    assert cfg.total_timeout_s == 10     # untouched default
    assert not hasattr(cfg, "unknown_key")


def test_from_yaml_builds_instance_with_filtered_keys():
    cfg = CommonConfig.from_yaml({
        "repetitions": 4,
        "total_timeout_s": 12,
        "garbage": "nope",
    })
    assert isinstance(cfg, CommonConfig)
    assert cfg.repetitions == 4
    assert cfg.total_timeout_s == 12
    assert cfg.move_timeout_s == 5   # default retained
    assert not hasattr(cfg, "garbage")


def test_init_accepts_yaml_mapping():
    cfg = CommonConfig({"min_score": -1.0, "max_score": 10.0})
    assert cfg.min_score == -1.0
    assert cfg.max_score == 10.0


def test_update_is_chainable():
    cfg = CommonConfig()
    returned = cfg.update({"repetitions": 2})
    assert returned is cfg
    assert cfg.repetitions == 2


def test_second_concrete_class_behaves_the_same():
    ex = ExerciseConfig.from_yaml({"name": "fib", "hidden": True, "noise": 1})
    assert ex.name == "fib"
    assert ex.hidden is True
    assert ex.weight == 1.0
    assert not hasattr(ex, "noise")


def test_inheritance_supports_parent_and_child_fields():
    cfg = AdvancedCommonConfig.from_yaml({
        "move_timeout_s": 1.5,
        "max_score": 5.0,
        "strict": False,
        "seed": 2024,
        "blah": "ignore me",
    })
    # parent fields
    assert cfg.move_timeout_s == 1.5
    assert cfg.max_score == 5.0
    # child fields
    assert cfg.strict is False
    assert cfg.seed == 2024
    # defaults carry over for untouched
    assert cfg.total_timeout_s == 10
    assert cfg.min_score == 0.0
    assert cfg.repetitions == 1
    assert not hasattr(cfg, "blah")


def test_update_on_inherited_class_modifies_both_parent_and_child_fields():
    cfg = AdvancedCommonConfig()
    cfg.update({"total_timeout_s": 30, "strict": False, "seed": 7})
    assert cfg.total_timeout_s == 30
    assert cfg.strict is False
    assert cfg.seed == 7
