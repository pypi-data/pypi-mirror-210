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

from .base import COMMIT_FLAG, PROJECT, PULL_REQUEST, PagureMessage, SCHEMA_URL


class PullRequestAssignedAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.assigned.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
            "project": PROJECT,
        },
        "required": ["agent", "pullrequest", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Pull-request {name}#{id} was assigned\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{username} assigned the pull-request {name}#{id} to {assignee}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.agent_name,
            assignee=self.body["pullrequest"]["assignee"]["name"],
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestAssignedResetV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.assigned.reset"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
            "project": PROJECT,
        },
        "required": ["agent", "pullrequest", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Pull-request {name}#{id} was un-assigned\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{username} reset the assignee of the pull-request {name}#{id}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.agent_name,
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestClosedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.closed"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
            "merged": {"type": "boolean"},
        },
        "required": ["agent", "pullrequest", "merged"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            "Pull-Request: {fullname}#{id} has been {action}\nBy: {agent_name}".format(
                fullname=self.body["pullrequest"]["project"]["fullname"],
                id=self.body["pullrequest"]["id"],
                agent_name=self.agent_name,
                action="merged" if self.body["merged"] else "closed without merging",
            )
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} {action} the pull-request {name}#{id}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            action="merged" if self.body["merged"] else "closed without merging",
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestCommentAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.comment.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
        },
        "required": ["agent", "pullrequest"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            "Pull-Request: {fullname}#{id} has a new comment\nBy: {agent_name}".format(
                fullname=self.body["pullrequest"]["project"]["fullname"],
                id=self.body["pullrequest"]["id"],
                agent_name=self.agent_name,
            )
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} commented on the pull-request {name}#{id}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
        )

    @property
    def url(self):
        full_url = self.body["pullrequest"]["full_url"]
        commentid = self.body["pullrequest"]["comments"][-1]["id"]

        return "{full_url}#comment-{commentid}".format(
            full_url=full_url, commentid=commentid
        )


class PullRequestCommentEditedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.comment.edited"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
        },
        "required": ["agent", "pullrequest"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            "Edited comment on Pull-Request: {fullname}#{id}\nBy: {agent_name}".format(
                fullname=self.body["pullrequest"]["project"]["fullname"],
                id=self.body["pullrequest"]["id"],
                agent_name=self.agent_name,
            )
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} edited comment on the pull-request {name}#{id}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
        )

    @property
    def url(self):
        full_url = self.body["pullrequest"]["full_url"]
        commentid = self.body["pullrequest"]["comments"][-1]["id"]

        return "{full_url}#comment-{commentid}".format(
            full_url=full_url, commentid=commentid
        )


class PullRequestFlagAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.flag.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
            "flag": COMMIT_FLAG,
        },
        "required": ["agent", "pullrequest", "flag"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "New pull-request flag: {username} {status}\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            username=self.body["flag"]["username"],
            status=self.body["flag"]["status"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "Pull-request {name}#{id} was flagged as {status} by {username}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.body["flag"]["username"],
            status=self.body["flag"]["status"],
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestFlagUpdatedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.flag.updated"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
            "flag": COMMIT_FLAG,
        },
        "required": ["agent", "pullrequest", "flag"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            "Pull-request flag updated: {username} {status}\nBy: {agent_name}".format(
                agent_name=self.agent_name,
                username=self.body["flag"]["username"],
                status=self.body["flag"]["status"],
            )
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{username} updated flag on pull-request {name}#{id} to {status}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.body["flag"]["username"],
            status=self.body["flag"]["status"],
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestInitialCommentEditedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.initial_comment.edited"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "pullrequest": PULL_REQUEST,
        },
        "required": ["agent", "pullrequest", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            "Description of pull-request {name}#{id} edited\nBy: {agent_name}".format(
                agent_name=self.agent_name,
                name=self.body["pullrequest"]["project"]["fullname"],
                id=self.body["pullrequest"]["id"],
            )
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{username} has edited the description of the pull-request {name}#{id}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.agent_name,
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestNewV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.new"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
        },
        "required": ["agent", "pullrequest"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "New Pull-Request: {fullname}#{id}\nBy: {agent_name}".format(
            fullname=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} opened a pull-request {fullname}#{id}: {title}".format(
            agent_name=self.agent_name,
            fullname=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            title=self.body["pullrequest"]["title"],
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestRebasedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.rebased"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
        },
        "required": ["agent", "pullrequest"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Pull-request {name}#{id} was rebased\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{username} rebased the pull-request {name}#{id}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.agent_name,
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestReopenedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.reopened"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
        },
        "required": ["agent", "pullrequest"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Pull-request {name}#{id} was re-opened\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{username} re-opened the pull-request {name}#{id}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.agent_name,
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestTagAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.tag.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
            "project": PROJECT,
            "tags": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["agent", "pullrequest", "project", "tags"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Pull-request {name}#{id} was tagged\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{username} tagged the pull-request {name}#{id} with {tags}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.agent_name,
            tags=", ".join(self.body["tags"]),
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestTagRemovedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.tag.removed"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
            "project": PROJECT,
            "tags": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["agent", "pullrequest", "project", "tags"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Pull-request {name}#{id} was un-tagged\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{username} un-tagged the pull-request {name}#{id} with: {tags}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.agent_name,
            tags=", ".join(self.body["tags"]),
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]


class PullRequestUpdatedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.pull-request.updated"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "pullrequest": PULL_REQUEST,
        },
        "required": ["agent", "pullrequest"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Pull-request {name}#{id} was updated\nBy: {agent_name}".format(
            agent_name=self.agent_name,
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{username} updated the pull-request {name}#{id}".format(
            name=self.body["pullrequest"]["project"]["fullname"],
            id=self.body["pullrequest"]["id"],
            username=self.agent_name,
        )

    @property
    def url(self):
        return self.body["pullrequest"]["full_url"]
