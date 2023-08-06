"""Change Log Entry
"""

from __future__ import annotations

from typing import List, Optional, Dict
from datetime import datetime
import re
import pytz
from pydantic import BaseModel, Field


def extract_line_content(line, id_character):
    """Extracts the line content of git log with the format
    "<character>:[<content>]"

    Args:
        line (str): Line to be extracted from
        id_character (str): Single character for controll
            the extraction

    Returns:
        str: Returns the extracted content
    """
    matches = re.findall(
        r'(?<=^' + id_character + r':\[).*?(?=\]$)',
        line,
    )
    assert len(matches) == 1
    return matches[0]


def split_and_strip(text, splitby=','):
    """Split by character and strip each list element

    Args:
        text (str): Text to be split
        splitby (str, optional): character to be split by. Defaults to ','.

    Returns:
        List[str]: List of splitted and stripped strings
    """
    return list(filter(
        lambda x: x,
        map(
            lambda x: x.strip(),
            text.split(splitby),
        )
    ))


def extract_tags_refs(tag_line):
    """Extracts tags and refs from log line

    Args:
        tag_line (str): Line containing the tag and ref tags

    Returns:
        Tuple[List[str], List[str]]: List of tags and refs
    """
    line_content = extract_line_content(tag_line, 'T')
    refs = split_and_strip(line_content)
    tags = list(filter(lambda x: x.startswith('tag: '), refs))
    tags = list(map(lambda x: x[5:], tags))
    refs = list(filter(lambda x: not x.startswith('tag: '), refs))
    refs = list(map(lambda x: x.replace('HEAD -> ', ''), refs))

    return tags, refs


def extract_additions_deletions(numstat_text):
    """Extract additions and deletions from numstat text

    Args:
        numstat_text (str): Multiline text block containing the git
            log num stat information

    Returns:
        List[Dict[str, any]]: List of dictionaries
    """
    content = re.findall(r'(\d+)\t(\d+)\t(.+)', numstat_text)
    return list(map(lambda x: {
        "additions": int(x[0]),
        "deletions": int(x[1]),
        "path": x[2],
    }, content))


def extract_submodule_update(numstat_text):
    """Extract submodule updates from numstat text

    Args:
        numstat_text (str): Multiline text block containing the git
            log num stat and patch information

    Returns:
        List[Dict[str, any]]: List of dictionaries
    """
    content = re.findall(
        r'Submodule\s*(.*?)\s*([a-f0-9]+)\.{3}([a-f0-9]+)',
        numstat_text,
    )
    submodule_list = list(map(lambda x: {
        "submodule_name": x[0],
        "from_sha": x[1],
        "to_sha": x[2],
    }, content))
    return {x['submodule_name']: x for x in submodule_list}


class FileAdditionsDeletions(BaseModel):
    """Dataclass for storing file additions and deletions
    """
    path: str
    additions: int
    deletions: int


class SubmoduleUpdate(BaseModel):
    """Dataclass for storing submodule updates
    """
    submodule_name: str
    from_sha: str
    to_sha: str
    entries: Optional[List[ChangeLogEntry]] = Field(default_factory=list)


