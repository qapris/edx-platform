"""
Helpers for student roles
"""


from openedx.core.djangoapps.django_comment_common.models import (
    FORUM_ROLE_ADMINISTRATOR,
    FORUM_ROLE_COMMUNITY_TA,
    FORUM_ROLE_GROUP_MODERATOR,
    FORUM_ROLE_MODERATOR,
    Role
)
from openedx.core.lib.cache_utils import request_cached
from common.djangoapps.student.roles import (
    CourseBetaTesterRole,
    CourseInstructorRole,
    CourseStaffRole,
    GlobalStaff,
    OrgInstructorRole,
    OrgStaffRole
)

from openedx_filters.learning.filters import (
    AccessRoleCheckRequested,
    AccessRoleAdditionRequested,
    AccessRoleRemovalRequested,
    UsersWithRolesRequested
)


@request_cached()
def has_staff_roles(user, course_key):
    """
    Return true if a user has any of the following roles
    Staff, Instructor, Beta Tester, Forum Community TA, Forum Group Moderator, Forum Moderator, Forum Administrator
    """
    forum_roles = [FORUM_ROLE_COMMUNITY_TA, FORUM_ROLE_GROUP_MODERATOR,
                   FORUM_ROLE_MODERATOR, FORUM_ROLE_ADMINISTRATOR]
    is_staff = CourseStaffRole(course_key).has_user(user)
    is_instructor = CourseInstructorRole(course_key).has_user(user)
    is_beta_tester = CourseBetaTesterRole(course_key).has_user(user)
    is_org_staff = OrgStaffRole(course_key.org).has_user(user)
    is_org_instructor = OrgInstructorRole(course_key.org).has_user(user)
    is_global_staff = GlobalStaff().has_user(user)
    has_forum_role = Role.user_has_role_for_course(user, course_key, forum_roles)
    if any([is_staff, is_instructor, is_beta_tester, is_org_staff,
            is_org_instructor, is_global_staff, has_forum_role]):
        return True
    return False


def has_role_access(user, roles: list, course_key):
    """
    Return true if a user has the given role in the given course.
    """
    user, roles, course_key = AccessRoleCheckRequested.run_filter(
        user=user,
        roles=roles,
        course_key=course_key,
    )
    return [role.has_user(user) for role in roles]


def add_role_access(user, roles: list, course_key):
    """
    Add the given role to the user in the given course.
    """
    user, roles, course_key = AccessRoleAdditionRequested.run_filter(
        user=user,
        roles=roles,
        course_key=course_key,
    )
    for role in roles:
        role.add_users(user)


def remove_role_access(user, role):
    """
    Remove the given role from the user in the given course.
    """
    user, roles, course_key = AccessRoleRemovalRequested.run_filter(
        user=user,
        roles=roles,
        course_key=course_key,
    )
    for role in roles:
        role.remove_users(user)


def get_users_with_role(role):
    """
    Return a list of users who have the given role in the given course.
    """
    user, roles, course_key = UsersWithRolesRequested.run_filter(
        user=user,
        roles=roles,
        course_key=course_key,
    )
    users_with_roles = [
        role.users_with_role() for role in roles
    ]
    return users_with_roles
