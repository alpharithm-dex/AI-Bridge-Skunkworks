import unittest
import json
import io
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

class TestBiasApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bias Correction API', response.data)
        self.assertIn(b'Single Sentence Correction', response.data)
        self.assertIn(b'Batch Processing', response.data)

    def test_batch_correct(self):
        batch_data = [
            {
                "id": "test_001",
                "text": "Mosetsana o apea dijo.",
                "lang": "tn"
            }
        ]
        
        data = {
            'file': (io.BytesIO(json.dumps(batch_data).encode('utf-8')), 'test.json')
        }
        
        response = self.app.post('/batch-correct', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'test_001')
        self.assertIn('correction', result[0])

if __name__ == '__main__':
    unittest.main()
