# Contributing to PyCodeMetrics

PyCodeMetricsプロジェクトへの貢献に興味を持っていただき、ありがとうございます。以下は、開発者向けのガイドラインです。

## 開発環境のセットアップ

このプロジェクトはuvを使用して管理されています。以下の手順で開発環境をセットアップしてください：

1. uv のインストール

    [astral-sh/uv](https://github.com/astral-sh/uv)の手順に従ってuvをインストール

2. リポジトリをクローンします。

    ```sh
    git clone mmocchi/pycodemetrics
    cd pycodemetrics
    ```

2. Poetryを使用して依存関係をインストールします。

    ```sh
    uv pip install -e ".[dev]"
    ```

## 開発用コマンド

開発中に使用できる主なコマンドは以下の通りです：

- テストの実行:
  ```sh
  uv run pytest
  ```

- リンターの実行:
  ```sh
  uv run ruff check .
  ```

- 型チェックの実行:
  ```sh
  uv run mypy src
  ```

## コードスタイル

このプロジェクトでは、PEP 8に準拠したコードスタイルを採用しています。コードを提出する前に、必ずリンターと型チェックを実行してください。
