from core.updater import _parse_version, _pick_setup_asset, _sha256_from_digest


def test_parse_version():
    assert _parse_version("v2.1.0") == (2, 1, 0)
    assert _parse_version("2.0.1") > _parse_version("v2.0.0")
    assert _parse_version("v2.1.0-beta") == (0,)


def test_pick_setup_asset_prefers_setup():
    assets = [
        {"name": "DeepCalculator.exe"},
        {"name": "notes.txt"},
        {"name": "DeepCalculator_Setup.exe"},
    ]
    assert _pick_setup_asset(assets)["name"] == "DeepCalculator_Setup.exe"


def test_pick_setup_asset_fallbacks():
    assert _pick_setup_asset([{"name": "app.EXE"}])["name"] == "app.EXE"
    assert _pick_setup_asset([{"name": "app.zip"}]) is None
    assert _pick_setup_asset([]) is None


def test_sha256_from_digest():
    assert _sha256_from_digest("sha256:ABCDEF") == "abcdef"
    assert _sha256_from_digest("md5:abc") == ""
    assert _sha256_from_digest("") == ""
