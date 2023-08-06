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

"""Unit tests for the message schema."""

from jsonschema import ValidationError

import pytest

from .utils import PROJECT
from ..project_schema import ProjectGroupAddedV1


def test_minimal():
    """
    Assert the message schema validates a message with the required fields.
    """
    body = {
        "agent": "dummy-user",
        "project": PROJECT,
    }
    message = ProjectGroupAddedV1(body=body)
    message.validate()
    assert message.url == "http://localhost.localdomain/fedora-infra/fedocal-messages"


def test_missing_fields():
    """Assert an exception is actually raised on validation failure."""
    minimal_message = {
        "project": PROJECT,
    }
    message = ProjectGroupAddedV1(body=minimal_message)
    with pytest.raises(ValidationError):
        message.validate()


def test_str():
    """Assert __str__ produces a human-readable message."""
    body = {
        "agent": "dummy-user",
        "project": PROJECT,
        "new_group": "dummy-group",
        "access": "commit",
    }
    expected_str = (
        "Group: dummy-group added to fedora-infra/fedocal-messages "
        "as commit\nBy: dummy-user"
    )
    message = ProjectGroupAddedV1(body=body)
    message.validate()
    assert expected_str == str(message)


def test_summary():
    """Assert the summary is correct."""
    body = {
        "agent": "dummy-user",
        "project": PROJECT,
        "new_group": "dummy-group",
        "access": "commit",
    }
    expected_summary = (
        "dummy-user added the group dummy-group to the project "
        '"fedora-infra/fedocal-messages" at the commit level'
    )
    message = ProjectGroupAddedV1(body=body)
    message.validate()
    assert expected_summary == message.summary
