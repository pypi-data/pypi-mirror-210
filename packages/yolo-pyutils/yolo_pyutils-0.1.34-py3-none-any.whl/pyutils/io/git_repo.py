import os
import git


class GitRepo:

    def __init__(self, name, url, remote_conn_name='origin'):
        self.name = name
        self.url = url
        self.remote_conn_name = remote_conn_name
        self.repo = None

    def init(self, repo_local_dir, auto_clone=True):
        if os.path.exists(repo_local_dir):
            # reuse if already have directory
            repo = git.Repo(repo_local_dir)
        elif auto_clone:
            repo = git.Repo.clone_from(url=self.url, to_path=repo_local_dir)
        else:
            raise RuntimeError("local directory {} not found for repo {}".format(repo_local_dir, self.name))
        self.repo = repo

    def get_last_commit(self):
        if not self.repo:
            raise RuntimeError("repo {} haven't been initialized".format(self.name))
        commits = list(self.repo.iter_commits())
        if len(commits) > 0:
            last_commit = commits[0]
            return {"datetime": last_commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "committer": last_commit.committer,
                    "message": last_commit.message,
                    "hexsha": last_commit.hexsha}

    def get_changed_files(self, rev=None):
        return [item.a_path for item in self.repo.index.diff(rev)]

    def undo_changed_file(self, file_path):
        self.repo.index.checkout(file_path, force=True)

    def get_remote(self, refresh=False):
        # get remote connection, raise IndexError: No item found with id '...' if failed
        remote = self.repo.remotes[self.remote_conn_name]
        if refresh:
            remote.fetch()
        return remote

    def get_remote_branch(self, branch_name):
        remote = self.get_remote(refresh=True)
        found_refs = list(filter(lambda x: x.name == '{}/{}'.format(self.remote_conn_name, branch_name), remote.refs))
        if len(found_refs) > 0:
            return found_refs[0]

    def remove_remote_branch(self, branch_name):
        remote_branch = self.get_remote_branch(branch_name)
        if remote_branch:
            self.get_remote().push(refspec=(":%s" % remote_branch.remote_head))
            return remote_branch

    def create_remote_branch(self, new_branch_name, base_branch_name):
        # create local branch from remote base branch
        base_branch = self.get_remote_branch(base_branch_name)
        head = self.repo.create_head(new_branch_name, base_branch)
        self.get_remote().push(head)

    def checkout_remote_branch(self, branch_name):
        ref = self.get_remote_branch(branch_name)
        if not ref:
            raise RuntimeError("remote branch {} not found".format(branch_name))
        if branch_name in self.repo.heads:
            # checkout latest commit from remote
            self.repo.heads[branch_name].set_tracking_branch(ref).checkout()
        else:
            # create head from remote if not present
            self.repo.create_head(branch_name, ref).set_tracking_branch(ref).checkout()
        self.get_remote().pull()

    def checkout_tag(self, tag_name):
        self.repo.git.checkout(tag_name)

    def create_remote_tag(self, branch_name, tag_name):
        tag = self.repo.create_tag(tag_name, ref=self.repo.heads[branch_name])
        self.get_remote().push(tag.path)

    def get_tag_reference(self, tag_name):
        # get remote connection, raise IndexError: No item found with id '...' if failed
        for tag_ref in self.repo.tags:
            if tag_ref.name == tag_name:
                return tag_ref
        return None

    def remove_remote_tag(self, tag_name):
        tag_ref = self.get_tag_reference(tag_name)
        if tag_ref:
            self.repo.delete_tag(tag_ref)
            self.get_remote().push(f':{tag_ref.path}')
        return tag_ref
