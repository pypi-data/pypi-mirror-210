from typing import Optional, List
import pandas as pd
from github import Github, Repository, ContentFile, GithubException
from datagit.dataset_helpers import sort_dataframe_on_first_column_and_assert_is_unique


def store_metric(ghClient: Github, dataframe: pd.DataFrame, filepath: str, assignees: List[str] = [], branch: str = "production"):
    repo_orga, repo_name, file_path = filepath.split('/', 2)

    repo = ghClient.get_repo(repo_orga + "/" + repo_name)
    assert_branch_exist(repo, branch)
    contents = assert_file_exists(repo,file_path, ref=branch)
    dataframe = sort_dataframe_on_first_column_and_assert_is_unique(dataframe)
    if contents is None:
        create_file_with_pull_request(file_path, repo, branch, dataframe, assignees)
        pass
    else:
        new_contents = dataframe.to_csv()
        if contents.decoded_content.decode('utf-8') != new_contents:
            push_new_content_with_pull_request(
                file_path, repo, branch, contents, dataframe, assignees)
    pass


def assert_file_exists(repo: Repository.Repository, file_path: str, ref: str) -> Optional[ContentFile.ContentFile]:
    try:
        contents = repo.get_contents(file_path, ref=ref)
        assert not isinstance(contents, list), "pathfile returned multiple contents"
        return contents
    except GithubException as e:
        if e.status == 404:
            return None
        else:
            raise e


def push_new_content_with_pull_request(file_path: str, repo: Repository.Repository, branch: str, contents: ContentFile.ContentFile, dataframe: pd.DataFrame, assignees: List[str]):
    commit_message = "Update metric :" + file_path
    new_contents = dataframe.to_csv()
    repo.update_file(contents.path, commit_message,
                     new_contents, contents.sha, branch)

    create_pullrequest(repo, branch, assignees)



def create_file_with_pull_request(file_path: str, repo: Repository.Repository, branch: str, dataframe: pd.DataFrame, assignees: List[str]):
    encoded_content = dataframe.to_csv()
    repo.create_file(file_path, "New Metric "+file_path, encoded_content, branch)
    create_pullrequest(repo, branch, assignees)



def create_pullrequest(repo: Repository.Repository, branch: str, assignees: List[str]):
    try:
        pullrequest = repo.create_pull(title="New data", body="New data available",
                         head=branch, base=repo.default_branch)
        print("Pull request created: " + pullrequest.html_url)
        if len(assignees) > 0:
            existing_assignees = assert_assignees_exists(repo, assignees)
            pullrequest.add_to_assignees(*existing_assignees)
    except GithubException as e:
        if e.status == 422:
            print("Pull request already exists, skipping...")
        else:
            raise e
        

def assert_branch_exist(repo: Repository.Repository, branch_name: str) -> None:
    try:
        branch = repo.get_branch(branch_name)
    except:
        branch = None

    # If the branch doesn't exist, create it
    if not branch:
        print(f"Branch {branch_name} doesn't exist, creating it...")
        master_ref = repo.get_git_ref("heads/main")
        repo.create_git_ref(f"refs/heads/{branch_name}", master_ref.object.sha)

def assert_assignees_exists(repo: Repository.Repository, assignees: List[str]) -> List[str]:
    members = [collaborator.login for collaborator in repo.get_collaborators()]
    exising_assignees = []
    for assignee in assignees:
        if assignee not in members:
            print(f"Assignee {assignee} does not exist")
        else:
            exising_assignees.append(assignee)
    return exising_assignees