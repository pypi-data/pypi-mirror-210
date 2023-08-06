import os.path
import unittest
from pyutils.io.git_repo import GitRepo
import uuid
import shutil


class TestGitRepo(unittest.TestCase):

    def setUp(self):
        uid = str(uuid.uuid4())
        self.repo_local_dir = os.path.join('/tmp', uid)
        print(f'set up tmp dir {self.repo_local_dir}')
        self.git_repo = GitRepo(name="test", url="https://github.com/TaoYang526/test.git")
        self.git_repo.init(self.repo_local_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.repo_local_dir)
        print(f'cleaned up tmp dir {self.repo_local_dir}')

    def test_manage_tag(self):
        branch_name = 'release-0.1'
        fetched_branch = self.git_repo.get_remote_branch(branch_name)
        if fetched_branch:
            # remove test branch if existing
            print(f'branch {branch_name} is existing, trigger removing it')
            removed_branch = self.git_repo.remove_remote_branch(branch_name)
            self.assertIsNotNone(removed_branch, "failed to remove branch, removed_branch={}".format(removed_branch))
            fetched_branch = self.git_repo.get_remote_branch(branch_name)
            self.assertIsNone(fetched_branch, "failed to remove branch, fetched_branch={}".format(fetched_branch))
        print(f'create new branch {branch_name} ...')
        # create new branch
        self.git_repo.create_remote_branch(branch_name, 'master')
        # check new branch created
        fetched_new_branch = self.git_repo.get_remote_branch(branch_name)
        self.assertIsNotNone(fetched_new_branch, "failed to fetch new created branch")

        tag_name = 'v0.1.1'
        tag_ref = self.git_repo.get_tag_reference(tag_name)
        if tag_ref:
            # remove test tag if existing
            print(f'tag {tag_name} is existing, trigger removing it')
            self.git_repo.remove_remote_tag(tag_name)
            tag_ref = self.git_repo.get_tag_reference(tag_name)
            self.assertIsNone(tag_ref, f"failed to remove tag, fetched tag={tag_ref}")
        # create tag
        self.git_repo.create_remote_tag(branch_name, tag_name)
        # check created
        tag_ref = self.git_repo.get_tag_reference(tag_name)
        self.assertIsNotNone(tag_ref, f"expected to get tag {tag_name}")
        # remove tag
        self.git_repo.remove_remote_tag(tag_name)
        tag_ref = self.git_repo.get_tag_reference(tag_name)
        self.assertIsNone(tag_ref, f"expected to not get tag {tag_name}")

        # remove branch
        self.git_repo.remove_remote_branch(branch_name)


if __name__ == "__main__":
    unittest.main()
