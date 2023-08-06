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

from ..misc_schema import TestNotificationV1


def test_minimal():
    """
    Assert the message schema validates a message with the required fields.
    """
    body = {
        "content": "Test message",
    }
    message = TestNotificationV1(body=body)
    message.validate()
    assert message.url == "https://pagure.io"


def test_missing_fields():
    """Assert an exception is actually raised on validation failure."""
    message = TestNotificationV1(body={})
    with pytest.raises(ValidationError):
        message.validate()


def test_str():
    """Assert __str__ produces a human-readable message."""
    body = {
        "content": "Test message",
    }
    expected_str = "Test notification"
    message = TestNotificationV1(body=body)
    message.validate()
    assert expected_str == str(message)


def test_summary():
    """Assert the summary is correct."""
    body = {
        "content": "Test message",
    }
    expected_summary = "Test notification"
    message = TestNotificationV1(body=body)
    message.validate()
    assert expected_summary == message.summary
