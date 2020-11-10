def test_actions_invocation_record(action_invocations_record):
    assert len(action_invocations_record.actions) == 3
    assert action_invocations_record.archive is None
    assert action_invocations_record.metadata_ref.id == \
           '0~ziatpASSEiHdFpnwJuwZP5XrK5fND5RfMKOsfgAMd9kZrY7yLZfJQpqju3vazMV35oYDxSKotOIkTQvyUvaFLg=='
    assert action_invocations_record.metrics.analyzer_warning_count == 0
    assert action_invocations_record.metrics.error_count == 0
    assert action_invocations_record.metrics.tests_count == 14
    assert action_invocations_record.metrics.tests_failed_count == 6
    assert action_invocations_record.metrics.tests_skipped_count == 2
    assert action_invocations_record.metrics.warning_count == 0
