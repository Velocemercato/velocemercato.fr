import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import prepare_public_site as p


def test_historique_allege(tmp_path):
    (tmp_path/'studio').mkdir()
    post = {'target': 'meta/facebook', 'id': '1', 'url': 'https://www.facebook.com/x'}
    data = {'updated_at': 'b', 'confirmed': [post], 'targets': {},
            'history': [{'updated_at': 'a', 'confirmed': [post] * 50, 'targets': {'t': {'posts': [post]}}}]}
    (tmp_path/'studio/editorial-status.json').write_text(json.dumps(data))
    p._alleger_editorial_status(tmp_path)
    out = json.loads((tmp_path/'studio/editorial-status.json').read_text())
    assert out['confirmed'] == [post]
    assert 'confirmed' not in out['history'][0]
    assert out['history'][0]['targets']['t']['posts'] == [post]


def test_fichier_trop_gros_retire(tmp_path, monkeypatch):
    monkeypatch.setattr(p, 'LIMITE_PAGES', 10)
    (tmp_path/'gros.bin').write_bytes(b'x' * 11)
    (tmp_path/'petit.txt').write_text('ok')
    p._retirer_fichiers_trop_gros(tmp_path)
    assert not (tmp_path/'gros.bin').exists() and (tmp_path/'petit.txt').exists()
