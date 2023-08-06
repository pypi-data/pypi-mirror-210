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

"""Unit tests for common properties of the message schemas."""

from .utils import PROJECT
from .. import get_message_object_from_topic


def test_object_type():
    """Assert some properties are correct."""
    cls = get_message_object_from_topic("pagure.git.receive")
    msg = cls(body={"repo": PROJECT})
    assert str(type(msg)) == "<class 'pagure_messages.git_schema.GitReceiveV1'>"


def test_topic():
    """Assert some properties are correct."""
    cls = get_message_object_from_topic("pagure.git.receive")
    msg = cls(body={"repo": PROJECT})

    assert msg.topic == "pagure.git.receive"


def test_invalidtopic():
    """Assert some properties are correct."""
    cls = get_message_object_from_topic("fedocal.invalid.topic")

    assert str(type(cls())) == "<class 'fedora_messaging.message.Message'>"
