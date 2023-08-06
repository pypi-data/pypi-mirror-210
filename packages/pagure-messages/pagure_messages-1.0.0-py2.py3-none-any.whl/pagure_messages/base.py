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
import warnings

from fedora_messaging import message
from fedora_messaging.schema_utils import user_avatar_url


SCHEMA_URL = "http://fedoraproject.org/message-schema/"


TagColored = {
    "type": "object",
    "properties": {
        "tag": {"type": "string"},
        "tag_description": {"type": "string"},
        "tag_color": {"type": "string"},
    },
    "required": ["tag", "tag_description", "tag_color"],
}


BOARD = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "active": {"type": "boolean"},
        "status": {"type": ["array", "null"], "items": {"type": "string"}},
        "tag": {"type": TagColored},
        "full_url": {"type": "string"},
    },
    "required": ["name", "active", "status", "tag", "full_url"],
}


BOARD_STATUS = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "bg_color": {"type": "string"},
        "close": {"type": "boolean"},
        "close_status": {"type": ["string", "null"]},
        "default": {"type": "boolean"},
    },
    "required": ["name", "bg_color", "close", "close_status", "default"],
}


BOARD_ISSUE = {
    "type": "object",
    "properties": {
        "board": {"type": BOARD},
        "status": {"type": BOARD_STATUS},
        "rank": {"type": "number"},
    },
    "required": ["board", "rank", "status"],
}


USER = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "fullname": {"type": "string"},
        "url_path": {"type": "string"},
        "full_path": {"type": "string"},
    },
    "required": ["name", "fullname", "url_path"],
}


GIT_RECEIVE_USER = {
    "type": "object",
    "properties": {
        "name": {"oneOf": [{"type": "null"}, {"type": "string"}]},
        "fullname": {"type": "string"},
        "url_path": {"oneOf": [{"type": "null"}, {"type": "string"}]},
    },
    "required": ["name", "fullname", "url_path"],
}


PAGURE_LOG = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "type": {"type": "string"},
        "ref_id": {"type": "string"},
        "date": {"type": "string"},
        "date_created": {"type": "string"},
        "user": USER,
    },
    "required": ["id", "type", "ref_id", "date", "date_created", "user"],
}


MILESTONES = {
    "type": "object",
    "properties": {
        "date": {"type": "string"},
        "active": {"type": "boolean"},
    },
}


PRIORITIES = {
    "type": "object",
    "properties": {
        "date": {"type": "string"},
        "active": {"type": "boolean"},
    },
}


BASE_PROJECT = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "fullname": {"type": "string"},
        "url_path": {"type": "string"},
        "description": {"type": "string"},
        "namespace": {"type": ["string", "null"]},
        "parent": {"type": "null"},
        "date_created": {"type": "string"},
        "date_modified": {"type": "string"},
        "user": USER,
        # "access_users": {"type": "string"},
        # "access_groups": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        # "priorities": {"type": "object"},
        # "custom_keys": {
        #    "type": "array",
        #    "items": {"type": "array", "items": {"type": "string"}},
        # },
        "close_status": {"type": "array", "items": {"type": "string"}},
        "milestones": {"type": "object", "properties": {"type": MILESTONES}},
    },
    "required": [
        "id",
        "name",
        "fullname",
        "url_path",
        "description",
        "namespace",
        "parent",
        "date_created",
        "date_modified",
        "user",
        # "access_users",
        # "access_groups",
        "tags",
        # "priorities",
        # "custom_keys",
        "close_status",
        "milestones",
    ],
}


PROJECT = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "fullname": {"type": "string"},
        "url_path": {"type": "string"},
        "full_url": {"type": "string"},
        "description": {"type": "string"},
        "namespace": {"type": ["string", "null"]},
        # "parent": {"type": ["null", BASE_PROJECT]},
        "date_created": {"type": "string"},
        "date_modified": {"type": "string"},
        "user": USER,
        # "access_users": {"type": "string"},
        # "access_groups": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        # "priorities": {"type": "object"},
        # "custom_keys": {
        # "type": "array",
        # "items": {"type": "array", "items": {"type": "string"}},
        # },
        "close_status": {"type": "array", "items": {"type": "string"}},
        "milestones": {
            "oneOf": [
                {"type": "null"},
                MILESTONES,
            ]
        },
    },
    "required": [
        "id",
        "name",
        "full_url",
        "fullname",
        "url_path",
        "description",
        "namespace",
        # "parent",
        "date_created",
        "date_modified",
        "user",
        # "access_users",
        # "access_groups",
        "tags",
        # "priorities",
        # "custom_keys",
        "close_status",
        "milestones",
    ],
}


RELATED_PR = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "title": {"type": "string"},
    },
    "required": ["id", "title"],
}


