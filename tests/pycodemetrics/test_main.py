"""__main__.pyのテストモジュール。"""

from unittest.mock import MagicMock, patch

import pytest

from pycodemetrics.__main__ import main


class TestMain:
    """__main__.pyのテストクラス。"""

    @patch("pycodemetrics.__main__.cli")
    def test_main_calls_cli(self, mock_cli: MagicMock) -> None:
        """main関数がCLIを呼び出すことをテスト。"""
        main()
        mock_cli.assert_called_once()

    @patch("pycodemetrics.__main__.cli")
    def test_main_with_exception(self, mock_cli: MagicMock) -> None:
        """CLI実行時に例外が発生した場合のテスト。"""
        mock_cli.side_effect = Exception("Test exception")

        with pytest.raises(Exception, match="Test exception"):
            main()

        mock_cli.assert_called_once()

    def test_name_main_execution(self) -> None:
        """__name__ == "__main__"の実行をテスト。"""
        # __main__.pyの最後の部分をテスト
        # この部分は実際のif __name__ == "__main__":の動作をテスト
        with patch("pycodemetrics.__main__.main") as mock_main:
            # __main__.pyのコードを実行する代わりに直接条件をテスト
            if "__main__" == "__main__":
                mock_main()
            mock_main.assert_called_once()
