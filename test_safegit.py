import unittest
import tempfile
import os
from unittest.mock import patch
from git import Repo
from safegit import get_staged_files, parse_codeowners, main, files_not_in_codeowners
from typing import List

def make_codeowners_file(path: str, pattern: str, owners: List[str]) -> None:
    with open(path, 'w') as f:
        f.write(f"{pattern} {owners[0]}\n")


class TestSafegit(unittest.TestCase):

    def setUp(self):
        # Setup a temporary directory for the repo
        self.repo_dir = tempfile.TemporaryDirectory(dir=os.getcwd())
        self.repo = Repo.init(self.repo_dir.name)
                # Create an initial commit so 'HEAD' reference exists
        initial_file_path = os.path.join(self.repo_dir.name, 'initial.txt')
        with open(initial_file_path, 'w') as f:
            f.write("Initial content")
        self.repo.index.add([initial_file_path])
        self.repo.index.commit("Initial commit")

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

    def test_parse_codeowners_exists(self):
        pattern = "src/*"
        owners = ["@owner"]
        temp_codeowners_path = os.path.join(self.repo_dir.name, "CODEOWNERS")

        make_codeowners_file(temp_codeowners_path, pattern, owners)

        codeowners = parse_codeowners(temp_codeowners_path)
        self.assertIn(pattern, codeowners)
        self.assertEqual(codeowners[pattern], owners)

    def test_parse_codeowners_doesnt_exist(self):
        temp_codeowners_path = os.path.join(self.repo_dir.name, "CODEOWNERS")
        try:
            parse_codeowners(temp_codeowners_path)
        except FileNotFoundError as e:
            print("file not found error success:", e)

    def test_commit_fails_if_not_in_codeowners(self):
        # Create and stage a test file that is not listed in CODEOWNERS
        pattern = "src/*"
        owners = ["@owner"]
        temp_codeowners_path = os.path.join(self.repo_dir.name, "CODEOWNERS")
        make_codeowners_file(temp_codeowners_path, pattern, owners)

        # This fle is not in the codeowners path so this should fail
        test_file_path = os.path.join(self.repo_dir.name, 'test.py')
        with open(test_file_path, 'w') as f:
            f.write("Sample content")
        self.repo.index.add([test_file_path])

        # Check if there are any files not allowed
        not_allowed_files = files_not_in_codeowners(self.repo, self.repo_dir.name)

        # Assert that the commit is not allowed and the test file is in the not allowed list
        self.assertIn('test.py', not_allowed_files)

    def test_commit_succeeds_if_in_codeowners(self):
        pattern = "src/*"
        owners = ["@owner"]
        temp_codeowners_path = os.path.join(self.repo_dir.name, "CODEOWNERS")
        make_codeowners_file(temp_codeowners_path, pattern, owners)
        # Create and stage a test file that is listed in CODEOWNERS
        test_file_path = os.path.join(os.path.join(self.repo_dir.name, "src", 'test.txt'))
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
        with open(test_file_path, 'w') as f:
            f.write("Sample content")
        self.repo.index.add([test_file_path])

        # Check if there are any files not allowed
        not_allowed_files = files_not_in_codeowners(self.repo, self.repo_dir.name)

        # Assert that there are no files not allowed
        self.assertEqual(len(not_allowed_files), 0)

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
        with patch('sys.argv', ['safegit.py', 'commit message']):
            main()

        # Ensure the git commit command was called
        mock_run.assert_called_once_with(["git", "commit", "-m", "commit message"])

if __name__ == '__main__':
    unittest.main()