ISSUE = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "full_url": {"type": "string"},
        "title": {"type": "string"},
        "content": {"type": "string"},
        "status": {"type": "string"},
        "close_status": {"type": ["string", "null"]},
        "date_created": {"type": "string"},
        "last_updated": {"type": "string"},
        "closed_at": {"type": ["string", "null"]},
        "user": USER,
        "private": {"type": "boolean"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "depends": {"type": "array", "items": {"type": "string"}},
        "blocks": {"type": "array", "items": {"type": "string"}},
        "assignee": {"oneOf": [{"type": "null"}, USER]},
        # "priorities": {"type": "object"},
        "milestone": {
            "oneOf": [
                {"type": "null"},
                {"type": "string"},
            ]
        },
        "custom_fields": {
            "type": "array",
            "items": {"type": "array", "items": {"type": "string"}},
        },
        "closed_by": {"oneOf": [{"type": "null"}, USER]},
        "related_prs": {
            "oneOf": [{"type": "null"}, {"type": "array", "items": RELATED_PR}]
        },
    },
    "required": [
        "id",
        "full_url",
        "title",
        "content",
        "status",
        "close_status",
        "date_created",
        "last_updated",
        "closed_at",
        "user",
        "private",
        "tags",
        "depends",
        "blocks",
        "assignee",
        # "priorities",
        "milestone",
        "custom_fields",
        "closed_by",
        "related_prs",
    ],
}


PULL_REQUEST = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "uid": {"type": "string"},
        "title": {"type": "string"},
        "full_url": {"type": "string"},
        "branch": {"type": "string"},
        "project": PROJECT,
        "branch_from": {"type": "string"},
        "repo_from": {"oneOf": [{"type": "null"}, USER]},
        "remote_git": {"oneOf": [{"type": "null"}, {"type": "string"}]},
        "date_created": {"type": "string"},
        "updated_on": {"type": "string"},
        "last_updated": {"type": "string"},
        "closed_at": {"oneOf": [{"type": "null"}, {"type": "string"}]},
        "user": USER,
        "assignee": {"oneOf": [{"type": "null"}, USER]},
        "status": {"type": "string"},
        "commit_start": {"oneOf": [{"type": "null"}, {"type": "string"}]},
        "commit_stop": {"oneOf": [{"type": "null"}, {"type": "string"}]},
        "closed_by": {"oneOf": [{"type": "null"}, USER]},
        "initial_comment": {"oneOf": [{"type": "null"}, {"type": "string"}]},
        "cached_merge_status": {"type": "string"},
        "threshold_reached": {"oneOf": [{"type": "null"}, {"type": "string"}]},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "id",
        "uid",
        "title",
        "full_url",
        "branch",
        "project",
        "branch_from",
        "repo_from",
        "remote_git",
        "date_created",
        "updated_on",
        "last_updated",
        "closed_at",
        "user",
        "assignee",
        "status",
        "commit_start",
        "commit_stop",
        "closed_by",
        "initial_comment",
        "cached_merge_status",
        "threshold_reached",
        "tags",
    ],
}


COMMIT_FLAG = {
    "type": "object",
    "properties": {
        "commit_hash": {"type": "string"},
        "username": {"type": "string"},
        "comment": {"type": "string"},
        "status": {"type": "string"},
        "url": {"type": "string"},
        "date_created": {"type": "string"},
        "date_updated": {"type": "string"},
        "user": USER,
    },
    "required": [
        "commit_hash",
        "username",
        "comment",
        "status",
        "url",
        "date_created",
        "date_updated",
        "user",
    ],
}


GROUP = {
    "type": "object",
    "properties": {
        "display_name": {"type": "string"},
        "description": {"type": "string"},
        "creator": USER,
        "members": {"type": "array", "items": {"type": "string"}},
        "date_created": {"type": "string"},
        "group_type": {"type": "string"},
        "name": {"type": "string"},
        "full_url": {"type": "string"},
    },
    "required": [
        "display_name",
        "description",
        "creator",
        "members",
        "date_created",
        "group_type",
        "name",
        "full_url",
    ],
}


class PagureMessage(message.Message):
    """
    A sub-class of a Fedora message that defines a message schema for messages
    published by pagure.
    """

    __link__ = "https://pagure.io"
    __stg_link__ = "https://stg.pagure.io"

    def get_base_url(self):
        base_url = self.__link__
        if ".stg." in self.topic:  # pragma: no cover
            base_url = self.__stg_link__
        return base_url

    @property
    def app_name(self):
        return "Pagure"

    @property
    def app_icon(self):
        return "https://apps.fedoraproject.org/img/icons/pagure.png"

    @property
    def agent(self):
        warnings.warn(
            "agent property is deprecated, please use agent_name instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.agent_name

    @property
    def agent_name(self):
        return self.body.get("agent")

    @property
    def agent_avatar(self):
        return user_avatar_url(self.agent_name)

    @property
    def usernames(self):
        return [self.agent_name]
