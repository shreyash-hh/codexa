from unittest.mock import patch
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Repository, AnalysisRun


class AnalyzeAPITests(APITestCase):
    def setUp(self):
        self.analyze_url = '/api/analyze/'
        self.sample_github_url = 'https://github.com/octocat/Hello-World'

    def test_analyze_invalid_payload(self):
        response = self.client.post(self.analyze_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('github_url', response.data['errors'])

    def test_analyze_invalid_github_url_format(self):
        response = self.client.post(
            self.analyze_url,
            {'github_url': 'https://notgithub.com/someone/repo'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    @patch('core.views.clone_github_repo')
    @patch('core.views.cleanup_cloned_repo')
    def test_analyze_successful_flow(self, mock_cleanup, mock_clone):
        mock_clone.return_value = {
            'success': True,
            'owner': 'octocat',
            'name': 'Hello-World',
            'github_url': self.sample_github_url,
            'clone_path': '/tmp/codexa_Hello-World_123',
            'cloned_at': timezone.now(),
            'metadata': {
                'name': 'Hello-World',
                'owner': 'octocat',
                'description': 'My first repo!',
                'language': 'Python',
                'default_branch': 'master'
            }
        }
        mock_cleanup.return_value = True

        response = self.client.post(
            self.analyze_url,
            {'github_url': self.sample_github_url},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['repository']['name'], 'Hello-World')
        self.assertEqual(response.data['repository']['owner'], 'octocat')
        self.assertIn('analysis_run_id', response.data)

        # Confirm DB records
        self.assertTrue(Repository.objects.filter(github_url=self.sample_github_url).exists())
        repo = Repository.objects.get(github_url=self.sample_github_url)
        self.assertEqual(repo.status, 'cloned')
        self.assertTrue(AnalysisRun.objects.filter(repository=repo).exists())
