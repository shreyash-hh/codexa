import tempfile
import os
from unittest.mock import patch
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Repository, AnalysisRun, Finding
from .analyzers.pylint_analyzer import analyze_and_save_pylint
from .analyzers.bandit_analyzer import analyze_and_save_bandit
from .analyzers.radon_analyzer import analyze_and_save_radon
from .analyzers.semgrep_analyzer import analyze_and_save_semgrep
from .analyzers.pip_audit_analyzer import analyze_and_save_pip_audit


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

    def test_pylint_analyzer_with_sample_code(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_code_path = os.path.join(temp_dir, 'bad_sample.py')
            with open(bad_code_path, 'w') as f:
                f.write('x = 1\ndef foo():\n  unused_var = 10\n')

            repo = Repository.objects.create(
                github_url='https://github.com/test/pylint-sample',
                name='pylint-sample',
                owner='test',
                status='cloned'
            )
            run = AnalysisRun.objects.create(repository=repo, status='running')

            findings = analyze_and_save_pylint(run, temp_dir)
            self.assertGreater(len(findings), 0)
            self.assertTrue(all(f.tool_name == 'pylint' for f in findings))
            self.assertTrue(Finding.objects.filter(run=run, tool_name='pylint').exists())

    def test_bandit_analyzer_with_insecure_code(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            insecure_code_path = os.path.join(temp_dir, 'insecure.py')
            with open(insecure_code_path, 'w') as f:
                f.write('password = "supersecretpassword123"\neval("1+1")\n')

            repo = Repository.objects.create(
                github_url='https://github.com/test/bandit-sample',
                name='bandit-sample',
                owner='test',
                status='cloned'
            )
            run = AnalysisRun.objects.create(repository=repo, status='running')

            findings = analyze_and_save_bandit(run, temp_dir)
            self.assertGreater(len(findings), 0)
            self.assertTrue(all(f.tool_name == 'bandit' for f in findings))
            self.assertTrue(Finding.objects.filter(run=run, tool_name='bandit').exists())

    def test_radon_analyzer_with_complex_code(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            complex_code_path = os.path.join(temp_dir, 'complex.py')
            # Create a deeply nested function to trigger high cyclomatic complexity
            nested_code = """
def complex_fn(a, b, c, d, e, f, g):
    if a:
        if b:
            return 1
        elif c:
            return 2
    elif d:
        if e:
            return 3
        elif f:
            return 4
    elif g:
        return 5
    return 0
"""
            with open(complex_code_path, 'w') as f:
                f.write(nested_code)

            repo = Repository.objects.create(
                github_url='https://github.com/test/radon-sample',
                name='radon-sample',
                owner='test',
                status='cloned'
            )
            run = AnalysisRun.objects.create(repository=repo, status='running')

            findings = analyze_and_save_radon(run, temp_dir)
            self.assertGreater(len(findings), 0)
            self.assertTrue(all(f.tool_name == 'radon' for f in findings))
            self.assertTrue(Finding.objects.filter(run=run, tool_name='radon').exists())

    def test_pip_audit_analyzer_with_vulnerable_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            req_path = os.path.join(temp_dir, 'requirements.txt')
            # Known historical vulnerable dependency
            with open(req_path, 'w') as f:
                f.write('urllib3==1.26.4\n')

            repo = Repository.objects.create(
                github_url='https://github.com/test/pip-audit-sample',
                name='pip-audit-sample',
                owner='test',
                status='cloned'
            )
            run = AnalysisRun.objects.create(repository=repo, status='running')

            findings = analyze_and_save_pip_audit(run, temp_dir)
            self.assertGreater(len(findings), 0)
            self.assertTrue(all(f.tool_name == 'pip-audit' for f in findings))
            self.assertTrue(Finding.objects.filter(run=run, tool_name='pip-audit').exists())

    @patch('core.views.clone_github_repo')
    @patch('core.views.analyze_and_save_pylint')
    @patch('core.views.analyze_and_save_bandit')
    @patch('core.views.analyze_and_save_radon')
    @patch('core.views.analyze_and_save_semgrep')
    @patch('core.views.analyze_and_save_pip_audit')
    @patch('core.views.cleanup_cloned_repo')
    def test_analyze_successful_flow(
        self, mock_cleanup, mock_pip, mock_semgrep, mock_radon, mock_bandit, mock_pylint, mock_clone
    ):
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
        mock_pylint.return_value = []
        mock_bandit.return_value = []
        mock_radon.return_value = []
        mock_semgrep.return_value = []
        mock_pip.return_value = []
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
        self.assertIn('analysis_run', response.data)
        summary = response.data['analysis_run']['summary_by_tool']
        self.assertIn('pylint', summary)
        self.assertIn('bandit', summary)
        self.assertIn('radon', summary)
        self.assertIn('semgrep', summary)
        self.assertIn('pip_audit', summary)

        # Confirm DB records
        self.assertTrue(Repository.objects.filter(github_url=self.sample_github_url).exists())
        repo = Repository.objects.get(github_url=self.sample_github_url)
        self.assertEqual(repo.status, 'cloned')
        self.assertTrue(AnalysisRun.objects.filter(repository=repo, status='completed').exists())
