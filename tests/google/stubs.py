from unittest.mock import Mock


def google_request_stub(resources, resource_type_label):
    mock_execute = Mock()
    mock_execute.return_value = {resource_type_label: resources}

    class GoogleRequest:
        execute = mock_execute

    return GoogleRequest


def google_resource_stub(request_stub):
    class GoogleResource:
        @staticmethod
        def list(**_kw):
            return request_stub()

    return GoogleResource


def google_request_pagination_stub(resources, resource_type_label):
    mock_execute = Mock()
    mock_execute.side_effect = [
        {resource_type_label: [resources[0]], 'nextPageToken': 'next-page-token'},
        {resource_type_label: [resources[1]]},
    ]

    class GoogleRequest:
        execute = mock_execute

    return GoogleRequest
