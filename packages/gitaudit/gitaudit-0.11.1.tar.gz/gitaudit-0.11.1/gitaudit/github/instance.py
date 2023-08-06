"""Github communication instance"""

from typing import List
from datetime import datetime
import netrc
import base64

import requests
from pydantic import BaseModel

from .graphql_objects import PullRequest, Repository, Commit, Submodule


class FileAddition(BaseModel):
    """
    A representation of a file addition or modification for a git commit.

    Attributes:
        path (str): The path of the file in the git tree, using Unix-style path separators.
        contents (str): The base64-encoded contents of the file.
    """
    path: str
    contents: str

    @classmethod
    def from_plain_text(cls, path: str, contents: str):
        """
        Create a FileAddition instance from plain text.

        Args:
            path (str): The path of the file in the git tree, using Unix-style path separators.
            contents (str): The plain text contents of the file.

        Returns:
            FileAddition: The corresponding FileAddition instance with base64-encoded contents.
        """
        encoded_contents = base64.b64encode(
            contents.encode("utf-8")).decode("utf-8")
        return cls(path=path, contents=encoded_contents)


class FileDeletion(BaseModel):
    """
    A representation of a file deletion for a git commit.

    Attributes:
        path (str): The path of the file in the git tree, using Unix-style path separators.
    """
    path: str


def escape_characters_graphql(text: str) -> str:
    """Adds escapting characters to text to ensure that
    the graph-ql call is not invalid

    Args:
        text (str): The incoming text

    Returns:
        str: The adapted text
    """
    if not text:
        return text
    text = text.replace('"', r'\"')

    return text


