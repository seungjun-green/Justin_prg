from git import Repo
import git


def git_push():
    try:
        repo = Repo(".")
        repo.git.add(update=True)
        repo.index.commit("updated error files")
        origin = repo.remote(name='origin')
        origin.push()
    except git.GitError as e:
        print(f'error: {e}')


git_push()
