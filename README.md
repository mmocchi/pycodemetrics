# PyCodeMetrics

PyCodeMetricsは、Pythonプロジェクトのコードメトリクスを収集および解析するためのツールです。

## 概要

このプロジェクトは、Pythonコードの複雑さ、品質、およびその他のメトリクスを評価するためのツールを提供します。以下の機能を含みます：

- Gitリポジトリからのログ解析
- コードの認知的複雑度の計算
- 各種メトリクスの収集とレポート生成

## インストール

PyCodeMetricsは以下のコマンドでインストールできます：

```sh
pip install pycodemetrics
```

## 使用方法

PyCodeMetricsを使用してプロジェクトを分析するには、以下のコマンドを実行します：

```sh
pycodemetrics analyze --path /path/to/your/project
```

このコマンドは指定されたディレクトリ内のPythonファイルを分析し、メトリクスのレポートを生成します。

## 開発

### 前提条件

開発には[Task](https://taskfile.dev/)が必要です。インストール方法は公式サイトを参照してください。

### 開発用タスク

プロジェクトではTaskfile.ymlを使用して開発タスクを管理しています：

```sh
# コードのリント
task lint

# コードのフォーマット
task format

# 自動修正とフォーマット
task fix

# 型チェック
task mypy

# テスト実行
task test

# カバレッジ付きテスト
task test-cov

# 全チェック実行（lint + mypy + test）
task check

# フォーマット後に全チェック実行
task dev
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細については[LICENSE](LICENSE)ファイルを参照してください。

## 貢献

プロジェクトへの貢献に興味がある場合は、[CONTRIBUTING.md](CONTRIBUTING.md)をご覧ください。
