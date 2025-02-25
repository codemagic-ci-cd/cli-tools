from codemagic.models.application_package.android import Strings


def test_get_value():
    strings = Strings(
        """<resources>
            <string name="message">Hello Android!</string>
        </resources>""",
    )
    assert strings.get_value("message") == "Hello Android!"


def test_get_missing_value():
    strings = Strings(
        """<resources>
            <string name="text">Some text...</string>
        </resources>""",
    )
    assert strings.get_value("other_text") is None
