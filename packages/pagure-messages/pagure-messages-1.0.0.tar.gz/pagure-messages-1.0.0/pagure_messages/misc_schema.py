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

from .base import COMMIT_FLAG, GROUP, PROJECT, PagureMessage, SCHEMA_URL


class CommitFlagAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.commit.flag.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "repo": PROJECT,
            "flag": COMMIT_FLAG,
        },
        "required": ["agent", "repo", "flag"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "New commit flag: {username} {status}\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            username=self.body["flag"]["username"],
            status=self.body["flag"]["status"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return (
            "Commit {commit_hash} of project {name} was flagged as {status} "
            "by {username}".format(
                name=self.body["repo"]["fullname"],
                commit_hash=self.body["flag"]["commit_hash"],
                username=self.body["flag"]["username"],
                status=self.body["flag"]["status"],
            )
        )

    @property
    def url(self):
        full_url = self.body["repo"]["full_url"]
        commithash = self.body["flag"]["commit_hash"]

        return "{full_url}/c/{commithash}".format(
            full_url=full_url, commithash=commithash
        )


class CommitFlagUpdatedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.commit.flag.updated"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "repo": PROJECT,
            "flag": COMMIT_FLAG,
        },
        "required": ["agent", "repo", "flag"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "New commit flag: {username} {status}\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            username=self.body["flag"]["username"],
            status=self.body["flag"]["status"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return (
            "{username} updated flag on commit {commit_hash} of project "
            "{name} to {status}".format(
                name=self.body["repo"]["fullname"],
                commit_hash=self.body["flag"]["commit_hash"],
                username=self.body["flag"]["username"],
                status=self.body["flag"]["status"],
            )
        )

    @property
    def url(self):
        full_url = self.body["repo"]["full_url"]
        commithash = self.body["flag"]["commit_hash"]

        return "{full_url}/c/{commithash}".format(
            full_url=full_url, commithash=commithash
        )


class GroupEditV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.group.edit"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "group": GROUP,
            "fields": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["agent", "group", "fields"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Group edit: {group_name}\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            group_name=self.body["group"]["name"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return (
            "{agent_name} edited the fields {fields} of the group {group_name}".format(
                agent_name=self.agent_name,
                group_name=self.body["group"]["name"],
                fields=", ".join(self.body["fields"]),
            )
        )

    @property
    def url(self):
        return self.body["group"]["full_url"]


class TestNotificationV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.Test.notification"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "content": {"type": "string"},
        },
        "required": ["content"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Test notification"

    @property
    def summary(self):
        """Return a summary of the message."""
        return str(self)

    @property
    def url(self):
        return self.get_base_url()
