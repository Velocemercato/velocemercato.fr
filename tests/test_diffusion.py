import base64
import datetime as dt
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import diffuser_jt as D
from tools import connecter_diffusion as C


KEY = base64.urlsafe_b64encode(b'k' * 32).decode()
MANIFEST = {'id': 'jt-2026-10-22-matin', 'date': '2026-10-22', 'moment': 'matin', 'duree_mesuree': 3,
            'chapitres': [{'debut_secondes': 0, 'univers': 'foot', 'titre': 'Football sourcé'},
                         {'debut_secondes': 1, 'univers': 'actus', 'titre': 'Actualité sourcée'},
                         {'debut_secondes': 2, 'univers': 'gaming', 'titre': 'Gaming sourcé'}]}


class DiffusionTests(unittest.TestCase):
    def test_state_encrypts_tokens_sessions_and_private_ids_and_checks_authentication(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'state.enc'
            state = D.State(path, KEY)
            state.data['tokens'] = {'youtube': 'refresh-token-test-secret'}
            state.data['programmes'] = {'private-video-id': 'session-test-secret'}
            state.save()
            self.assertNotIn(b'refresh-token', path.read_bytes())
            self.assertNotIn(b'private-video', path.read_bytes())
            loaded = D.State(path, KEY)
            self.assertEqual(loaded.data, state.data)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(D.DeliveryError):
                D.State(path, base64.urlsafe_b64encode(b'x'*32).decode())
            path.write_bytes(path.read_bytes()[:-1] + b'x')
            with self.assertRaises(D.DeliveryError):
                D.State(path, KEY)

    def test_missing_accounts_and_infrastructure_google_credentials_do_not_activate(self):
        with patch.dict('os.environ', {'GOOGLE_APPLICATION_CREDENTIALS': '/tmp/infrastructure.json'}, clear=True):
            self.assertFalse(D.enabled('youtube'))
            self.assertFalse(D.enabled('twitch'))
            with patch.object(D, 'HTTP') as http, patch.object(sys, 'argv', ['diffuser_jt.py']):
                D.main()
                http.assert_not_called()

    def test_rotated_twitch_refresh_is_saved_and_reconnection_replaces_it(self):
        variables = {'TWITCH_CLIENT_ID': 'client', 'TWITCH_CLIENT_SECRET': 'app-secret', 'TWITCH_REFRESH_TOKEN': 'initial'}
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', variables):
            state = D.State(Path(folder)/'state.enc', KEY)
            http = Mock()
            http.json.return_value = {'access_token': 'access', 'refresh_token': 'rotated'}
            D.access_token('twitch', state, http)
            D.access_token('twitch', state, http)
            self.assertEqual(http.json.call_args.kwargs['form']['refresh_token'], 'rotated')
            with patch.dict('os.environ', {'TWITCH_REFRESH_TOKEN': 'reconnected'}):
                D.access_token('twitch', state, http)
                self.assertEqual(http.json.call_args.kwargs['form']['refresh_token'], 'reconnected')
            self.assertNotIn(b'rotated', state.path.read_bytes())

    def test_youtube_metadata_discloses_ai_and_uses_measured_chapters(self):
        metadata = D.youtube_metadata(MANIFEST)
        self.assertTrue(metadata['status']['containsSyntheticMedia'])
        self.assertEqual(metadata['status']['privacyStatus'], 'private')
        self.assertIn('00:00 Football sourcé', metadata['snippet']['description'])
        self.assertIn('https://vmunivers.fr/', metadata['snippet']['description'])
        self.assertLessEqual(len(metadata['snippet']['title']), 100)

    def test_youtube_resumable_upload_handles_308_and_records_final_confirmation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            file = root/'master.mp4';file.write_bytes(b'0123456789')
            state = D.State(root/'state.enc', KEY)
            receipt = state.data['programmes'].setdefault('test', {})
            http = Mock()
            http.request.side_effect = [
                (200, {'Location': 'https://www.googleapis.com/upload/session-test'}, b''),
                (308, {}, b''),
                (308, {'Range': 'bytes=0-3'}, b''),
                (308, {'Range': 'bytes=0-7'}, b''),
                (200, {}, b'{"id":"aB1cdEF2ghi"}'),
            ]
            client = D.YouTube(http, state, 'access-test')
            ident = client.upload(file, D.youtube_metadata(MANIFEST), receipt, chunk_size=4)
            self.assertEqual(ident, 'aB1cdEF2ghi')
            self.assertEqual(receipt['status'], 'private')
            self.assertNotIn('session', receipt)
            chunks = [call.args[3] for call in http.request.call_args_list[2:]]
            self.assertEqual(b''.join(chunks), file.read_bytes())
            before = http.request.call_count
            self.assertEqual(client.upload(file, {}, receipt), ident)
            self.assertEqual(http.request.call_count, before)

    def test_youtube_resume_recovers_after_lost_response_without_duplicate_bytes(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(D.time, 'sleep'):
            root = Path(folder);file=root/'master.mp4';file.write_bytes(b'0123456789')
            state=D.State(root/'state.enc',KEY);receipt={'status':'uploading','session':'https://www.googleapis.com/upload/session-test'}
            http=Mock();http.request.side_effect=[(308,{'Range':'bytes=0-3'},b''),D.DeliveryError('réponse perdue'),
                (308,{'Range':'bytes=0-7'},b''),(200,{},b'{"id":"aB1cdEF2ghi"}')]
            ident=D.YouTube(http,state,'token-test').upload(file,{},receipt,chunk_size=4)
            self.assertEqual(ident,'aB1cdEF2ghi')
            self.assertEqual(http.request.call_args_list[1].args[3],b'4567')
            self.assertEqual(http.request.call_args_list[3].args[3],b'89')

    def test_youtube_never_follows_external_session_or_uploads_wrong_channel(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ',{'YOUTUBE_CHANNEL_ID':'expected'}):
            state=D.State(Path(folder)/'state.enc',KEY);http=Mock()
            http.json.return_value={'items':[{'id':'another-channel'}]}
            with self.assertRaises(D.DeliveryError):D.YouTube(http,state,'token').verify_channel()
            file=Path(folder)/'test.mp4';file.write_bytes(b'video')
            http.request.return_value=(200,{'Location':'https://example.org/session'},b'')
            with self.assertRaises(D.DeliveryError):D.YouTube(http,state,'token').upload(file,{}, {})
            self.assertEqual(http.request.call_count,1)

    def test_youtube_does_not_announce_public_before_hd_processing_or_confirmed_visibility(self):
        with tempfile.TemporaryDirectory() as folder:
            state=D.State(Path(folder)/'state.enc',KEY);http=Mock();receipt={'video_id':'aB1cdEF2ghi','status':'private'}
            http.json.return_value={'items':[{'id':'aB1cdEF2ghi','status':{'uploadStatus':'processed','privacyStatus':'private'},
                                               'processingDetails':{'processingStatus':'processing'}}]}
            with self.assertRaises(D.DeliveryError):D.YouTube(http,state,'token').make_public(receipt,timeout=0)
            self.assertEqual(http.json.call_count,1)
            http.json.side_effect=[{'items':[{'processingDetails':{'processingStatus':'succeeded'}}]}, {},
                {'items':[{'id':'aB1cdEF2ghi','status':{'privacyStatus':'private'}}]}]
            with self.assertRaises(D.DeliveryError):D.YouTube(http,state,'token').make_public(receipt)
            self.assertEqual(receipt['status'],'private')
            http.json.side_effect=[{'items':[{'processingDetails':{'processingStatus':'succeeded'}}]}, {},
                {'items':[{'id':'aB1cdEF2ghi','status':{'privacyStatus':'public'}}]}]
            D.YouTube(http,state,'token').make_public(receipt)
            self.assertEqual(receipt['status'],'published')

    def test_youtube_stays_private_without_owner_consent(self):
        with tempfile.TemporaryDirectory() as folder:
            state=D.State(Path(folder)/'state.enc',KEY)
            env={'VM_AUTO_YOUTUBE':'true','YOUTUBE_CLIENT_ID':'c','YOUTUBE_CLIENT_SECRET':'s','YOUTUBE_REFRESH_TOKEN':'r','YOUTUBE_CHANNEL_ID':'UC1','VM_YOUTUBE_PUBLIC':''}
            class FakeYT:
                calls=[]
                def __init__(self,*a):pass
                def verify_channel(self):pass
                def upload(self,file,meta,receipt):receipt.update(video_id='aB1cdEF2ghi',status='private')
                def make_public(self,receipt):FakeYT.calls.append('public');receipt['status']='published'
            with patch.dict(os.environ,env),patch.object(D,'access_token',return_value='t'),patch.object(D,'YouTube',FakeYT),patch.object(D,'youtube_metadata',return_value={}):
                receipts,errors=D.publish('f.mp4',{'id':'prog1'},state)
                self.assertEqual(errors,[]);self.assertEqual(receipts['youtube']['status'],'private_ready');self.assertEqual(FakeYT.calls,[])
                D.publish('f.mp4',{'id':'prog1'},state);self.assertEqual(FakeYT.calls,[])
            path=Path(folder)/'d.json';D.public_index(path,MANIFEST,receipts);self.assertFalse(path.exists() and 'aB1cdEF2ghi' in path.read_text())
            env['VM_YOUTUBE_PUBLIC']='true'
            with patch.dict(os.environ,env),patch.object(D,'access_token',return_value='t'),patch.object(D,'YouTube',FakeYT),patch.object(D,'youtube_metadata',return_value={}):
                receipts,_=D.publish('f.mp4',{'id':'prog1'},state)
            self.assertEqual(FakeYT.calls,['public']);self.assertEqual(receipts['youtube']['status'],'published')

    def test_twitch_preserves_existing_live_and_checks_connected_identity(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict('os.environ',{'TWITCH_BROADCASTER_ID':'123','TWITCH_CLIENT_ID':'client'}):
            state=D.State(Path(folder)/'state.enc',KEY);http=Mock()
            http.json.side_effect=[{'data':[{'id':'123','login':'testchannel'}]},{'data':[{'id':'live-existing'}]}]
            receipt={}
            with patch.object(D.subprocess,'Popen') as process:
                D.Twitch(http,state,'token').stream(Path('test.mp4'),'Titre',receipt,30)
                process.assert_not_called()
            self.assertEqual(receipt['status'],'skipped_live')
            http.json.side_effect=[{'data':[{'id':'456','login':'other'}]}]
            with self.assertRaises(D.DeliveryError):D.Twitch(http,state,'token').stream(Path('test.mp4'),'Titre',{},30)

    def test_twitch_requires_live_confirmation_and_stream_completion_before_success(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict('os.environ',{'TWITCH_BROADCASTER_ID':'123','TWITCH_CLIENT_ID':'client'}):
            state=D.State(Path(folder)/'state.enc',KEY);http=Mock()
            http.json.side_effect=[{'data':[{'id':'123','login':'testchannel'}]},{'data':[]},{},
                {'data':[{'stream_key':'live_123_SECRET_TEST'}]},{'data':[{'id':'new-live'}]}]
            process=Mock();process.poll.side_effect=[None,0];process.wait.return_value=0
            receipt={}
            with patch.object(D.subprocess,'Popen',return_value=process):
                D.Twitch(http,state,'token').stream(Path('master.mp4'),'Titre',receipt,30)
            self.assertEqual(receipt['status'],'ended')
            self.assertNotIn('SECRET_TEST',json.dumps(receipt))
            # Une reprise de cette même émission ne doit pas envoyer un second direct.
            with patch.object(D.subprocess,'Popen') as again:
                D.Twitch(http,state,'token').stream(Path('master.mp4'),'Titre',receipt,30)
                again.assert_not_called()

    def test_ambiguous_twitch_attempt_and_failed_state_persistence_prevent_retries(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict('os.environ',{'TWITCH_BROADCASTER_ID':'123','TWITCH_CLIENT_ID':'client'}):
            state=D.State(Path(folder)/'state.enc',KEY);http=Mock()
            with self.assertRaises(D.DeliveryError),patch.object(D.subprocess,'Popen') as process:
                D.Twitch(http,state,'token').stream(Path('master.mp4'),'Titre',{'status':'starting'},30)
                process.assert_not_called()
            state.persist=Mock(side_effect=RuntimeError('État distant indisponible'))
            file=Path(folder)/'master.mp4';file.write_bytes(b'video')
            with self.assertRaises(RuntimeError):D.YouTube(http,state,'token').upload(file,{}, {})
            http.request.assert_not_called()

    def test_private_uploads_never_appear_in_public_site_index(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'public.json'
            D.public_index(path,MANIFEST,{'youtube':{'status':'private','video_id':'private-secret'}})
            self.assertFalse(path.exists())
            D.public_index(path,MANIFEST,{'youtube':{'status':'published','url':'https://www.youtube.com/watch?v=aB1cdEF2ghi'}})
            self.assertIn('https://www.youtube.com/watch?v=',path.read_text())
            self.assertNotIn('private-secret',path.read_text())

    def test_account_setup_enables_only_after_success_and_preserves_encryption_key(self):
        calls=[]
        def github(*args,input_value=None):
            calls.append((args,input_value))
            if args[:2]==('secret','list'):return '[{"name":"VM_DIFFUSION_STATE_KEY"}]'
            if args[:2]==('variable','list'):return '[]'
            return ''
        with patch.object(C,'gh',side_effect=github):
            C.store('owner/repo','youtube',{'YOUTUBE_REFRESH_TOKEN':'test-refresh'})
        self.assertEqual(calls[-1][0],('variable','set','VM_AUTO_YOUTUBE','--repo','owner/repo','--body','true'))
        self.assertFalse(any(args[:3]==('secret','set','VM_DIFFUSION_STATE_KEY') for args,_ in calls))
        self.assertIn((('variable','set','VM_YOUTUBE_PUBLIC','--repo','owner/repo','--body','false'),None),calls)
        self.assertTrue(any(value=='test-refresh' and 'test-refresh' not in args for args,value in calls))
        with patch.object(C,'gh') as github:
            with self.assertRaises(D.DeliveryError):C.store('owner/repo','twitch',{'TWITCH_REFRESH_TOKEN':None})
            github.assert_not_called()

    def test_google_pkce_callback_runs_on_loopback_without_logging_code(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        received={}
        def browser(url):
            params=parse_qs(urlsplit(url).query);received.update(params)
            def callback():
                with urlopen(params['redirect_uri'][0]+'?state='+params['state'][0]+'&code=TEST_OAUTH_CODE',timeout=5) as response:
                    self.assertEqual(response.status,200)
            Thread(target=callback,daemon=True).start()
            return True
        with patch.object(C.webbrowser,'open',side_effect=browser),patch('sys.stdout',new_callable=io.StringIO) as output:
            code,redirect,verifier=C.authorize('youtube','client-test',port=port,timeout=5)
        self.assertEqual(code,'TEST_OAUTH_CODE')
        self.assertTrue(redirect.startswith('http://127.0.0.1:'))
        self.assertEqual(received['code_challenge_method'],['S256'])
        import hashlib
        self.assertEqual(received['code_challenge'][0],base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('='))
        self.assertNotIn(code,output.getvalue())

    def test_android_codespace_address_is_available_without_any_account_or_secret(self):
        with patch.dict('os.environ',{'CODESPACE_NAME':'vm-android-test'}),patch.object(C,'gh') as github,patch.object(sys,'argv',['connecter_diffusion.py','youtube','--codespaces','--adresse']),patch('sys.stdout',new_callable=io.StringIO) as output:
            C.main()
            self.assertEqual(output.getvalue().strip(),'https://vm-android-test-8765.app.github.dev/callback')
            github.assert_not_called()
        with patch.dict('os.environ',{'CODESPACE_NAME':''}):
            with self.assertRaises(D.DeliveryError):C.codespace_redirect()
        with self.assertRaises(D.DeliveryError):
            C.authorize('youtube','client-test',redirect_uri='https://example.org/callback')

    def test_codespace_https_callback_works_without_a_browser_on_the_server(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        original_server=C.HTTPServer
        def server(address,handler):
            self.assertEqual(address,('0.0.0.0',port))
            instance=original_server(address,handler)
            def callback():
                import urllib.error
                try:
                    urlopen(f'http://127.0.0.1:{port}/callback?state=incorrect&code=WRONG',timeout=5)
                except urllib.error.HTTPError as error:
                    self.assertEqual(error.code,400)
                with urlopen(f'http://127.0.0.1:{port}/callback?state=state-test&code=PRIVATE_TEST_CODE',timeout=5) as response:
                    self.assertEqual(response.status,200)
            Thread(target=callback,daemon=True).start()
            return instance
        redirect=f'https://vm-android-test-{port}.app.github.dev/callback'
        with patch.object(C,'HTTPServer',side_effect=server),patch.object(C.secrets,'token_urlsafe',side_effect=['state-test','verifier-test']),patch.object(C.webbrowser,'open') as browser,patch('sys.stdout',new_callable=io.StringIO) as output:
            code,received,_=C.authorize('youtube','client-test',port=port,timeout=5,redirect_uri=redirect)
        self.assertEqual((code,received),('PRIVATE_TEST_CODE',redirect))
        browser.assert_not_called()
        self.assertNotIn(code,output.getvalue())

    def test_real_hd_masters_assemble_only_when_fresh_and_authorized(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);masters=root/'masters';masters.mkdir()
            file=root/'source.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=blue:s=1280x720:r=24',
                '-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','1','-c:v','libx264','-threads','2',
                '-pix_fmt','yuv420p','-c:a','aac',str(file)],check=True)
            for universe in ['foot','actus','gaming']:
                name=universe+'-test.mp4';(masters/name).write_bytes(file.read_bytes())
                (masters/(universe+'.json')).write_text(json.dumps({'id':universe+'-test','univers':universe,
                    'format':'edition','moment':'matin','date':'2026-10-22T07:00:00+02:00','fichier':name,'titre':universe}))
            now=dt.datetime(2026,10,22,6,tzinfo=dt.timezone.utc)
            authorization={'publish':True,'created':now.isoformat(),'date':'2026-10-22','moment':'matin','run_id':'42'}
            (masters/'_autorisation.json').write_text(json.dumps(authorization))
            result=D.prepare(masters,root/'programme.mp4',now=now,expected_run='42')
            self.assertAlmostEqual(result['duree_mesuree'],3,delta=.15)
            self.assertEqual(result['id'],'jt-2026-10-22-matin')
            with self.assertRaises(D.DeliveryError):D.prepare(masters,root/'bad.mp4',now=now,expected_run='43')
            with self.assertRaises(D.DeliveryError):D.prepare(masters,root/'bad.mp4',now=now+dt.timedelta(hours=4),expected_run='42')
            ident='foot-speciale-test'
            (masters/(ident+'.mp4')).write_bytes(file.read_bytes())
            (masters/(ident+'.json')).write_text(json.dumps({'id':ident,'univers':'foot','format':'speciale',
                'date':'2026-10-22T07:00:00+02:00','titre':'Spéciale de contrôle'}))
            authorization.update(format='speciale',unit=ident)
            (masters/'_autorisation.json').write_text(json.dumps(authorization))
            special=D.prepare(masters,root/'speciale.mp4',now=now,expected_run='42')
            self.assertEqual(special['id'],ident)
            self.assertEqual(special['universes'],['foot'])
            self.assertIn('Spéciale avant-match',D.youtube_metadata(special)['snippet']['title'])
            authorization['publish']=False;(masters/'_autorisation.json').write_text(json.dumps(authorization))
            with self.assertRaises(D.DeliveryError):D.prepare(masters,root/'bad.mp4',now=now,expected_run='42')


if __name__=='__main__':
    unittest.main(verbosity=2)
