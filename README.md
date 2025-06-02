# PyCodeMetrics

PyCodeMetricsは、Pythonプロジェクトのコードメトリクスを収集および解析するためのツールです。

## 概要

このプロジェクトは、Pythonコードの複雑さ、品質、およびその他のメトリクスを評価するためのツールを提供します。以下の機能を含みます：

- Pythonファイルの静的解析とメトリクス計算
- コードホットスポットの分析
- コミッターによる分析
- 複数の出力形式（TABLE、JSON、CSV）
- 並列処理によるパフォーマンス最適化

## インストール

PyCodeMetricsは以下のコマンドでインストールできます：

```sh
pip install pycodemetrics
```

## 使用方法

### Pythonコードメトリクス分析

指定したパス内のPythonファイルを分析し、コード品質メトリクスを取得します：

```sh
# 基本的な使用方法
pycodemetrics analyze /path/to/your/project

# Gitリポジトリを考慮した分析
pycodemetrics analyze /path/to/your/project --with-git-repo

# 出力形式とエクスポートオプション
pycodemetrics analyze /path/to/your/project --format json --export results.json

# 表示列とフィルターの指定
pycodemetrics analyze /path/to/your/project --columns "file_path,cognitive_complexity" --limit 20 --code-type product
```

### ホットスポット分析

コードの変更頻度と複雑度から問題のある部分を特定します：

```sh
# 基本的なホットスポット分析
pycodemetrics hotspot /path/to/git/repository

# 並列処理とエクスポート
pycodemetrics hotspot /path/to/git/repository --workers 4 --export hotspots.csv --format csv
```

### コミッター分析

開発者ごとのコード変更パターンを分析します：

```sh
# コミッター分析
pycodemetrics committer /path/to/git/repository

# 出力制限とフィルター
pycodemetrics committer /path/to/git/repository --limit 10 --code-type all
```

## コマンドオプション

### 共通オプション

- `--format`: 出力形式（table, json, csv）
- `--export`: 結果をファイルにエクスポート
- `--export-overwrite`: エクスポートファイルの上書きを許可
- `--columns`: 表示する列を指定（カンマ区切り）
- `--limit`: 表示する行数の制限（0で制限なし）
- `--code-type`: コードタイプでフィルター（product, test, all）
- `--workers`: 並列処理のワーカー数

### analyze専用オプション

- `--with-git-repo`: Gitリポジトリ内のファイルを対象とする

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細については[LICENSE](LICENSE)ファイルを参照してください。

## 貢献

プロジェクトへの貢献に興味がある場合は、[CONTRIBUTING.md](CONTRIBUTING.md)をご覧ください。
