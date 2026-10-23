import datetime as dt
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pastille_media as media
import pastille_schedule as schedule
import pastille_pages as pages
import update_debat as debate
import update_emission as emission
from tools.assembler_jt import assemble


class PastilleTests(unittest.TestCase):
    def test_paris_schedule_winter_summer_and_clock_change(self):
        for date in ['2026-01-15','2026-07-15','2026-03-29','2026-10-25']:
            for hour, plan in [(8,'matin'),(12,'midi'),(20,'soir')]:
                now = dt.datetime.fromisoformat(f'{date}T{hour:02}:00').replace(tzinfo=schedule.PARIS)
                self.assertEqual(schedule.slot(now.astimezone(dt.timezone.utc),schedule.JT_CRON),plan)
        for hour in [6,7,9,11,13,19,21]:
            now=dt.datetime(2026,7,15,hour,tzinfo=schedule.PARIS)
            self.assertEqual(schedule.slot(now,schedule.JT_CRON),'')
        for date in ['2026-07-19','2026-11-01']:  # dimanches été / hiver
            sunday=dt.datetime.fromisoformat(f'{date}T18:00').replace(tzinfo=schedule.PARIS)
            self.assertEqual(schedule.slot(sunday.astimezone(dt.timezone.utc),schedule.BUTS_CRON),'buts')
            self.assertEqual(schedule.slot((sunday-dt.timedelta(days=1)).astimezone(dt.timezone.utc),schedule.BUTS_CRON),'')
            for hour in (22,23):
                late=dt.datetime.fromisoformat(f'{date}T{hour}:45').replace(tzinfo=schedule.PARIS)
                self.assertEqual(schedule.slot(late.astimezone(dt.timezone.utc),schedule.DEBATE_CRON),'debat')
        for moment in ['matin','midi','soir']:
            self.assertEqual({universe for universe,_,_ in emission.PLANS[moment]}, {'foot','actus','gaming'})

    def test_matches_must_be_fresh_confirmed_and_on_the_right_day(self):
        now=dt.datetime(2026,10,22,17,tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'scores.json'
            rows=[{'id':1,'date':'2026-10-22T18:00:00Z','statut':'TIMED'},
                  {'id':2,'date':'2026-10-22T18:00:00Z','statut':'POSTPONED'},
                  {'id':3,'date':'2026-10-21T16:00:00Z','statut':'FINISHED'},
                  {'id':4,'date':'2026-10-22T12:00:00Z','statut':'FINISHED'}]
            path.write_text(json.dumps({'maj':now.isoformat(),'matchs':rows}))
            self.assertEqual([row['id'] for row in schedule.confirmed_matches(folder,now)],[1])
            self.assertEqual([row['id'] for row in schedule.confirmed_matches(folder,now,finished=True)],[4])
            path.write_text(json.dumps({'maj':(now-dt.timedelta(hours=3)).isoformat(),'matchs':rows}))
            self.assertEqual(schedule.confirmed_matches(folder,now),[])

    def test_no_accidental_publication_or_oversized_cdn_upload(self):
        for variables,expected in [({},False),({'VM_PUBLISH':'1'},False),
          ({'VM_PUBLISH':'1','GITHUB_ACTIONS':'true','GITHUB_REF':'refs/heads/review'},False),
          ({'VM_PUBLISH':'1','GITHUB_ACTIONS':'true','GITHUB_REF':'refs/heads/main'},True)]:
            with patch.dict(os.environ,variables,clear=True):self.assertEqual(media.publication_enabled(),expected)
        with patch.dict(os.environ,{},clear=True),patch.object(emission,'git') as git:
            with self.assertRaises(RuntimeError):emission.publish(Path('x.mp4'),Path('x.jpg'),Path('x.m4a'))
            git.assert_not_called()
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'too-large.mp4'
            with file.open('wb') as stream:stream.truncate(media.CDN_MAX_BYTES)
            with self.assertRaises(RuntimeError):media.validate_cdn_files([file])
            with file.open('wb') as stream:stream.truncate(media.CDN_PACKAGE_BYTES)
            with self.assertRaises(RuntimeError):media.validate_cdn_package(folder)

    def test_piper_failure_does_not_become_an_espeak_publication(self):
        with patch.dict(os.environ,{},clear=True),patch.object(debate,'voice_model',return_value=Path('voice.onnx')),patch.object(debate.subprocess,'run',side_effect=RuntimeError('modèle indisponible')) as process:
            with self.assertRaises(RuntimeError):debate.speak('Le PSG joue.','PRESENTATEUR',Path('x.wav'),True)
            self.assertEqual(process.call_count,1)
            args=process.call_args.args[0]
            self.assertLess(float(args[args.index('--length-scale')+1]),0.84)
            self.assertIn('Paris Saint-Germain',process.call_args.kwargs['input'].decode())

    def test_per_episode_links_survive_a_later_media_commit(self):
        original=json.loads((ROOT/'studio/emissions.json').read_text())[0]
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);tv=root/'studio/tv';tv.mkdir(parents=True)
            row=dict(original);row.pop('media_sha',None)
            (tv/(row['id']+'.json')).write_text(json.dumps(row))
            listing=root/'studio/emissions.json';listing.write_text(json.dumps([original]))
            sha=tv/'_branche.json';sha.write_text(json.dumps({'sha':'b'*40,'fichiers':[row['fichier']]}))
            with patch.object(emission,'ROOT',root),patch.object(emission,'LIST',listing),patch.object(emission,'SHA_FILE',sha):emission.rebuild_list()
            result=json.loads(listing.read_text())[0]
            self.assertEqual(result['video'],original['video'])
            self.assertTrue((root/'studio/episodes'/f"{row['id']}.html").is_file())

    def test_social_metadata_exists_without_javascript_and_is_escaped(self):
        row=dict(json.loads((ROOT/'studio/emissions.json').read_text())[0])
        row['titre']='Une émission <script>alert(1)</script>'
        with tempfile.TemporaryDirectory() as folder:
            pages.build_episode_pages([row],folder)
            text=(Path(folder)/'studio/episodes'/f"{row['id']}.html").read_text()
            self.assertIn('property="og:video:type" content="video/mp4"',text)
            self.assertIn('property="og:url" content="'+pages.page_url(row['id'])+'"',text)
            self.assertNotIn('<script>alert(1)</script>',text)
            self.assertIn('&lt;script&gt;',text)

    def test_real_render_codec_sync_faststart_audio_and_short_intro(self):
        def tone(text,perso,out,use_piper):
            with wave.open(str(out),'wb') as wav:
                wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(48000)
                wav.writeframes(struct.pack('<h',300)*48000)
            return 'test-audio'
        script={'titre':'Essai technique — aucune actualité publiée','repliques':[('PRESENTATEUR','Contrôle de la lecture, de la conclusion et des sous-titres.') ]}
        with tempfile.TemporaryDirectory() as folder,patch.object(debate,'piper_ready',return_value=True),patch.object(debate,'speak',side_effect=tone):
            output=Path(folder)/'test.mp4';total,engines=debate.build_video(script,output)
            info=media.probe(output);video=next(stream for stream in info['streams'] if stream['codec_type']=='video')
            audio=next(stream for stream in info['streams'] if stream['codec_type']=='audio')
            self.assertEqual(engines,['test-audio'])
            self.assertAlmostEqual(total,0.8+1+0.12+5,places=2)
            self.assertAlmostEqual(float(info['format']['duration']),total,delta=0.15)
            self.assertEqual((video['codec_name'],video['width'],video['height'],video['avg_frame_rate'],video['pix_fmt']),('h264',1280,720,'24/1','yuv420p'))
            self.assertEqual((audio['codec_name'],audio['sample_rate']),('aac','48000'))
            self.assertTrue(output.with_suffix('.m4a').is_file())
            data=output.read_bytes();self.assertLess(data.index(b'moov'),data.index(b'mdat'))
            subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True)
            from PIL import Image
            with Image.open(output.with_suffix('.jpg')) as image:self.assertEqual(image.size,(1280,720))

    def test_optional_hd_master_reuses_audio_and_preserves_both_profiles(self):
        def tone(text,perso,out,use_piper):
            with wave.open(str(out),'wb') as wav:
                wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(48000);wav.writeframes(struct.pack('<h',300)*48000)
            return 'test-audio'
        script={'titre':'Contrôle des deux profils','repliques':[('PRESENTATEUR','Contrôle technique des originaux du programme.')]}
        encode=media.encode_hd_master
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'VM_VIDEO_PROFILE':'cdn','VM_KEEP_HD_MASTER':'1'}),patch.object(debate,'piper_ready',return_value=True),patch.object(debate,'speak',side_effect=tone) as speak:
            master=Path(folder)/'hd.mp4'
            with patch.object(media,'encode_hd_master',side_effect=lambda frames,output,total,music:encode(frames,master,total,music)):
                light=Path(folder)/'cdn.mp4';debate.build_video(script,light)
            self.assertEqual(speak.call_count,1)
            frame_rate=lambda file:next(row for row in media.probe(file)['streams'] if row['codec_type']=='video')['avg_frame_rate']
            self.assertEqual(frame_rate(light),'12/1')
            self.assertEqual(frame_rate(master),'24/1')
            subprocess.run(['ffmpeg','-v','error','-i',str(master),'-f','null','-'],check=True)

    def test_real_cdn_profile_remains_playable_and_fits_transport(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'VM_VIDEO_PROFILE':'cdn'}):
            root=Path(folder)
            Image.new('RGB',(1280,720),'#14285a').save(root/'frame.png')
            (root/'images.txt').write_text("file 'frame.png'\nduration 2\nfile 'frame.png'\n")
            with wave.open(str(root/'voix.wav'),'wb') as wav:
                wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(48000)
                wav.writeframes(struct.pack('<h',300)*96000)
            output=root/'cdn.mp4'
            info=media.encode_video(root,output,2,debate.ASSETS/'beat.m4a')
            video=next(stream for stream in info['streams'] if stream['codec_type']=='video')
            self.assertEqual(video['avg_frame_rate'],'12/1')
            media.validate_cdn_files([output,output.with_suffix('.m4a')])
            subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True)

    def test_long_programme_preserves_sources_and_real_chapter_times(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'studio/tv').mkdir(parents=True);(root/'studio/tmp').mkdir()
            file=root/'fixture.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=blue:s=320x180:r=24',
                            '-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','1','-c:v','libx264',
                            '-threads','2','-pix_fmt','yuv420p','-c:a','aac',str(file)],check=True)
            source=file.read_bytes()
            for universe in ['foot','actus','gaming']:
                name=universe+'-test.mp4';(root/'studio/tmp'/name).write_bytes(source)
                (root/'studio/tv'/(universe+'.json')).write_text(json.dumps({'id':universe+'-test',
                  'univers':universe,'format':'edition','moment':'matin','date':'2026-10-22T07:00:00+02:00',
                  'titre':'Essai technique '+universe,'fichier':name}))
            result=assemble(root,'matin','2026-10-22',root/'programme.mp4')
            self.assertFalse(result['publie'])
            self.assertEqual([chapter['univers'] for chapter in result['chapitres']],['foot','actus','gaming'])
            self.assertEqual([chapter['debut_secondes'] for chapter in result['chapitres']],[0,1,2])
            self.assertAlmostEqual(result['duree_mesuree'],3,delta=0.15)
            self.assertEqual((root/'studio/tmp/foot-test.mp4').read_bytes(),source)
            subprocess.run(['ffmpeg','-v','error','-i',str(root/'programme.mp4'),'-f','null','-'],check=True)

    def test_long_programme_refuses_missing_fresh_news(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(subprocess,'run') as process:
            (Path(folder)/'studio/tv').mkdir(parents=True)
            with self.assertRaises(RuntimeError):assemble(folder,'soir','2026-10-22',Path(folder)/'programme.mp4')
            process.assert_not_called()


if __name__=='__main__':unittest.main(verbosity=2)
