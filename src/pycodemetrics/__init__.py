"""PyCodeMetrics package.

このパッケージは、Pythonプロジェクトのコードメトリクスを収集および解析するためのツールを提供します。

主な機能:
    - Gitリポジトリからのログ解析
    - コードの認知的複雑度の計算
    - 各種メトリクスの収集とレポート生成
    - ホットスポット分析
    - コミッター分析

使用方法:
    コマンドラインから使用:
        $ pycodemetrics analyze --path /path/to/your/project

    プログラムから使用:
        from pycodemetrics.metrics.py.python_metrics import compute_metrics
        metrics = compute_metrics(code)
"""
