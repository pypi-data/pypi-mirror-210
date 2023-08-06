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

from fedora_messaging import message

import pkg_resources


from .git_schema import (  # noqa: F401
    GitBranchCreationV1,
    GitBranchDeletionV1,
    GitReceiveV1,
    GitTagCreationV1,
    GitTagDeletionV1,
)
from .issue_schema import (  # noqa: F401
    IssueAssignedAddedV1,
    IssueAssignedResetV1,
    IssueCommentAddedV1,
    IssueDependencyAddedV1,
    IssueDependencyRemovedV1,
    IssueDropV1,
    IssueEditV1,
    IssueNewV1,
    IssueTagAddedV1,
    IssueTagRemovedV1,
)
from .misc_schema import (  # noqa: F401
    CommitFlagAddedV1,
    CommitFlagUpdatedV1,
    GroupEditV1,
    TestNotificationV1,
)
from .project_schema import (  # noqa: F401
    ProjectDeletedV1,
    ProjectEditV1,
    ProjectForkedV1,
    ProjectGroupAccessUpdatedV1,
    ProjectGroupAddedV1,
    ProjectGroupRemovedV1,
    ProjectNewV1,
    ProjectTagEditedV1,
    ProjectTagRemovedV1,
    ProjectUserAccessUpdatedV1,
    ProjectUserAddedV1,
    ProjectUserRemovedV1,
)
from .pull_requests_schema import (  # noqa: F401
    PullRequestAssignedAddedV1,
    PullRequestAssignedResetV1,
    PullRequestClosedV1,
    PullRequestCommentAddedV1,
    PullRequestCommentEditedV1,
    PullRequestFlagAddedV1,
    PullRequestFlagUpdatedV1,
    PullRequestInitialCommentEditedV1,
    PullRequestNewV1,
    PullRequestRebasedV1,
    PullRequestReopenedV1,
    PullRequestTagAddedV1,
    PullRequestTagRemovedV1,
    PullRequestUpdatedV1,
)


def get_message_object_from_topic(topic):
    """Returns the Message class corresponding to the topic."""

    output = None

    for entry_point in pkg_resources.iter_entry_points("fedora.messages"):
        cls = entry_point.load()
        if cls.topic == topic:
            output = cls
            break

    if output is None:
        output = message.Message

    return output