class Github:
    """Instance communicating with Github"""

    def __init__(self, url: str = "https://api.github.com/graphql", token: str = ""):
        self.url = url

        if token:
            self.token = token
        else:
            self.token = netrc.netrc().authenticators(url)[2]

        self.session = requests.Session()
        self.session.headers = {
            "Authorization": f"token {self.token}",
            "Content-type": "application/json; charset=utf-8;",
            "Accept": "application/json;",
        }

    def _call(self, data: str):
        response = self.session.post(url=self.url, json={"query": data})
        return response.json()["data"]

    def query(self, querydata: str):
        """Call Github using a query

        Args:
            querydata (str): GraphQl Query

        Returns:
            dict: Json return object
        """
        return self._call(f"query {{{querydata}}}")

    def mutation(self, mutationdata):
        """Call Github using a query

        Args:
            mutationdata (str): GraphQl mutation

        Returns:
            dict: Json return object
        """
        return self._call(f"mutation {{{mutationdata}}}")

    def pull_request(self, owner: str, repo: str, number: int, querydata: str) -> PullRequest:
        """Queries Pull Request Information

        Args:
            owner (str): The owner of the repository
            repo (str): The repository name
            number (int): The pull request number
            query (str): The requested GraphQL query data

        Returns:
            PullRequest: The pull request object
        """
        res = self.query((
            f'repository(owner:"{owner}", name:"{repo}")'
            f'{{ pullRequest(number:{number}) {{ {querydata} }} }}'
        ))
        return PullRequest.parse_obj(res['repository']['pullRequest'])

    def search_pull_requests(self, search_query: str, querydata: str) -> List[PullRequest]:
        """Search Pull Requests on Github

        Args:
            search_query (str): The query to search for
            querydata (str): The pull request graphql query data

        Returns:
            List[PullRequest]: List of found pull requests
        """
        has_next_page = True
        end_cursor = None
        results = []

        while has_next_page:
            after_content = f'after:"{end_cursor}"' if end_cursor else ''
            res = self.query((
                'search('
                f'type: ISSUE, first: 100, query: "{search_query}",'
                f'{after_content}'
                '){'
                'issueCount '
                'pageInfo { endCursor hasNextPage } '
                f'nodes {{ ...on PullRequest {{ {querydata} }} }}'
                '}'
            ))

            total_count = res['search']['issueCount']
            assert total_count <= 1000, \
                (
                    f'Cannot retrieve more than 1000 pull request but "{total_count}" were found! '
                    'Please narrow down your search!'
                )

            results.extend(res['search']['nodes'])
            has_next_page = res['search']['pageInfo']['hasNextPage']
            end_cursor = res['search']['pageInfo']['endCursor']
        return list(map(PullRequest.parse_obj, results))

    def create_pull_request(
        self,
        repository_id: str,
        head_ref_name: str,
        base_ref_name: str,
        title: str,
        body: str = None,
        draft: bool = False,
        querydata: str = None
    ) -> PullRequest:
        """Creates a pull request in a repository

        Args:
            repository_id (str): Id of the repository
            head_ref_name (str): Name of the feature / bugfix / ... branch to be merged
            base_ref_name (str): Name of the branch being merged into
            title (str): Title of the pull request
            body (str, optional): Body of the pull request. Defaults to None.
            draft (bool, optional): Whether the pull request shall be created as draft.
                Defaults to false.
            querydata (str, optional): Data to be returend. Defaults to None.

        Returns:
            PullRequest: PullRequest object of the newly created pull request
        """
        title = escape_characters_graphql(title)
        body = escape_characters_graphql(body)

        body_content = f'body: "{body}",' if body else ''
        draft_content = f'draft: {draft},' if draft else ''
        query_data_content = f'pullRequest {{ {querydata} }}' if querydata else ''
        res = self.mutation((
            'createPullRequest(input: {'
            f'repositoryId: "{repository_id}",'
            f'headRefName: "{head_ref_name}",'
            f'baseRefName: "{base_ref_name}",'
            f'title: "{title}",'
            f'{body_content}'
            f'{draft_content}'
            '}){'
            'clientMutationId,'
            f'{query_data_content}'
            '}'
        ))

        if not querydata:
            return None

        if res['createPullRequest']['pullRequest']:
            return PullRequest.parse_obj(res['createPullRequest']['pullRequest'])

        return None

    def update_pull_request(
        self,
        pull_request_id: str,
        title: str = None,
        body: str = None,
        querydata: str = None,
    ) -> PullRequest:
        """Update Existing Pull Request

        Args:
            pull_request_id (str): The id of the pull request to be updated
            title (str, optional): If set update the title. Defaults to None.
            body (str, optional): If set update the body. Defaults to None.
            querydata (str, optional): Specify which data to be returned
                from the pull request. Defaults to None.

        Returns:
            PullRequest: _description_
        """
        title = escape_characters_graphql(title)
        body = escape_characters_graphql(body)

        body_content = f'body: "{body}",' if body else ''
        title_content = f'title: "{title}",' if title else ''
        query_data_content = f'pullRequest {{ {querydata} }}' if querydata else ''
        res = self.mutation((
            'updatePullRequest(input: {'
            f'pullRequestId: "{pull_request_id}",'
            f'{title_content}'
            f'{body_content}'
            '}){'
            'clientMutationId,'
            f'{query_data_content}'
            '}'
        ))

        if querydata:
            return PullRequest.parse_obj(res['updatePullRequest']['pullRequest'])

        return None

    def add_pull_request_review(
        self,
        pull_request_id: str,
        event: str = 'APPROVE',
        body: str = '',
    ) -> str:
        """Adds a review to a pull request

        Args:
            pull_request_id (str): The id of the pull request
            event (str): The type of review event. Default: 'APPROVE'.
            body (str): The body of the review. Default: ''.

        Returns:
            str: The id of the newly created pull request review
        """

        input_params = {
            "pullRequestId": pull_request_id,
            "event": event,
            "body": body
        }
        response = self.mutation((
            'addPullRequestReview(input: {'
            f'pullRequestId: "{input_params["pullRequestId"]}",'
            f'event: {input_params["event"]},'
            f'body: "{input_params["body"]}"'
            '}){'
            f'clientMutationId,'
            'pullRequestReview {'
            f'id'
            '}'
            '}'
        ))

        return response['addPullRequestReview']['pullRequestReview']['id']

    def dismiss_pull_request_review(self, review_id: str, message: str):
        """
        Dismiss an approved or rejected pull request review.

        Args:
            review_id (str): The Node ID of the pull request review to modify.
            message (str): The contents of the pull request review dismissal message.
        """
        self.mutation(
            (
                'dismissPullRequestReview(input: {'
                f'pullRequestReviewId: "{review_id}",'
                f'message: "{message}",'
                '}) {'
                'clientMutationId'
                '}'
            )
        )

    def add_comment(self, subject_id: str, body: str):
        """Adds a comment to an issue or pull request

        Args:
            subject_id (str): The id of the issue or pull request
            body (str): The body of the comment (can be markdown)
        """
        self.mutation((
            f'addComment(input: {{body: "{body}", subjectId: "{subject_id}"}})'
            '{ clientMutationId }'
        ))

    def get_file_content(self, owner: str, repo: str, ref: str, rel_file_path: str) -> str:
        """Returns the content of a file on GitHub as text

        Args:
            owner (str): Name of the repository owner
            repo (str): Name of the repository
            ref (str): The name of the commit/branch/tag
            rel_file_path (str): The relative file path in the repository

        Returns:
            str: The content of the file as text
        """

        query = (
            f'repository(owner:"{owner}", name:"{repo}") {{'
            f'object(expression: "{ref}:{rel_file_path}") {{'
            '... on Blob {'
            'text'
            '}'
            '}'
            '}'
        )
        response = self.query(query)
        file_content = response['repository']['object']['text']
        return file_content

    def get_repository(self, owner: str, repo: str, querydata: str):
        """Returns the repository object

        Args:
            owner (str): Name of the repository owner
            repo (str): Name of the repository
            querydata (str): Data to be queried from the repository (graph-ql)

        Returns:
            str: ID of the repository
        """
        res = self.query((
            f'repository(owner:"{owner}", name:"{repo}")'
            f'{{ {querydata} }}'
        ))
        return Repository.parse_obj(res['repository'])

    def get_commit_for_expression(self, owner: str, repo: str, expression: str, querydata: str):
        """Returns the commit object for the given expression

        Args:
            owner (str): Name of the repository owner
            repo (str): Name of the repository
            expression (str): Expression used to identify the commit, such as a branch name or a
                commit SHA
            querydata (str): Data to be queried from the commit object (GraphQL)

        Returns:
            Commit: An instance of the Commit class containing the commit data as specified in the
                querydata parameter
        """

        query = (
            f'repository(owner:"{owner}", name:"{repo}") {{'
            f'commit: object(expression: "{expression}") {{'
            f"... on Commit {{{querydata}}}"
            "}"
        )
        response = self.query(query)
        commit = response['repository']['commit']
        return Commit.parse_obj(commit)

    def get_first_commit_before_date(
        self,
        owner: str,
        repo: str,
        ref: str,
        commit_date_time: datetime,
        querydata: str,
    ) -> Commit:
        """Returns the first commit object before a given date for a ref in a repository.

        Args:
            owner (str): Name of the repository owner.
            repo (str): Name of the repository.
            ref (str): The reference (e.g., branch) in the repository.
            commit_date_time (datetime): The date and time to find the commit before.
            querydata (str): Data to be queried from the commit object (GraphQL).

        Returns:
            Commit: An instance of the Commit class containing the commit data as specified in the
                querydata parameter if a commit is found before the specified date and time, or
                None if no commit is found.
        """
        formatted_date = commit_date_time.isoformat()

        query = (
            f'repository(owner:"{owner}", name:"{repo}") {{'
            f'ref(qualifiedName: "{ref}") {{'
            f'target {{'
            '... on Commit {'
            f'history(first: 1, until: "{formatted_date}") {{'
            'nodes {'
            f'{querydata}'
            '}'
            '}'
            '}'
            '}'
            '}'
            '}'
        )
        response = self.query(query)
        history_nodes = response['repository']['ref']['target']['history']

        if history_nodes:
            return Commit.parse_obj(history_nodes['nodes'][0])

        return None

    def get_first_sha_before_date(
        self,
        owner: str,
        repo: str,
        ref: str,
        commit_date_time: datetime,
    ) -> str:
        """Returns the first commit SHA before a given date for a ref in a repository.

        Args:
            owner (str): Name of the repository owner.
            repo (str): Name of the repository.
            ref (str): The reference (e.g., branch) in the repository.
            commit_date_time (datetime): The date and time to find the commit before.

        Returns:
            str: The commit SHA of the first commit before the specified date and time, or None if
                no commit is found.
        """
        commit = self.get_first_commit_before_date(
            owner, repo, ref, commit_date_time, 'oid')

        if commit:
            return commit.oid

        return None

    def get_label_id(self, owner: str, repo: str, label_name: str) -> str:
        """
        Get the ID of a label by its name in the specified repository.

        Args:
            owner (str): Name of the repository owner.
            repo (str): Name of the repository.
            label_name (str): Name of the label.

        Returns:
            str: The ID of the label with the specified name, or None if not found.
        """
        query = (
            f'repository(owner:"{owner}", name:"{repo}") {{'
            f'label(name: "{label_name}") {{'
            'id'
            '}'
            '}'
        )

        response = self.query(query)
        label = response['repository']['label']

        if label:
            return label['id']
        else:
            return None

    def add_label_to_labelable(self, labelable_id: str, label_ids: List[str]):
        """
        Add one or multiple labels to a labelable object, such as an issue or pull request.

        Args:
            labelable_id (str): The ID of the labelable object to which the labels should be added.
            label_ids (List[str]): A list of label IDs to add to the labelable object.
        """
        if not label_ids:
            return

        label_ids_string = ",".join(
            [f'"{label_id}"' for label_id in label_ids])
        mutation = (
            'addLabelsToLabelable(input: {'
            f'labelableId: "{labelable_id}",'
            f'labelIds: [{label_ids_string}]'
            '}) {'
            'clientMutationId'
            '}'
        )
        self.mutation(mutation)

    def remove_label_from_labelable(self, labelable_id: str, label_ids: List[str]):
        """
        Remove labels from a labelable object (issue or pull request) based on their IDs.

        Args:
            labelable_id (str): The ID of the labelable object (issue or pull request).
            label_ids (List[str]): A list of label IDs to be removed.
        """

        label_ids_string = ",".join(
            [f'"{label_id}"' for label_id in label_ids])

        mutation = (
            f'removeLabelsFromLabelable(input: {{'
            f'labelableId: "{labelable_id}",'
            f'labelIds: [{label_ids_string}]'
            '}) {'
            'clientMutationId'
            '}'
        )
        self.mutation(mutation)

    def create_branch(self, owner: str, repo: str, base_oid: str, ref_name: str):
        """
        Create a new branch in the specified repository.

        Args:
            owner (str): Name of the repository owner.
            repo (str): Name of the repository.
            base_oid (str): The commit OID that the new branch should point to.
            ref_name (str): The name of the new branch.
        """
        repo_id = self.get_repository(owner, repo, 'id').id
        mutation = (
            'createRef(input: {'
            f'repositoryId: "{repo_id}",'
            f'name: "refs/heads/{ref_name}",'
            f'oid: "{base_oid}"'
            '}) {'
            'clientMutationId'
            '}'
        )
        self.mutation(mutation)

    def create_tag(self, owner: str, repo: str, base_oid: str, tag_name: str):
        """
        Create a new tag in the specified repository.

        Args:
            owner (str): Name of the repository owner.
            repo (str): Name of the repository.
            base_oid (str): The commit OID that the new tag should point to.
            tag_name (str): The name of the new tag.
        """

        repo_id = self.get_repository(owner, repo, 'id').id
        mutation = (
            'createRef(input: {'
            f'repositoryId: "{repo_id}",'
            f'name: "refs/tags/{tag_name}",'
            f'oid: "{base_oid}"'
            '}) {'
            'clientMutationId'
            '}'
        )
        self.mutation(mutation)

    def create_commit_on_branch(
        self,
        owner: str,
        repo: str,
        ref_name: str,
        head_sha: str,
        message_headline: str,
        message_body: str = None,
        additions: List[FileAddition] = None,
        deletions: List[FileDeletion] = None,
        querydata: str = None,
    ) -> Commit:
        """
        Create a commit on a specified branch with the provided file additions and deletions, and
        return a Commit object with the specified query data.

        Args:
            owner (str): Name of the repository owner.
            repo (str): Name of the repository.
            ref_name (str): The name of the branch.
            head_sha (str): The SHA of the head commit.
            message_headline (str): The headline of the commit message.
            message_body (str, optional): The body of the commit message. Defaults to None.
            additions (List[FileAddition], optional): A list of FileAddition instances representing
                files to add or modify. Defaults to an empty list.
            deletions (List[FileDeletion], optional): A list of FileDeletion instances representing
                files to delete. Defaults to an empty list.
            querydata (str, optional): The GraphQL query string to fetch additional commit data.
                Defaults to None.

        Returns:
            Commit: A Commit object containing the requested data, or None if the commit creation
                failed.

        Usage:
            # Instantiate the FileAddition and FileDeletion classes
            addition = FileAddition.from_plain_text("path/to/file.txt", "File contents")
            deletion = FileDeletion(path="path/to/file_to_delete.txt")

            # Call the create_commit_on_branch method with the required arguments and query data
            commit = create_commit_on_branch(
                owner="owner_name",
                repo="repo_name",
                ref_name="branch_name",
                head_sha="head_commit_sha",
                message_headline="Commit headline",
                additions=[addition],
                deletions=[deletion],
                querydata="oid, messageHeadline, author {name, email, date}"
            )
        """
        if not additions:
            additions = []
        if not deletions:
            deletions = []

        additions_input = [
            f'{{path: "{addition.path}", contents: "{addition.contents}"}}'
            for addition in additions
        ]
        additions_string = ','.join(additions_input)

        deletions_input = [
            f'{{path: "{deletion.path}"}}' for deletion in deletions]
        deletions_string = ','.join(deletions_input)

        message_body_text = f'body: "{message_body}",' if message_body else ''
        commit_query_data_text = f'commit {{{querydata}}}' if querydata else ''

        mutation = (
            'createCommitOnBranch(input: {'
            'branch:{'
            f'repositoryNameWithOwner: "{owner}/{repo}",'
            f'branchName: "{ref_name}",'
            '}'
            f'expectedHeadOid: "{head_sha}",'
            "message:{"
            f'headline: "{message_headline}",'
            f'{message_body_text}'
            '},'
            'fileChanges:{'
            f'additions: [{additions_string}],'
            f'deletions: [{deletions_string}]'
            '}'
            '}) {'
            f'clientMutationId,{commit_query_data_text}'
            '}'
        )

        res = self.mutation(mutation)

        if 'commit' in res['createCommitOnBranch']:
            return Commit.parse_obj(res['createCommitOnBranch']['commit'])

        return None

    def get_submodules(
        self,
        owner: str,
        repo: str,
        ref: str,
        querydata: str = None,
    ) -> List[Submodule]:
        """
        Get the submodule information for a given repository and ref.

        Args:
            owner (str): Name of the repository owner.
            repo (str): Name of the repository.
            ref (str): The reference (branch or tag) to get the submodule information from.
            querydata (str): Additional fields to fetch for each submodule.

        Returns:
            List[Submodule]: A list of Submodule objects containing the requested information.
        """
        if querydata is None:
            querydata = "name subprojectCommitOid"

        submodules = []
        has_next_page = True
        end_cursor = None

        while has_next_page:
            after_argument = f', after: "{end_cursor}"' if end_cursor else ""
            query = (
                f'repository(owner: "{owner}", name: "{repo}") {{'
                f'object(expression: "{ref}") {{'
                '... on Commit {'
                f'submodules (first: 100{after_argument}) {{'
                'pageInfo {endCursor hasNextPage},'
                'nodes {'
                f'{querydata}'
                '}'
                '}'
                '}'
                '}'
                '}'
            )

            response = self.query(query)

            if 'repository' in response and 'object' in response['repository']:
                submodules_nodes = response['repository']['object']['submodules']['nodes']
                submodules.extend(map(Submodule.parse_obj, submodules_nodes))

                page_info = response['repository']['object']['submodules']['pageInfo']
                has_next_page = page_info['hasNextPage']
                end_cursor = page_info['endCursor']

        return submodules

    # def create_commit_on_branch(self, owner, repo, ref_name, head_sha, message_headline,
    # message_body, additions, deletions):
    #     raise NotImplementedError

    # def unsure___(self):
    #     # get_file_commit_history
    #     # get_file_pull_request_history
    #     # get_submodules
    #     raise NotImplementedError
