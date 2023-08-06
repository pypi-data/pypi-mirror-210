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

from .base import PROJECT, PagureMessage, SCHEMA_URL


class ProjectNewV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.new"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "New Project: {fullname}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return '{agent_name} created project "{name}"'.format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectEditV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.edit"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "fields": {"type": "array", "items": {"type": ["string", "null"]}},
        },
        "required": ["agent", "project", "fields"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Project Edited: {fullname}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return '{agent_name} edited the fields {fields} of project "{name}"'.format(
            agent_name=self.agent_name,
            fields=", ".join(self.body["fields"]),
            name=self.body["project"]["fullname"],
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectForkedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.forked"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Project: {fullname}\nForked by: {agent_name}".format(
            fullname=self.body["project"]["parent"]["fullname"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return '{agent_name} forked project "{parent}" to {name}'.format(
            agent_name=self.agent_name,
            parent=self.body["project"]["parent"]["fullname"],
            name=self.body["project"]["fullname"],
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectDeletedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.deleted"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Project: {fullname}\nDeleted by: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return '{agent_name} deleted project "{name}"'.format(
            agent_name=self.agent_name,
            name=self.body["project"]["fullname"],
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectGroupAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.group.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            "Group: {group} added to {fullname} as {access}\nBy: {agent_name}".format(
                fullname=self.body["project"]["fullname"],
                group=self.body["new_group"],
                access=self.body["access"],
                agent_name=self.agent_name,
            )
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return (
            '{agent_name} added the group {group} to the project "{name}" at '
            "the {access} level".format(
                agent_name=self.agent_name,
                group=self.body["new_group"],
                access=self.body["access"],
                name=self.body["project"]["fullname"],
            )
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectGroupRemovedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.group.removed"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
            "removed_groups": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            "Group: {group} removed from {fullname}({access})\nBy: {agent_name}".format(
                fullname=self.body["project"]["fullname"],
                group=self.body["new_group"],
                access=self.body["access"],
                agent_name=self.agent_name,
            )
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return (
            "{agent_name} removed the group {group} (with {access} level)  from the "
            'project "{name}"'.format(
                agent_name=self.agent_name,
                group=self.body["new_group"],
                access=self.body["access"],
                name=self.body["project"]["fullname"],
            )
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectGroupAccessUpdatedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.group.access.updated"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Group: {group} access updated to {access} on {fullname}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            group=self.body["new_group"],
            access=self.body["new_access"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return (
            "{agent_name} updated the access of group {group} to {access} on "
            'the project "{name}"'.format(
                agent_name=self.agent_name,
                group=self.body["new_group"],
                access=self.body["new_access"],
                name=self.body["project"]["fullname"],
            )
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectTagEditedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.tag.edited"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Tag: {tag_name} edited on {fullname}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            tag_name=self.body["new_tag"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return '{agent_name} edited the tag {tag_name} on the project "{name}"'.format(
            agent_name=self.agent_name,
            tag_name=self.body["new_tag"],
            name=self.body["project"]["fullname"],
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectTagRemovedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.tag.removed"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "Tag(s): {tags} removed from {fullname}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            tags=", ".join(self.body["tags"]),
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return '{agent_name} removed the tag(s) {tags} of project "{name}"'.format(
            agent_name=self.agent_name,
            tags=", ".join(self.body["tags"]),
            name=self.body["project"]["fullname"],
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectUserAccessUpdatedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.user.access.updated"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "User: {user} access edited to {new_access} on {fullname}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            user=self.body["new_user"],
            new_access=self.body["new_access"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return (
            "{agent_name} updated the access of {user} to {new_access} on the "
            'project "{name}"'.format(
                agent_name=self.agent_name,
                user=self.body["new_user"],
                new_access=self.body["new_access"],
                name=self.body["project"]["fullname"],
            )
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectUserAddedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.user.added"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "User: {user} added to {fullname}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            user=self.body["new_user"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return '{agent_name} added the {user} to the project "{name}"'.format(
            agent_name=self.agent_name,
            user=self.body["new_user"],
            name=self.body["project"]["fullname"],
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]


class ProjectUserRemovedV1(PagureMessage):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure when a new thing is created.
    """

    topic = "pagure.project.user.removed"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a new project is created",
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "project": PROJECT,
        },
        "required": ["agent", "project"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return "User: {user} removed from {fullname}\nBy: {agent_name}".format(
            fullname=self.body["project"]["fullname"],
            user=self.body["removed_user"],
            agent_name=self.agent_name,
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return '{agent_name} removed the {user} from the project "{name}"'.format(
            agent_name=self.agent_name,
            user=self.body["removed_user"],
            name=self.body["project"]["fullname"],
        )

    @property
    def url(self):
        return self.body["project"]["full_url"]
