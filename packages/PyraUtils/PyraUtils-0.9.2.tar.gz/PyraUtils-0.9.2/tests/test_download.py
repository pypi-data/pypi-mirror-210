import pytest

from PyraUtils.common.download import DownloadUtil 
from PyraUtils.common.download import DownloadProgressUtil

# fixture 是一种为您的测试提供一些常见设置或拆卸的功能
@pytest.fixture
def url():
    return "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"

def test_downloadutil_01(url):
    dl_path = "./tmp/dl_01"
    assert (DownloadUtil.dl_01(url, dl_path), True)

def test_downloadutil_02(url):
    dl_path = "./tmp/dl_02"
    assert (DownloadUtil.dl_02(url, dl_path), True)

def test_downloadutil_03(url):
    dl_path = "./tmp/dl_03"
    assert (DownloadUtil.dl_03(url, dl_path), True)

def test_downloadutil_04(url):
    dl_path = "./tmp/dl_04"
    assert (DownloadUtil.dl_04(url, dl_path), True)

def test_downloadprogressutil_01(url):
    dl_path = "./tmp/dl_progress_01"
    assert (DownloadProgressUtil.dl_01(url, dl_path), True)

def test_downloadprogressutil_02(url):
    dl_path = "./tmp/dl_progress_02"
    assert (DownloadProgressUtil.dl_02(url, dl_path), True)