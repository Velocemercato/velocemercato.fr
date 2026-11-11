import datetime as dt
import unittest
from tools import teasers_vm as mod


class Tests(unittest.TestCase):
    def setUp(self):
        self.now=dt.datetime(2026,11,11,8,tzinfo=mod.PARIS)
        self.row={'id':'une-info','titre':'Une annonce de jeu vidéo','resume':'Une brève originale.',
                  'publishedAt':self.now.isoformat(),'sources':[{'nom':'Source','url':'https://example.com/info'}]}
    def test_reject_old_future_unsourced_and_repeated(self):
        self.assertIsNotNone(mod.choose([self.row],'gaming',[],self.now))
        self.assertIsNone(mod.choose([self.row],'gaming',[{'univers':'gaming','article_id':'une-info'}],self.now))
        for delta in (-30,1):
            row={**self.row,'publishedAt':(self.now+dt.timedelta(hours=delta)).isoformat()}
            self.assertIsNone(mod.choose([row],'gaming',[],self.now))
        self.assertIsNone(mod.choose([{**self.row,'sources':[]}],'gaming',[],self.now))
    def test_manga_only_is_not_a_gaming_teaser(self):
        row={**self.row,'titre':'One Piece : nouveau chapitre du manga'}
        self.assertIsNone(mod.choose([row],'gaming',[],self.now))
    def test_upcoming_blocks_paris_and_next_day(self):
        self.assertEqual(mod.upcoming(self.now).hour,9)
        self.assertEqual(mod.upcoming(self.now.replace(hour=10)).hour,12)
        self.assertEqual(mod.upcoming(self.now.replace(hour=18)).hour,20)
        tomorrow=mod.upcoming(self.now.replace(hour=22))
        self.assertEqual(tomorrow.hour,9)
        self.assertEqual(tomorrow.day,12)


if __name__=='__main__':unittest.main()
