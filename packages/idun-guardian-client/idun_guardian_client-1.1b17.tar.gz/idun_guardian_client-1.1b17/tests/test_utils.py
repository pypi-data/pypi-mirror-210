from idun_guardian_client import igeb_utils


def test_check_platform():
    """
    GIVEN None
    WHEN check_platform is called
    THEN a string is returned
    """

    import platform

    assert isinstance(igeb_utils.check_platform(), str)
    assert platform.system() == igeb_utils.check_platform()


def test_check_valid_mac():
    """
    GIVEN a string
    WHEN check_valid_mac is called
    THEN a boolean is returned
    """
    assert isinstance(igeb_utils.check_valid_mac("00:00:00:00:00:00"), bool)
    assert igeb_utils.check_valid_mac("00000000-0000-0000-0000-000000000000") == False


def test_check_valid_uuid():
    """
    GIVEN a string
    WHEN check_valid_uuid is called
    THEN a boolean is returned
    """
    assert isinstance(
        igeb_utils.check_valid_uuid("00000000-0000-0000-0000-000000000000"), bool
    )
    assert igeb_utils.check_valid_uuid("00:00:00:00:00:00") == False


def generate_mock_data_array():
    """
    GIVEN None
    WHEN generate_mock_data is called
    THEN a dict is returned
    """
    assert isinstance(igeb_utils.generate_mock_data(), dict)
