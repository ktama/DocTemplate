# DocTemplate

DocTemplateは、Pandocを利用してMarkdownファイルを美しいHTMLドキュメントに変換するためのテンプレートプロジェクトです。

## 特長
- Pandocのカスタムテンプレート（`template.html`）を利用
- Mermaid.jsによるダイアグラム描画（`mermaid.lua`）
- Prism.jsによるシンタックスハイライト（`prism-theme.css`）
- 独自のスタイル（`style.css`）

## 必要なもの
- [Pandoc](https://pandoc.org/)（インストール必須）

## 使い方
1. 変換したいMarkdownファイル（例: `sample.md`）を用意します。
2. VS Codeのタスク「Pandoc: Markdown to HTML」を実行するか、以下のコマンドをPowerShellで実行します：

   ```powershell
   pandoc --defaults=defaults.yaml sample.md -o sample.html
   ```

3. 生成されたHTMLファイル（例: `sample.html`）をブラウザで開きます。

## ファイル構成
- `defaults.yaml` : Pandocのデフォルト設定
- `template.html` : HTMLテンプレート
- `mermaid.lua` : Mermaid.js用フィルタ
- `prism-theme.css` : Prism.js用テーマ
- `style.css` : カスタムスタイル
- `sample.md` : サンプルMarkdown
- `sample.html` : サンプル出力

## ライセンス
このプロジェクトはMITライセンスです。
