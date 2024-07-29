# PyCodeMetrics

PyCodeMetricsは、Pythonプロジェクトのコードメトリクスを収集および解析するためのツールです。

## 概要

このプロジェクトは、Pythonコードの複雑さ、品質、およびその他のメトリクスを評価するためのツールを提供します。以下の機能を含みます：

- Gitリポジトリからのログ解析
- コードの認知的複雑度の計算
- 各種メトリクスの収集とレポート生成

## for Users

### Install

### Usage


## for Contributers
### Setup

このプロジェクトはPoetryを使用して管理されています。以下の手順でインストールしてください：

1. リポジトリをクローンします。

    ```sh
    git clone <repository-url>
    cd pycodemetrics
    ```

2. Poetryを使用して依存関係をインストールします。

    ```sh
    poetry install
    ```

### Usage

#### CLI

`main.py`を実行して、メトリクスを収集および解析します。

```sh
poetry run pycodemetrics analyze --dir_path .