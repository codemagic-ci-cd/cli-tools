from codemagic.models.enums import ResourceEnum


class OrderBy(ResourceEnum):
    """
    Values follow the Firebase App Distribution `releases.list` `orderBy` grammar, which uses a
    space-separated `desc` suffix, see
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases/list
    """

    CREATE_TIME_DESC = "createTime desc"
    CREATE_TIME_ASC = "createTime"
