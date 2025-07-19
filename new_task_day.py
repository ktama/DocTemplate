#!/usr/bin/env python3
"""
new_task_day.py
────────────────────────────────────────────────────────────────────────────
■ 目的
  - Markdown で管理する日次タスクファイル (tasks/YYYY-MM-DD.md) を自動生成
  - 最新ファイルの未完了タスクを“コピー”で持ち越し   ※元ファイルは残る
  - デフォルトで Git に add ＆ commit（push は任意）

■ 特徴
  - 休日を挟んでも “最新日のタスク” を探して持ち越し
  - 優先度アイコンは色付き絵文字 🟥🟧🟩⬜
  - ファイル冒頭に「優先度／緊急度／重要度」のチートシートを自動挿入
  - Windows / macOS / Linux 共通（Python 3.8+）

■ 使い方（コマンドプロンプト / PowerShell / ターミナル）
  # 今日のファイルを作成・タスク持ち越し・Git コミット
  python new_task_day.py

  # 指定日ファイルを生成（2025-07-18）
  python new_task_day.py 2025-07-18

  # 持ち越しせず新規ファイルのみ作成
  python new_task_day.py --no-carry

  # Git コミットしたくない場合
  python new_task_day.py --no-commit
────────────────────────────────────────────────────────────────────────────
"""

import argparse
import datetime as dt
import pathlib
import subprocess
import sys
import re
import shutil

# ========== 設定 =============================================================
ROOT = pathlib.Path(__file__).resolve().parent   # スクリプト置き場＝リポジトリ root
TASK_DIR = ROOT / "tasks"                        # タスクフォルダ

TEMPLATE_HEAD = """\
## 🗂 タスク一覧（{date}）

<!-- ========== Priority Cheatsheet (Color) =========== -->
<!-- 🟥 High   = 今週中に着手しないと成果 or 納期に直結 -->
<!-- 🟧 Medium = 今週内に対応できればOK。来週以降でも可 -->
<!-- 🟩 Low    = 重要度が低い / 割り込み許容            -->
<!-- ⬜ Hold   = 着手禁止・前提待ち                     -->
<!-- Urgency : 3=直ちに対応 / 2=数日以内 / 1=余裕あり    -->
<!-- Impact  : 3=失敗で大影響 / 2=中程度の影響 / 1=軽微  -->
<!-- =================================================== -->

"""

# ========== ヘルパ関数 =======================================================
def latest_task_file(before: dt.date) -> pathlib.Path | None:
    """`before` より前で一番新しい tasks/YYYY-MM-DD.md を返す"""
    for days in range(1, 1000):  # 最大 1000 日さかのぼり
        p = TASK_DIR / f"{before - dt.timedelta(days=days)}.md"
        if p.exists():
            return p
    return None


def load_unfinished(path: pathlib.Path) -> list[str]:
    """
    前回ファイルから「未完了タスクブロック」を丸ごと抽出して返す関数

    - 先頭が '- [ ]' で始まる行をタスク開始と判定
    - その直後に続く **インデント付き行（2空白以上で始まり、空行でない）** を
      同じタスクの詳細行としてまとめて取得
    - 完了タスク（'- [x]') は無視
    """
    if not path or not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    blocks: list[str] = []
    grab = False

    for ln in lines:
        # 1) 未完了タスクの開始行を検出
        if re.match(r"^\s*-\s\[\s\]\s", ln):
            grab = True
            blocks.append(ln)
            continue

        # 2) 直前が未完了タスクなら、インデント行を同ブロックとして追加
        if grab and re.match(r"^\s{2,}\S", ln):
            blocks.append(ln)
        else:
            # インデント条件を満たさなくなったらブロック終了
            grab = False

    return blocks


def git_is_available() -> bool:
    """git コマンドが使えるか判定"""
    return shutil.which("git") is not None


def git_commit(file_path: pathlib.Path, date: dt.date):
    """Git へ add & commit"""
    if not git_is_available():
        print("⚠️  Git 未検出。コミットをスキップ")
        return
    subprocess.run(["git", "add", str(file_path)], check=True)
    subprocess.run(["git", "commit", "-m", f"Start {date} tasks"], check=True)
    # push したい場合は次行を有効化
    # subprocess.run(["git", "push"], check=True)
    print("Committed to Git.")

# ========== main =============================================================
def main():
    ap = argparse.ArgumentParser(
        description="Generate daily task markdown (carry & commit by default).")
    ap.add_argument("date", nargs="?",
                    help="YYYY-MM-DD (default: today)")
    ap.add_argument("--no-carry", action="store_true",
                    help="未完了タスクを持ち越さない")
    ap.add_argument("--no-commit", action="store_true",
                    help="Git にコミットしない")
    args = ap.parse_args()

    # --- 日付決定 ------------------------------------------------------------
    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    today_path = TASK_DIR / f"{today}.md"
    today_path.parent.mkdir(parents=True, exist_ok=True)

    # --- 未完了タスク持ち越し -------------------------------------------------
    carry_tasks = []
    if not args.no_carry:
        prev = latest_task_file(today)
        carry_tasks = load_unfinished(prev)

    # --- ファイル生成 --------------------------------------------------------
    with today_path.open("w", encoding="utf-8") as f:
        f.write(TEMPLATE_HEAD.format(date=today))
        f.writelines(carry_tasks)

    print(f"Created {today_path.relative_to(ROOT)} "
          f"({len(carry_tasks)} carried tasks)")

    # --- Git コミット --------------------------------------------------------
    if not args.no_commit:
        try:
            git_commit(today_path, today)
        except subprocess.CalledProcessError as e:
            print("⚠️  Git 実行失敗:", e, file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