class ChangeLogEntry(BaseModel):
    """Dataclass for storing change log data
    """
    sha: str
    url: Optional[str]
    parent_shas: Optional[List[str]] = Field(default_factory=list)
    cherry_pick_sha: Optional[str]
    other_parents: Optional[List[List[ChangeLogEntry]]] \
        = Field(default_factory=list)
    branch_offs: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)
    refs: Optional[List[str]] = Field(default_factory=list)
    subject: Optional[str]
    commit_date: Optional[datetime]
    author_name: Optional[str]
    author_mail: Optional[str]
    body: Optional[str] = ''
    numstat: Optional[
        List[FileAdditionsDeletions]
    ] = Field(default_factory=list)
    submodule_updates: Optional[Dict[str, SubmoduleUpdate]] = Field(
        default_factory=dict)

    @ property
    def sorted_numstat(self):
        """Path sorted File NumStat

        Returns:
            List[FileAdditionsDeletions]: Sorted numstat
        """
        return sorted(self.numstat, key=lambda x: x.path)

    def copy_without_hierarchy(self):
        """Copy Itself without hierarchy elements
        (branch_offs, other_parents)

        Returns:
            ChangeLogEntry: the copied entry
        """
        copy_dict = self.dict(exclude={'branch_offs', 'other_parents'})
        return ChangeLogEntry.parse_obj(copy_dict)

    def copy_as_parentlog_entry(self) -> ChangeLogEntry:
        """Creates a copy of itself but only containing the parent log information

        Returns:
            ChangeLogEntry: Copy with parent log information
        """
        return ChangeLogEntry(
            sha=self.sha,
            parent_shas=self.parent_shas,
            commit_date=self.commit_date,
        )

    def to_save_dict(self) -> Dict[str, any]:
        """Saves content to dictionary

        Returns:
            Dict[str, any]: dict content of entry
        """
        local_exclude = {'other_parents'}
        local_dict = self.dict(
            exclude=local_exclude,
            exclude_defaults=True,
            exclude_unset=True,
        )

        other_parents_dict = []

        for other_p in self.other_parents:
            other_parents_dict.append(list(map(
                lambda x: x.to_save_dict(),
                other_p
            )))

        if other_parents_dict:
            local_dict['other_parents'] = other_parents_dict
        return local_dict

    @ classmethod
    def from_log_text(cls, log_text, url_provider=None, instance_class=None):
        """Create ChangeLogEntry from logging text

        Args:
            log_text (str): Logging text

        Returns:
            ChangeLogEntry: Change log entry dataclass
        """
        item_text, rest_text = log_text.split('#SB#')
        body_text, numstat_text = rest_text.split('#EB#')

        cherry_picked_commits = re.findall(
            r"(?<=\(cherry\spicked\sfrom\scommit\s)[a-f0-9]+(?=\))",
            body_text,
        )

        (
            sha_line,
            parents_line,
            tags_line,
            subject_line,
            date_line,
            author_name_line,
            author_mail_line,
        ) = item_text.strip().split('\n')

        tags, refs = extract_tags_refs(tags_line)
        sha = extract_line_content(sha_line, 'H')

        if not instance_class:
            instance_class = ChangeLogEntry

        return instance_class(
            sha=sha,
            url=url_provider(sha) if url_provider else None,
            parent_shas=split_and_strip(
                extract_line_content(parents_line, 'P'), splitby=' '),
            tags=tags,
            refs=refs,
            subject=extract_line_content(subject_line, 'S'),
            commit_date=datetime.fromisoformat(
                extract_line_content(date_line, 'D')).astimezone(pytz.utc),
            author_name=extract_line_content(author_name_line, 'A'),
            author_mail=extract_line_content(author_mail_line, 'M'),
            body=body_text.strip(),
            cherry_pick_sha=cherry_picked_commits[0] if len(
                cherry_picked_commits) == 1 else None,
            numstat=extract_additions_deletions(numstat_text),
            submodule_updates=extract_submodule_update(numstat_text),
        )

    @ classmethod
    def from_head_log_text(cls, log_text, instance_class=None):
        """Create ChangeLogEntry from logging text

        Args:
            log_text (str): Logging text

        Returns:
            ChangeLogEntry: Change log entry dataclass
        """
        res = re.findall(
            r'([a-f0-9]+)\[(?:([a-f0-9\s]+))?\](?:\((.*?)\))?', log_text)

        if not instance_class:
            instance_class = ChangeLogEntry

        return instance_class(
            sha=res[0][0],
            parent_shas=res[0][1].split(' ') if res[0][1] else [],
            commit_date=datetime.fromisoformat(
                res[0][2]) if res[0][2] else None
        )

    @ classmethod
    def list_from_objects(cls, items: List[dict], instance_class=None):
        """Given a list of dict objects create a list of ChangeLogEntries

        Args:
            items (List[dict]): List of dict objects

        Returns:
            List[ChangeLogEntry]: List of ChangeLogEntries
        """

        if not instance_class:
            instance_class = ChangeLogEntry

        return [instance_class.parse_obj(x) for x in items]
