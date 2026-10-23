"""Budget éditorial court : réécriture entière, jamais de phrase tronquée."""
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import update_emission as E
from tools import diffuser_jt as D
from tools import assembler_jt as A


def response(words_per_line):
    data={'titre':'Contrôle de format, aucune publication','accroche':'Essai',
          'repliques':[{'perso':'PRESENTATEUR','texte':' '.join(['mot']*words_per_line)} for _ in range(14)]}
    return {'content':[{'type':'text','text':json.dumps(data)}]}


class ExpressTests(unittest.TestCase):
    def test_oversized_script_is_rewritten_as_complete_lines_before_rendering(self):
        with patch.object(E.robot,'call_claude',side_effect=[response(45),response(30)]) as writer:
            script=E.write_script('foot','edition','midi',[])
        self.assertEqual(sum(len(text.split()) for _,text in script['repliques']),420)
        self.assertEqual(writer.call_count,2)
        self.assertIn('Recompose un journal complet',writer.call_args.args[1])
        self.assertEqual(len(script['repliques']),14)

    def test_still_oversized_script_is_refused_after_one_rewrite(self):
        with patch.object(E.robot,'call_claude',return_value=response(45)) as writer:
            with self.assertRaisesRegex(RuntimeError,'encore trop long'):
                E.write_script('actus','edition','matin',[])
        self.assertEqual(writer.call_count,2)

    def test_short_format_does_not_silently_cut_a_long_render(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);now=dt.datetime.now(dt.timezone.utc)
            date=now.astimezone(E.D.PARIS).date().isoformat()
            (root/'_autorisation.json').write_text(json.dumps({'publish':True,'created':now.isoformat(),
                'date':date,'moment':'midi','run_id':'42'}))
            with patch.object(D,'assemble',return_value={'duree_mesuree':841,'editorial_revision':'court-v1'}),patch.object(D,'probe') as probe:
                with self.assertRaisesRegex(D.DeliveryError,'supérieur à 14 minutes'):
                    D.prepare(root,root/'out.mp4',now=now,expected_run='42')
            probe.assert_not_called()

    def test_old_and_short_editions_are_not_mixed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for universe in ['foot','actus','gaming']:
                file=root/(universe+'-test.mp4');file.write_bytes(b'fixture-test')
                data={'id':universe+'-test','univers':universe,'format':'edition','moment':'midi',
                      'date':'2026-10-23T13:00:00+02:00','fichier':file.name,'titre':universe}
                if universe=='foot':data['editorial_revision']='court-v1'
                (root/(universe+'.json')).write_text(json.dumps(data))
            info={'format':{'duration':'2'},'streams':[
                {'codec_type':'video','codec_name':'h264','width':1280,'height':720,'pix_fmt':'yuv420p','avg_frame_rate':'24/1'},
                {'codec_type':'audio','codec_name':'aac','sample_rate':'48000','channels':1}]}
            with patch.object(A,'probe',return_value=info),patch.object(A.subprocess,'run') as render:
                with self.assertRaisesRegex(RuntimeError,'éditoriales incompatibles'):
                    A.assemble(root,'midi','2026-10-23',root/'out.mp4',root,require_hd=True)
            render.assert_not_called()
