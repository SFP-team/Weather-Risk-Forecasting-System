"""Synthetic-only recovery tests; never interrupt a production weather worker."""
import multiprocessing
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import requests
import shutil
import fcntl
from pilot import Downloads, retry_delay
from datetime import datetime, timezone


class Response:
    headers={}
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def raise_for_status(self): pass
    def iter_content(self,*args): yield b'synthetic-weather-fixture'


def crash_before_publish(root):
    client=Downloads(Path(root))
    with patch.object(client,'safe_space'), patch.object(client.session,'get',return_value=Response()), patch('pilot.os.replace',side_effect=lambda *args:os._exit(73)):
        client.get('https://fixture.invalid/object',Path(root)/'payload')


class RecoveryTests(unittest.TestCase):
    def test_http_date_retry_after(self):
        now=datetime(2020,1,1,tzinfo=timezone.utc)
        self.assertEqual(retry_delay('Wed, 01 Jan 2020 00:01:00 GMT',1,now),60)
        self.assertEqual(retry_delay('Tue, 31 Dec 2019 23:59:00 GMT',1,now),2)
        self.assertEqual(retry_delay('invalid',2,now),4)

    def test_html_200_not_published(self):
        class HTML(Response):
            headers={'Content-Type':'text/html'}
            def iter_content(self,*args): yield b'<html>synthetic error</html>'
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root=Path(directory); client=Downloads(root)
            with patch.object(client,'safe_space'),patch.object(client.session,'get',return_value=HTML()):
                with self.assertRaises(ValueError): client.get('https://fixture.invalid/html',root/'payload')
            self.assertFalse((root/'payload').exists())
            self.assertEqual(client.db.execute('SELECT status FROM objects').fetchone()[0],'failed_terminal')
            client.db.close()

    def test_throttling_retry_after(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root=Path(directory); client=Downloads(root)
            response=requests.Response(); response.status_code=429; response.headers['Retry-After']='17'
            error=requests.HTTPError('fixture throttled',response=response)
            with patch.object(client,'safe_space'),patch.object(client.session,'get',side_effect=[error,Response()]) as request,patch('pilot.time.sleep') as sleep:
                client.get('https://fixture.invalid/throttle',root/'payload')
                self.assertEqual(request.call_count,2)
                sleep.assert_called_with(17)
            client.db.close()

    def test_disk_floor_and_project_quota(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            client=Downloads(Path(directory))
            with patch('pilot.subprocess.check_output',return_value='/media/fpt/fpt2'),patch('pilot.shutil.disk_usage',return_value=shutil._ntuple_diskusage(100,90,10)):
                with self.assertRaisesRegex(RuntimeError,'free-space'): client.safe_space()
            with patch('pilot.subprocess.check_output',side_effect=['/media/fpt/fpt2',str(client.disk_limit+1)+' fixture']),patch('pilot.shutil.disk_usage',return_value=shutil._ntuple_diskusage(100,10,90)):
                with self.assertRaisesRegex(RuntimeError,'disk ceiling'): client.safe_space()
            client.db.close()

    def test_exclusive_worker_lock(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path=Path(directory)/'worker.lock'
            with path.open('a') as first,path.open('a') as second:
                fcntl.flock(first.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
                with self.assertRaises(BlockingIOError):
                    fcntl.flock(second.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)

    def test_real_child_interruption_and_resume(self):
        # Forked child's abrupt exit leaves SQLite committed and a partial file.
        # This root contains synthetic fixtures only and is automatically cleaned.
        with tempfile.TemporaryDirectory(prefix='weather-recovery-',dir=Path(__file__).parent) as directory:
            root=Path(directory)
            child=multiprocessing.get_context('fork').Process(target=crash_before_publish,args=(directory,))
            child.start(); child.join(10)
            if child.is_alive():
                child.terminate(); child.join(); self.fail('Test child timed out')
            self.assertEqual(child.exitcode,73)
            self.assertFalse((root/'payload').exists())
            self.assertTrue((root/'payload.partial').exists())
            client=Downloads(root)
            with patch.object(client,'safe_space'), patch.object(client.session,'get',return_value=Response()) as request:
                first=client.get('https://fixture.invalid/object',root/'payload')
                before=client.db.execute('SELECT value FROM counters').fetchone()[0]
                second=client.get('https://fixture.invalid/object',root/'payload')
                self.assertEqual(first,second)
                self.assertEqual(request.call_count,1)
                self.assertEqual(before,client.db.execute('SELECT value FROM counters').fetchone()[0])
            self.assertFalse((root/'payload.partial').exists())
            client.db.close()

    def test_retry_budget_survives_reopen(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root=Path(directory); client=Downloads(root)
            with patch.object(client,'safe_space'), patch.object(client.session,'get',side_effect=requests.Timeout('fixture')) as request, patch('pilot.time.sleep'):
                with self.assertRaises(requests.Timeout): client.get('https://fixture.invalid/timeout',root/'payload')
                self.assertEqual(request.call_count,5)
            client.db.close(); client=Downloads(root)
            with patch.object(client.session,'get') as request:
                with self.assertRaises(RuntimeError): client.get('https://fixture.invalid/timeout',root/'payload')
                request.assert_not_called()
            client.db.close()

    def test_terminal_failure_not_retried_on_restart(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root=Path(directory); client=Downloads(root)
            response=requests.Response(); response.status_code=403
            error=requests.HTTPError('fixture denied',response=response)
            with patch.object(client,'safe_space'),patch.object(client.session,'get',side_effect=error) as request:
                with self.assertRaises(requests.HTTPError): client.get('https://fixture.invalid/denied',root/'payload')
                self.assertEqual(request.call_count,1)
            client.db.close(); client=Downloads(root)
            with patch.object(client.session,'get') as request:
                with self.assertRaises(RuntimeError): client.get('https://fixture.invalid/denied',root/'payload')
                request.assert_not_called()
            client.db.close()

    def test_checksum_corruption_not_redownloaded_silently(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root=Path(directory); client=Downloads(root)
            with patch.object(client,'safe_space'),patch.object(client.session,'get',return_value=Response()):
                client.get('https://fixture.invalid/object',root/'payload')
            (root/'payload').write_bytes(b'corrupt synthetic fixture')
            with patch.object(client.session,'get') as request:
                with self.assertRaises(RuntimeError): client.get('https://fixture.invalid/object',root/'payload')
                request.assert_not_called()
            client.db.close()

    def test_mount_loss_blocks_network(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root=Path(directory); client=Downloads(root)
            with patch('pilot.subprocess.check_output',return_value='/'),patch.object(client.session,'get') as request:
                with self.assertRaisesRegex(RuntimeError,'mount'): client.get('https://fixture.invalid/object',root/'payload')
                request.assert_not_called()
            client.db.close()


if __name__=='__main__': unittest.main()
