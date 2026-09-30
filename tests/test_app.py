import unittest
import os
import tempfile
from app import create_app, app

class TestAppRoutes(unittest.TestCase):
    def test_default_app_client(self):
        client = app.test_client()
        docs_dir = app.config['DOCS_DIR']
        if os.path.exists(os.path.join(docs_dir, 'index.html')):
            response = client.get('/')
            self.assertEqual(response.status_code, 200)

        if os.path.exists(os.path.join(docs_dir, 'about.html')):
            response = client.get('/about')
            self.assertEqual(response.status_code, 200)

        response = client.get('/non-existent-page-xyz')
        self.assertEqual(response.status_code, 404)

    def test_isolated_custom_docs_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample files
            with open(os.path.join(tmpdir, 'index.html'), 'w') as f:
                f.write('<h1>Welcome</h1>')
            with open(os.path.join(tmpdir, 'portfolio.html'), 'w') as f:
                f.write('<h1>Portfolio</h1>')

            custom_app = create_app(docs_dir=tmpdir)
            client = custom_app.test_client()

            # Root path
            res_root = client.get('/')
            self.assertEqual(res_root.status_code, 200)
            self.assertIn(b'Welcome', res_root.data)

            # Extensionless fallback
            res_portfolio = client.get('/portfolio')
            self.assertEqual(res_portfolio.status_code, 200)
            self.assertIn(b'Portfolio', res_portfolio.data)

            # Direct file
            res_direct = client.get('/portfolio.html')
            self.assertEqual(res_direct.status_code, 200)
            self.assertIn(b'Portfolio', res_direct.data)

            # Missing file
            res_missing = client.get('/missing')
            self.assertEqual(res_missing.status_code, 404)

if __name__ == '__main__':
    unittest.main()
