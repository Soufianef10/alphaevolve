import textwrap

from pwb_alphaevolve.evolution.patching import apply_patch


def sample_parent() -> str:
    return textwrap.dedent(
        """
        def fn():
            # === EVOLVE-BLOCK: decision_logic
            if True:
                return 1
            # === END EVOLVE-BLOCK
            return 0
        """
    )


def test_apply_patch_full_code():
    parent = sample_parent()
    patch = {"code": "print('hi')"}
    assert apply_patch(parent, patch) == "print('hi')"


def test_apply_patch_block_replacement():
    parent = sample_parent()
    patch = {"blocks": {"decision_logic": "if False:\n    return 2"}}
    result = apply_patch(parent, patch)
    assert "if False" in result
    assert "return 2" in result


def test_apply_patch_noop_missing_block():
    parent = sample_parent()
    patch = {"blocks": {"missing": "pass"}}
    assert apply_patch(parent, patch) == parent
