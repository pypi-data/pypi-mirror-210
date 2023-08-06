# Copyright (C) 2020  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from .base import GIT_RECEIVE_USER, PROJECT, PagureMessage, SCHEMA_URL


class GitMessage(PagureMessage):
    """
    Used when git events generate Fedora messages.
    """

    def _name_if_namespace(self, namespace):
        if self.body["repo"]["namespace"] == namespace:
            return [self.body["repo"]["name"]]
        return []

    @property
    def packages(self):
        return self._name_if_namespace("rpms")

    @property
    def containers(self):
        return self._name_if_namespace("containers")

    @property
    def modules(self):
        return self._name_if_namespace("modules")

    @property
    def flatpaks(self):
        return self._name_if_namespace("flatpaks")


class GitBranchCreationV1(GitMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.git.branch.creation"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "repo": PROJECT,
            "tag": {"type": "string"},
            "rev": {"type": "string"},
            "authors": {"type": "array", "items": GIT_RECEIVE_USER},
        },
        "required": ["agent", "repo", "branch", "rev", "authors"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Git branch: {branch} created\nBy: {agent_name}".format(
            branch=self.body["branch"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} created the branch {branch} on {name}".format(
            agent_name=self.agent_name,
            name=self.body["repo"]["fullname"],
            branch=self.body["branch"],
        )

    @property
    def url(self):
        base_url = self.body["repo"]["full_url"]

        item = self.body["branch"]
        if "refs/heads/" in item:
            item = item.replace("refs/heads/", "")

        tmpl = "{base_url}/tree/{item}"
        return tmpl.format(base_url=base_url, item=item)


class GitBranchDeletionV1(GitMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.git.branch.deletion"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "repo": PROJECT,
            "tag": {"type": "string"},
            "rev": {"type": "string"},
            "authors": {"type": "array", "items": GIT_RECEIVE_USER},
        },
        "required": ["agent", "repo", "branch", "rev", "authors"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Git branch: {branch} deleted\nBy: {agent_name}".format(
            branch=self.body["branch"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} deleted the branch {branch} on {name}".format(
            agent_name=self.agent_name,
            name=self.body["repo"]["fullname"],
            branch=self.body["branch"],
        )

    @property
    def url(self):
        return self.body["repo"]["full_url"]


class GitReceiveV1(GitMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.git.receive"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "forced": {"type": "boolean"},
            "repo": PROJECT,
            "old_commit": {"type": "string"},
            "branch": {"type": "string"},
            "authors": {"type": "array", "items": GIT_RECEIVE_USER},
            "total_commits": {"type": "number"},
            "start_commit": {"type": "string"},
            "end_commit": {"type": "string"},
        },
        "required": [
            "agent",
            "forced",
            "repo",
            "old_commit",
            "branch",
            "authors",
            "total_commits",
            "start_commit",
            "end_commit",
        ],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "New commit: {count} commits\nBy: {agent_name}".format(
            count=self.body["total_commits"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} pushed {count} commits on {fullname} (branch: {branch})".format(
            agent_name=self.agent_name,
            fullname=self.body["repo"]["fullname"],
            count=self.body["total_commits"],
            branch=self.body["branch"],
        )

    @property
    def url(self):
        base_url = self.body["repo"]["full_url"]

        item = self.body["branch"]
        if "refs/heads/" in item:
            item = item.replace("refs/heads/", "")

        tmpl = "{base_url}/tree/{item}"
        return tmpl.format(base_url=base_url, item=item)


class GitTagCreationV1(GitMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.git.tag.creation"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "repo": PROJECT,
            "tag": {"type": "string"},
            "rev": {"type": "string"},
            "authors": {"type": "array", "items": GIT_RECEIVE_USER},
        },
        "required": ["agent", "repo", "tag", "rev", "authors"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Git tag: {tag} created\nBy: {agent_name}".format(
            tag=self.body["tag"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} tagged the commit {rev} on {name} as {tag}".format(
            agent_name=self.agent_name,
            name=self.body["repo"]["fullname"],
            tag=self.body["tag"],
            rev=self.body["rev"],
        )

    @property
    def url(self):
        base_url = self.body["repo"]["full_url"]
        tag = self.body["tag"]

        tmpl = "{base_url}/commits/{tag}"
        return tmpl.format(base_url=base_url, tag=tag)


class GitTagDeletionV1(GitMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.git.tag.deletion"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "repo": PROJECT,
            "tag": {"type": "string"},
            "rev": {"type": "string"},
            "authors": {"type": "array", "items": GIT_RECEIVE_USER},
        },
        "required": ["agent", "repo", "tag", "rev", "authors"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Git tag: {tag} deleted\nBy: {agent_name}".format(
            tag=self.body["tag"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} deleted the tag {tag} of commit {rev} on {name}".format(
            agent_name=self.agent_name,
            name=self.body["repo"]["fullname"],
            tag=self.body["tag"],
            rev=self.body["rev"],
        )

    @property
    def url(self):
        base_url = self.body["repo"]["full_url"]
        tmpl = "{base_url}/releases"
        return tmpl.format(base_url=base_url)
