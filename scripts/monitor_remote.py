import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = REPO_ROOT / "logs"
LOG_PATH = LOG_DIR / "git_monitor.log"
PYTHON_EXE = Path(r"D:\Anaconda3\envs\datacompenv\python.exe")


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}"
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line, flush=True)


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = result.stdout.strip()
    if output:
        for line in output.splitlines():
            log(f"$ {' '.join(args)} :: {line}")
    if check and result.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed with exit code {result.returncode}")
    return result


def is_clean_worktree() -> bool:
    result = run(["git", "status", "--short"], check=True)
    return not result.stdout.strip()


def has_staged_changes() -> bool:
    result = run(["git", "diff", "--cached", "--name-only"], check=True)
    return bool(result.stdout.strip())


def validate_staged_changes() -> None:
    log("开始运行合并前检查")
    run(["git", "diff", "--check", "--cached"], check=True)
    result = run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], check=True)
    python_files = [line.strip() for line in result.stdout.splitlines() if line.strip().endswith(".py")]
    if python_files:
        log(f"Python 语法检查：{', '.join(python_files)}")
        run([str(PYTHON_EXE), "-m", "py_compile", *python_files], check=True)


def sync_main_from_origin() -> None:
    log("检查 origin/main")
    run(["git", "fetch", "origin", "--prune"], check=True)
    result = run(["git", "rev-list", "--left-right", "--count", "main...origin/main"], check=True)
    ahead_text, behind_text = result.stdout.strip().split()
    ahead = int(ahead_text)
    behind = int(behind_text)
    log(f"main 与 origin/main 差异：ahead={ahead} behind={behind}")

    if ahead > 0:
        log("本地 main 有未推送提交，先推送")
        run(["git", "push", "origin", "main"], check=True)

    if behind > 0:
        if not is_clean_worktree():
            raise RuntimeError("工作区不干净，跳过 origin/main 快进")
        log("快进合并 origin/main")
        run(["git", "merge", "--ff-only", "origin/main"], check=True)


def list_open_prs() -> list[dict]:
    result = run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--base",
            "main",
            "--json",
            "number,title,headRefName,mergeable,url,updatedAt",
        ],
        check=True,
    )
    return json.loads(result.stdout or "[]")


def merge_open_prs() -> None:
    prs = list_open_prs()
    if not prs:
        log("没有开放 PR")
        return

    for pr in prs:
        number = str(pr["number"])
        title = pr.get("title", "")
        log(f"检查 PR #{number}：{title} [{pr.get('mergeable')}] {pr.get('url')}")
        if pr.get("mergeable") == "CONFLICTING":
            log(f"PR #{number} 存在冲突，跳过")
            continue

        if not is_clean_worktree():
            raise RuntimeError("工作区不干净，停止处理 PR")

        branch_name = f"codex/auto-pr-{number}"
        run(["git", "switch", "main"], check=True)
        run(["git", "fetch", "origin", f"pull/{number}/head:{branch_name}", "--force"], check=True)

        try:
            log(f"尝试本地合并 PR #{number}")
            merge_result = run(["git", "merge", "--no-ff", "--no-commit", branch_name], check=False)
            if merge_result.returncode != 0:
                raise RuntimeError("merge failed")
            if not has_staged_changes():
                log(f"PR #{number} 没有产生待提交改动，跳过")
                run(["git", "merge", "--abort"], check=False)
                continue

            validate_staged_changes()
            safe_title = title.replace('"', "'")
            run(["git", "commit", "-m", f"合并 PR #{number}：{safe_title}"], check=True)
            run(["git", "push", "origin", "main"], check=True)
            log(f"PR #{number} 已合并并推送")
        except Exception as exc:
            log(f"PR #{number} 处理失败：{exc}")
            run(["git", "merge", "--abort"], check=False)
            run(["git", "reset", "--hard", "HEAD"], check=False)


def monitor_cycle() -> None:
    log("===== 开始检查 =====")
    try:
        sync_main_from_origin()
        merge_open_prs()
    except Exception as exc:
        log(f"本轮检查失败：{exc}")
    log("===== 检查结束 =====")


def main() -> int:
    parser = argparse.ArgumentParser(description="每隔一段时间检查 GitHub main 和开放 PR。")
    parser.add_argument("--interval-minutes", type=int, default=30)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    log(f"远端监控启动：interval={args.interval_minutes} once={args.once}")
    while True:
        monitor_cycle()
        if args.once:
            return 0
        time.sleep(args.interval_minutes * 60)


if __name__ == "__main__":
    raise SystemExit(main())
