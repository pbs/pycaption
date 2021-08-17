import pytest


@pytest.fixture(scope="session")
def sample_microdvd():
    return """{230}{307}( clock ticking )
{371}{425}MAN:|When we think|\u266a ...say bow, wow, \u266a
{425}{468}we have this vision of Einstein
{468}{522}as an old, wrinkly man|with white hair.
{522}{669}MAN 2:|E equals m c-squared is|not about an old Einstein.
{669}{805}MAN 2:|It's all about an eternal Einstein.
{805}{905}<LAUGHING & WHOOPS!>
"""


@pytest.fixture(scope="session")
def sample_microdvd_2():
    return """{230}{307}( clock ticking )
{371}{425}MAN:|When we think|\u266a ...say bow, wow, \u266a
{425}{468}we have this vision of Einstein
{468}{522}|as an old, wrinkly man|with white hair.
{522}{669}MAN 2:|E equals m c-squared is|not about an old Einstein.
{669}{805}MAN 2:|It's all about an eternal Einstein.
{805}{905}<LAUGHING & WHOOPS!>
"""


@pytest.fixture(scope="session")
def sample_microdvd_invalid_format():
    return """{230}{307}( clock ticking )
{}{425}{567} MAN:|When we think|\u266a ...say bow, wow, \u266a
{425}{468}we have this vision of Einstein
"""


@pytest.fixture(scope="session")
def missing_fps_sample_microdvd():
    return """{301}{307}( clock ticking )
{0}{0} MAN:|When we think|\u266a ...say bow, wow, \u266a
"""


@pytest.fixture(scope="session")
def sample_microdvd_empty():
    return """
"""


@pytest.fixture(scope="session")
def sample_microdvd_empty_cue_output():
    return """{30}{57}abc"""
