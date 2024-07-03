import unittest
import tempfile
import os
from unittest.mock import patch
from git import Repo
from safegit import get_staged_files, parse_codeowners, is_file_owned, main

class TestSafegit(unittest.TestCase):

    def setUp(self):
        # Setup a temporary directory for the repo
        self.repo_dir = tempfile.TemporaryDirectory()
        self.repo = Repo.init(self.repo_dir.name)

    def tearDown(self):
        # Cleanup the temporary directory
        self.repo_dir.cleanup()

    def test_get_staged_files(self):
        # Create a temporary file and add it to the repo
        test_file_path = os.path.join(self.repo_dir.name, 'test.txt')
        with open(test_file_path, 'w') as f:
            f.write("Sample content")

        self.repo.index.add([test_file_path])
        staged_files = get_staged_files(self.repo)
        self.assertIn('test.txt', staged_files)

    @patch('safegit.CODEOWNERS_PATH', new_callable=lambda: tempfile.mkstemp()[1])
    def test_parse_codeowners(self, mock_codeowners_path):
        pattern = "src/*"
        owners = ["@owner"]
        with open(mock_codeowners_path, 'w') as f:
            f.write(f"{pattern} {owners[0]}\n")

        codeowners = parse_codeowners(mock_codeowners_path)
        self.assertIn(pattern, codeowners)
        self.assertEqual(codeowners[pattern], owners)

    def test_is_file_owned(self):
        codeowners = {'src/': ['@owner']}
        self.assertTrue(is_file_owned('src/main.py', codeowners))
        self.assertFalse(is_file_owned('docs/readme.md', codeowners))

    @patch('safegit.Repo')
    @patch('safegit.parse_codeowners')
    @patch('safegit.get_staged_files')
    @patch('safegit.subprocess.run')
    def test_main(self, mock_run, mock_get_staged_files, mock_parse_codeowners, mock_repo):
        # Set up the mocks
        mock_repo.return_value = self.repo
        mock_get_staged_files.return_value = ['src/main.py']
        mock_parse_codeowners.return_value = {'src/': ['@owner']}
        mock_run.return_value = None

        # Call the main function with a commit message
        with patch('sys.argv', ['git_commit_wrapper.py', 'commit message']):
            main()

        # Ensure the git commit command was called
        mock_run.assert_called_once_with(["git", "commit", "-m", "commit message"])

if __name__ == '__main__':
    unittest.main()
