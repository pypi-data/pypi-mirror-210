"""Calculate Branch Trees
"""

from __future__ import annotations
import itertools

from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel, Field
from gitaudit.git.change_log_entry import ChangeLogEntry


class Segment(BaseModel):
    """Class for Storing a Branch Segment
    """
    entries: List[ChangeLogEntry]
    children: Optional[Dict[str, Segment]] = Field(default_factory=dict)
    ref_name: Optional[str]

    @property
    def length(self):
        """Returns the number of entries in this segment
        """
        return len(self.entries)

    @property
    def end_sha(self):
        """Returns the sha of the last entry in this segment
        """
        return self.entries[0].sha

    @property
    def end_entry(self):
        """Returns the last entry in this segment
        """
        return self.entries[0]

    @property
    def start_sha(self):
        """Returns the sha of the first entry in this segment
        """
        return self.entries[-1].sha

    @property
    def start_entry(self):
        """Returns the first entry in this segment
        """
        return self.entries[-1]

    @property
    def shas(self):
        """Returns all first parent shas in this segment as a list
        """
        return list(map(lambda x: x.sha, self.entries))


class Tree(BaseModel):
    """Branching tree out of segments
    """
    root: Segment = None

    def append_log(self, hier_log: List[ChangeLogEntry], ref_name: str):
        """Append a new hierarchy log history to the tre

        Args:
            hier_log (List[ChangeLogEntry]): to be appended log
            ref_name (str): name of the branch / ref
        """
        new_segment = Segment(
            entries=hier_log,
            ref_name=ref_name,
        )

        if not self.root:
            self.root = new_segment
        else:
            self._merge_segment(new_segment)

    def _merge_segment(self, new_segment: Segment):
        index = -1

        assert self.root.entries[index].sha == new_segment.entries[index].sha, \
            "Initial shas do not match which is a prerequisite!"

        parent_segment = None
        current_segment = self.root

        while new_segment:

            while len(current_segment.entries) > (-index-1) \
                    and len(new_segment.entries) > (-index-1) \
                    and current_segment.entries[index].sha == new_segment.entries[index].sha:
                index -= 1

            if len(new_segment.entries) <= (-index-1):
                # The new segment does not exceed the exiting one
                # --> no action necessary
                new_segment = None
            elif len(current_segment.entries) <= (-index-1):
                # the new segment exceeds the existing one
                # --> replace the existing one with the new one
                if current_segment.children:
                    # replace current segment
                    new_segment = Segment(
                        entries=new_segment.entries[:(index+1)],
                        ref_name=new_segment.ref_name,
                    )

                    if new_segment.start_sha in current_segment.children:
                        parent_segment = current_segment
                        current_segment = current_segment.children[new_segment.start_sha]
                        index = -1
                    else:
                        current_segment.children[new_segment.start_sha] = new_segment
                        new_segment = None
                else:
                    if parent_segment:
                        parent_segment.children[new_segment.start_sha] = new_segment
                        new_segment = None
                    else:
                        self.root = new_segment
                        new_segment = None
            else:
                current_segment_pre = Segment(
                    entries=current_segment.entries[(index+1):],
                    ref_name=current_segment.ref_name,
                )
                current_segment_post = Segment(
                    entries=current_segment.entries[:(index+1)],
                    ref_name=current_segment.ref_name,
                    children=current_segment.children,
                )
                new_segment_post = Segment(
                    entries=new_segment.entries[:(index+1)],
                    ref_name=new_segment.ref_name,
                )

                current_segment_pre.children[current_segment_post.start_sha] = current_segment_post
                current_segment_pre.children[new_segment_post.start_sha] = new_segment_post

                if parent_segment:
                    parent_segment.children[current_segment_pre.start_sha] = current_segment_pre
                    new_segment = None
                else:
                    self.root = current_segment_pre
                    new_segment = None

    def iter_segments(self):
        """Iterate Tree Segments

        Yields:
            Segment: Iterated Tree Segment
        """
        queue = [self.root]

        while queue:
            seg = queue.pop(0)
            yield seg
            queue.extend(seg.children.values())

    def flatten_segments(self) -> List[Segment]:
        """Return all child segments of root as a flattened list

        Returns:
            List[Segment]: Flattened segments
        """
        return list(self.iter_segments())

    def end_segments(self) -> List[Segment]:
        """Return a list of end segments

        Returns:
            List[Segment]: end segments
        """
        return list(filter(lambda x: not x.children, self.flatten_segments()))

    def get_segment_trace(self, ref_name: str) -> List[Segment]:
        """Returns the segment trace from a branch name until the root segment (also including it)

        Args:
            ref_name (str): The name of the end segment (branch name)

        Returns:
            List[Segment]: List of segments from end segment (first) to root (last)
        """
        end_sha_segments_map = {x.end_sha: x for x in self.flatten_segments()}
        ref_name_end_segments_map = {
            x.ref_name: x for x in self.end_segments()}

        assert ref_name in ref_name_end_segments_map, \
            f'Branch name "{ref_name}" is not used by any end segment!'

        segments = [ref_name_end_segments_map[ref_name]]

        while segments[-1].start_entry.parent_shas:
            fp_sha = segments[-1].start_entry.parent_shas[0]
            segments.append(end_sha_segments_map[fp_sha])

        return segments

    def get_segments_trace_until_merge_base(
        self,
        head_ref_name: str,
        base_ref_name: str,
    ) -> Tuple[List[Segment], List[Segment]]:
        """Gets the trace of two end refs (head and base) and returns the segments until the
        first combined segments (thus extracting the individual head and base segment traces).

        Args:
            head_ref_name (str): The head branch name
            base_ref_name (str): The base branch name

        Returns:
            Tuple[List[Segment], List[Segment]]: The individual segment lists (head, base)
        """
        head_segments = self.get_segment_trace(head_ref_name)
        base_segments = self.get_segment_trace(base_ref_name)

        index = -1

        while head_segments[index].end_sha == base_segments[index].end_sha:
            index -= 1

        index += 1

        return head_segments[:index], base_segments[:index]

    def get_entries_until_merge_base(
        self,
        head_ref_name: str,
        base_ref_name: str,
    ) -> Tuple[List[ChangeLogEntry], List[ChangeLogEntry]]:
        """Gets the change log of both branches until the
        first combined segments (thus extracting the individual head and base changelogs).

        Args:
            head_ref_name (str): The head branch name
            base_ref_name (str): The base branch name

        Returns:
            Tuple[List[ChangeLogEntry], List[ChangeLogEntry]]: The individual changelogs
                (head, base)
        """
        head_segments, base_segments = self.get_segments_trace_until_merge_base(
            head_ref_name,
            base_ref_name,
        )

        head_entries_arr = map(lambda x: x.entries, head_segments)
        base_entries_arr = map(lambda x: x.entries, base_segments)

        head_entries = list(itertools.chain.from_iterable(head_entries_arr))
        base_entries = list(itertools.chain.from_iterable(base_entries_arr))

        return head_entries, base_entries
