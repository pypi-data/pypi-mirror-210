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

from .base import ISSUE, PROJECT, PagureMessage, SCHEMA_URL


class IssueAssignedAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when an issue is deleted.
    """

    topic = "pagure.issue.assigned.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
        },
        "required": ["agent", "project", "issue"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Issue: {fullname}#{id} assigned to {assignee}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            agent_name=self.agent_name,
            assignee=self.body["issue"]["assignee"]["name"],
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} assigned issue {name}#{id} to {assignee}".format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            assignee=self.body["issue"]["assignee"]["name"],
        )

    @property
    def url(self):
        return self.body["issue"]["full_url"]


class IssueAssignedResetV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when an issue is deleted.
    """

    topic = "pagure.issue.assigned.reset"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
        },
        "required": ["agent", "project", "issue"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Issue un-assigned: {fullname}#{id}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} reset the assignee on issue {name}#{id}".format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
        )

    @property
    def url(self):
        return self.body["issue"]["full_url"]


class IssueCommentAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when an issue is deleted.
    """

    topic = "pagure.issue.comment.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Issue: {fullname}#{id} has a new comment\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} commented on the issue {name}#{id}".format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
        )

    @property
    def url(self):
        issue_url = self.body["issue"]["full_url"]
        commentid = self.body["issue"]["comments"][-1]["id"]

        return "{issue_url}#comment-{commentid}".format(
            issue_url=issue_url, commentid=commentid
        )


class IssueDependencyAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when an issue is deleted.
    """

    topic = "pagure.issue.dependency.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
            "added_dependency": {"type": "number"},
        },
        "required": ["agent", "project", "added_dependency"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            "Issue: {fullname}#{id} depends on #{depissueid}\nBy: {agent_name}".format(
                fullname=self.body["project"]["fullname"],
                id=self.body["issue"]["id"],
                agent_name=self.agent_name,
                depissueid=self.body["added_dependency"],
            )
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} set the issue {name}#{id} as depending on #{depissueid}".format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            depissueid=self.body["added_dependency"],
        )

    @property
    def url(self):
        return self.body["issue"]["full_url"]


class IssueDependencyRemovedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when an issue is deleted.
    """

    topic = "pagure.issue.dependency.removed"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
            "removed_dependency": {"type": "array", "items": {"type": "number"}},
        },
        "required": ["agent", "project", "removed_dependency"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            "Issue: {fullname}#{id} no longer depending"
            " on #{depissueid}\nBy: {agent_name}".format(
                fullname=self.body["project"]["fullname"],
                id=self.body["issue"]["id"],
                agent_name=self.agent_name,
                depissueid=", #".join(
                    [str(i) for i in self.body["removed_dependency"]]
                ),
            )
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return (
            "{agent_name} removed the dependency"
            " on #{depissueid} on the issue {name}#{id}".format(
                agent_name=self.agent_name,
                name=self.body["project"]["fullname"],
                id=self.body["issue"]["id"],
                depissueid=", #".join(
                    [str(i) for i in self.body["removed_dependency"]]
                ),
            )
        )

    @property
    def url(self):
        return self.body["issue"]["full_url"]


class IssueDropV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when an issue is deleted.
    """

    topic = "pagure.issue.drop"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
        },
        "required": ["agent", "project", "issue"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Issue deleted: {fullname}#{id}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} deleted issue {name}#{id}: {title}".format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            title=self.body["issue"]["title"],
        )

    @property
    def url(self):
        full_url = self.body["project"]["full_url"]

        return "{full_url}/issues".format(full_url=full_url)


class IssueEditV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when an issue is updated.
    """

    topic = "pagure.issue.edit"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
            "fields": {"type": "array", "items": {"type": ["string", "null"]}},
        },
        "required": ["agent", "project", "issue", "fields"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Edited Issue: {fullname}#{id}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return (
            "{agent_name} edited fields {fields} of issue {name}#{id}: {title}".format(
                agent_name=self.agent_name,
                name=self.body["project"]["fullname"],
                id=self.body["issue"]["id"],
                title=self.body["issue"]["title"],
                fields=", ".join(self.body["fields"]),
            )
        )

    @property
    def url(self):
        return self.body["issue"]["full_url"]


class IssueNewV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.issue.new"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
        },
        "required": ["agent", "project", "issue"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "New Issue: {fullname}#{id}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} created issue {name}#{id}: {title}".format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            title=self.body["issue"]["title"],
        )

    @property
    def url(self):
        return self.body["issue"]["full_url"]


class IssueTagAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when an issue is deleted.
    """

    topic = "pagure.issue.tag.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
            "tags": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Issue: {fullname}#{id} tagged with {tags}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            agent_name=self.agent_name,
            tags=", ".join(self.body["tags"]),
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} tagged the issue {name}#{id} with: {tags}".format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            tags=", ".join(self.body["tags"]),
        )

    @property
    def url(self):
        return self.body["issue"]["full_url"]


class IssueTagRemovedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when an issue is deleted.
    """

    topic = "pagure.issue.tag.removed"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "issue": ISSUE,
            "tags": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Issue: {fullname}#{id} un-tagged with {tags}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            agent_name=self.agent_name,
            tags=", ".join(self.body["tags"]),
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return "{agent_name} removed tags {tags} from issue {name}#{id}".format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
            id=self.body["issue"]["id"],
            tags=", ".join(self.body["tags"]),
        )

    @property
    def url(self):
        return self.body["issue"]["full_url"]
