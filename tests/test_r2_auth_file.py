from unittest.mock import patch
from types import SimpleNamespace
import unittest
from scripts import r2_utils

class ExistingAuthFileTests(unittest.TestCase):
    def test_existing_auth_file_is_passed_to_wrangler_without_reading_or_copying_it(self):
        name='/existing publisher/private config.env'
        with patch.dict('os.environ',{'WRANGLER_ENV_FILE':name}),\
                patch.object(r2_utils.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='ok')) as run:
            self.assertEqual(r2_utils._run('r2','object','get','bucket/manifest.json','--remote'),'ok')
            args,kwargs=run.call_args
            self.assertEqual(args[0][:4],['npx','wrangler','r2','object'])
            self.assertEqual(args[0][-2:],['--env-file',name])
            self.assertNotIn('shell',kwargs)
