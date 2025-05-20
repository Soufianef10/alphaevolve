import pytest
from pwb_alphaevolve.evolution.patching import apply_patch


PARENT_CODE = (
    "class Strategy:\n"
    "    def __init__(self):\n"
    "        pass\n"
    "\n"
    "    # === EVOLVE-BLOCK: decision_logic =================================\n"
    "    def decide(self):\n"
    "        return 1\n"
    "    # === END EVOLVE-BLOCK =============================================\n"
)


def test_apply_patch_full_replacement():
    new_code = "def foo():\n    return 42\n"
    patched = apply_patch(PARENT_CODE, {"code": new_code})
    assert patched == new_code


def test_apply_patch_block_replacement():
    diff = {"blocks": {"decision_logic": "def decide(self):\n    return 2"}}
    patched = apply_patch(PARENT_CODE, diff)
    expected = (
        "class Strategy:\n"
        "    def __init__(self):\n"
        "        pass\n"
        "\n"
        "    # === EVOLVE-BLOCK: decision_logic =================================\n"
        "    def decide(self):\n"
        "        return 2\n"
        "    # === END EVOLVE-BLOCK =============================================\n"
    )
    assert patched == expected


def test_apply_patch_unknown_block_noop():
    diff = {"blocks": {"nonexistent": "def x(): pass"}}
    patched = apply_patch(PARENT_CODE, diff)
    assert patched == PARENT_CODE
