import pytest

from ..PyraUtils.common._file import FileUtils 

# fixture 是一种为您的测试提供一些常见设置或拆卸的功能
@pytest.fixture
def path():
    return "./tmp"

def test_fileutil_01(path):
    assert FileUtils.get_listfile_01(path)
