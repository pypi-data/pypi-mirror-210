import pytest

from lib.exception import NoAutoScanException
from test import mock_entry
from test.mock2_entity import Mock2
from test.mock_entity import Mock
from test.mock_entry import engine


def test_mock_inject_success():
    mock2 = mock_entry.get_mock2()

    assert mock2 == engine.application_context.get_type_object_first(Mock2)
    print("自动加载mock2成功")
    assert mock2.get_mock() == engine.application_context.get_type_object_first(Mock)
    print("自动加载mock2中的mock1成功")


def test_mock_inject_failed():
    # mock4 没有设置自动依赖，应该报错
    with pytest.raises(NoAutoScanException):
        mock_entry.get_mock3()
    print("成功检测到mock3中没有加载成功的mock4")
