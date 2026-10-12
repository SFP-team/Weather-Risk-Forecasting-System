import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

OPS = Path(__file__).resolve().parents[2] / 'ops' / 'bin'


def load(name):
    spec = importlib.util.spec_from_file_location(name, OPS / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


watchdog = load('api_watchdog')
preflight = load('preflight')


class DecideTests(unittest.TestCase):
    def test_stopped_service_is_left_alone(self):
        self.assertEqual(watchdog.decide(False, None, 5), ('none', 0))

    def test_one_failed_check_waits_and_the_second_restarts(self):
        action, failures = watchdog.decide(True, None, 0)
        self.assertEqual((action, failures), ('none', 1))
        self.assertEqual(watchdog.decide(True, None, failures), ('restart_unreachable', 0))

    def test_long_busy_analysis_restarts(self):
        busy = {'status': 'busy', 'busy_seconds': watchdog.BUSY_LIMIT_S + 1}
        self.assertEqual(watchdog.decide(True, busy, 0), ('restart_busy', 0))

    def test_healthy_or_briefly_busy_service_resets_failures(self):
        self.assertEqual(watchdog.decide(True, {'status': 'ready', 'busy_seconds': None}, 1), ('none', 0))
        self.assertEqual(watchdog.decide(True, {'status': 'busy', 'busy_seconds': 30.0}, 1), ('none', 0))


class RotateTests(unittest.TestCase):
    def test_rotation_keeps_the_live_file_and_shifts_old_copies(self):
        with tempfile.TemporaryDirectory() as folder:
            log = Path(folder) / 'api.log'
            log.write_bytes(b'x' * 50)
            (Path(folder) / 'api.log.1').write_bytes(b'old')
            self.assertTrue(watchdog.rotate(log, limit=10, keep=3))
            self.assertEqual(log.stat().st_size, 0)
            self.assertEqual((Path(folder) / 'api.log.1').read_bytes(), b'x' * 50)
            self.assertEqual((Path(folder) / 'api.log.2').read_bytes(), b'old')

    def test_small_or_missing_logs_are_not_rotated(self):
        with tempfile.TemporaryDirectory() as folder:
            log = Path(folder) / 'api.log'
            self.assertFalse(watchdog.rotate(log, limit=10))
            log.write_bytes(b'abc')
            self.assertFalse(watchdog.rotate(log, limit=10))


class PreflightTests(unittest.TestCase):
    def test_full_project_drive_refuses_and_full_root_only_warns(self):
        gib = preflight.GIB
        with tempfile.TemporaryDirectory() as folder:
            def usage(path, free_root, free_project):
                free = free_root if str(path) == '/' else free_project
                return type('Usage', (), {'free': free})()
            with patch.object(preflight.shutil, 'disk_usage', lambda p: usage(p, 1 * gib, 500 * gib)):
                self.assertEqual(preflight.main(Path(folder)), 0)
            with patch.object(preflight.shutil, 'disk_usage', lambda p: usage(p, 500 * gib, 1 * gib)):
                self.assertEqual(preflight.main(Path(folder)), 1)
            self.assertTrue((Path(folder) / 'cache/location_api').is_dir())


if __name__ == '__main__':
    unittest.main()
