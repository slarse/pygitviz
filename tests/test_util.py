from _pygitviz import util


class TestGetOs:
    """Tests for the get_os function."""

    WSL2_UNAME_STRING = "Linux DESKTOP-XXXXXXX 5.10.16.3-microsoft-standard-WSL2 #1 SMP Fri Apr 2 22:23:49 UTC 2021"

    def test_detect_wsl2(self, mocker):
        mocker.patch(
            "_pygitviz.util.captured_run",
            autospec=True,
            return_value=(0, self.WSL2_UNAME_STRING, ""),
        )

        os = util.get_os("linux")

        assert os == util.WSL2
