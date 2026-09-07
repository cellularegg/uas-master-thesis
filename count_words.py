#!/usr/bin/env python3
"""Count thesis chapter words and compare them with the MDS guidelines.

The count is intentionally based on the chapter source files rather than the
generated PDF. Active table inputs are expanded before counting. LaTeX
commands, comments, citations/references, and math are excluded; visible
headings and prose are counted.

Run from the repository root:

    python3 count_words.py

Alternative chapter files can be supplied explicitly:

    python3 count_words.py --main path/to/main.tex

Each run also records one snapshot per calendar day in
``word_count_history.json`` and displays recent progress toward the hardcoded
7 September 2026 deadline.
"""

from __future__ import annotations

import argparse
import json
from math import ceil
import random
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path


# Reference values from MDS_Guidelines_MasterThesis_20230923.md, section B/C.
REFERENCE_TOTAL_WORDS = 9_000
DEADLINE = date(2026, 9, 7)
HISTORY_PATH = Path("word_count_history.json")
HISTORY_DAYS_TO_SHOW = 7
CONFETTI_PARTICLE_COUNT = 400
CONFETTI_DURATION_MS = 5_000
CONFETTI_FRAME_INTERVAL_MS = 16
_QT_APPLICATION = None
CHAPTER_REFERENCE_PERCENTAGES = {
    "introduction": 15.0,
    "methodology": 20.0,
    "results": 50.0,
    "discussion": 15.0,
}

INCLUDE_RE = re.compile(r"\\(?:include|input)\s*\{([^{}]+)\}")
APPENDIX_RE = re.compile(r"\\appendix\b")
TABLE_INPUT_RE = re.compile(r"\\input\s*\{(tables/[^{}]+)\}")
CHAPTER_TITLE_RE = re.compile(r"\\chapter(?:\[[^\]]*\])?\s*\{([^{}]*)\}", re.IGNORECASE)

# Commands whose arguments are metadata rather than visible paper text.
REFERENCE_COMMAND_RE = re.compile(
    r"\\(?:cite[a-z]*|[Pp]ageref|[Rr]ef|eqref|label|url|path)\*?"
    r"(?:\[[^\]]*\])?(?:\{[^{}]*\})+"
)

MATH_ENVIRONMENTS = (
    "equation",
    "equation*",
    "align",
    "align*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "displaymath",
    "math",
)
MATH_ENVIRONMENT_RE = re.compile(
    r"\\begin\{(?:"
    + "|".join(re.escape(name) for name in MATH_ENVIRONMENTS)
    + r")\}.*?\\end\{(?:"
    + "|".join(re.escape(name) for name in MATH_ENVIRONMENTS)
    + r")\}",
    re.DOTALL,
)

WORD_RE = re.compile(r"(?u)\b[\w]+(?:[-’'][\w]+)*\b")
ENVIRONMENT_RE = re.compile(r"\\(?:begin|end)\s*\{[^{}]*\}(?:\s*\[[^\]]*\])?")
BRACED_ARGUMENT_RE = r"\{(?:[^{}]|\{[^{}]*\})*\}"
TABLE_ENVIRONMENT_BEGIN_RE = re.compile(
    r"\\begin\s*\{(?:tabular|tabularx|longtable|xltabular|array)\}"
    r"(?:\s*\[[^\]]*\])?"
    r"(?:\s*" + BRACED_ARGUMENT_RE + r"){1,2}"
)


class Colors:
    """ANSI colors used for terminal output."""

    RESET = "\033[0m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    ORANGE = "\033[38;5;208m"
    LIGHT_GREEN = "\033[92m"
    GREEN = "\033[32m"
    RED = "\033[31m"


def colorize(value: str, color: str, enabled: bool) -> str:
    return f"{color}{value}{Colors.RESET}" if enabled else value


def remove_comments(text: str) -> str:
    """Remove LaTeX comments while preserving escaped percent signs."""

    uncommented_lines = []
    for line in text.splitlines():
        comment_start = None
        for index, character in enumerate(line):
            if character != "%":
                continue
            backslashes = 0
            preceding = index - 1
            while preceding >= 0 and line[preceding] == "\\":
                backslashes += 1
                preceding -= 1
            if backslashes % 2 == 0:
                comment_start = index
                break
        uncommented_lines.append(line if comment_start is None else line[:comment_start])
    return "\n".join(uncommented_lines)


def latex_to_text(source: str) -> str:
    """Return visible-ish text from a LaTeX source fragment."""

    text = remove_comments(source)

    # Remove mathematical material before stripping commands inside it.
    text = MATH_ENVIRONMENT_RE.sub(" ", text)
    text = re.sub(r"\\\(.*?\\\)", " ", text, flags=re.DOTALL)
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.DOTALL)
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.DOTALL)
    text = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", " ", text, flags=re.DOTALL)

    # Keep the displayed label of a hyperlink, but remove its URL.
    text = re.sub(r"\\href\s*\{[^{}]*\}\s*\{([^{}]*)\}", r"\1", text)
    text = REFERENCE_COMMAND_RE.sub(" ", text)

    # Environment names and table column declarations are structural LaTeX,
    # not visible document text.
    text = TABLE_ENVIRONMENT_BEGIN_RE.sub(" ", text)
    text = ENVIRONMENT_RE.sub(" ", text)

    # Remove command names and structural delimiters, retaining text in
    # ordinary command arguments, e.g. \textit{important} -> important.
    text = re.sub(r"\\[A-Za-z@]+\*?", " ", text)
    text = re.sub(r"[{}\[\]]", " ", text)
    return text


def count_words(source: str) -> int:
    """Count visible word-like tokens, excluding numeric-only tokens."""

    return sum(any(character.isalpha() for character in token) for token in WORD_RE.findall(latex_to_text(source)))


def expand_table_inputs(source: str, document_root: Path, active_paths: set[Path] | None = None) -> str:
    """Expand active table inputs so their visible contents are counted."""

    active_paths = set() if active_paths is None else active_paths
    source = remove_comments(source)

    def replace_input(match: re.Match[str]) -> str:
        table_path = (document_root / Path(match.group(1))).with_suffix(".tex").resolve()
        if table_path in active_paths:
            return ""
        if not table_path.is_file():
            return match.group(0)
        table_source = table_path.read_text(encoding="utf-8")
        return expand_table_inputs(table_source, document_root, active_paths | {table_path})

    return TABLE_INPUT_RE.sub(replace_input, source)


def truncate_before_appendix(comment_free_text: str) -> str:
    """Drop everything from \\appendix onward; it marks non-body appendix material."""

    appendix_match = APPENDIX_RE.search(comment_free_text)
    return comment_free_text if appendix_match is None else comment_free_text[: appendix_match.start()]


def count_source_words(source_path: Path, document_root: Path) -> int:
    """Count words in a source file, including active inputs from the tables folder."""

    source = truncate_before_appendix(remove_comments(source_path.read_text(encoding="utf-8")))
    return count_words(expand_table_inputs(source, document_root))


def discover_chapters(main_path: Path) -> list[Path]:
    text = truncate_before_appendix(remove_comments(main_path.read_text(encoding="utf-8")))
    chapters = []
    for included_path in INCLUDE_RE.findall(text):
        chapter_path = (main_path.parent / included_path).with_suffix(".tex")
        if chapter_path.exists() and chapter_path not in chapters:
            chapters.append(chapter_path)
    return chapters


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip().casefold()


def chapter_title(chapter_path: Path) -> str:
    source = remove_comments(chapter_path.read_text(encoding="utf-8"))
    match = CHAPTER_TITLE_RE.search(source)
    return match.group(1).strip() if match else chapter_path.stem


def signed_number(value: int) -> str:
    return f"{value:+,}"


def progress_bar(percentage: float, width: int = 30) -> str:
    """Render a fixed-width progress bar while preserving uncapped percentages."""

    filled = min(max(round(width * percentage / 100), 0), width)
    return f"[{'#' * filled}{'-' * (width - filled)}]"


def completion_color(percentage: float) -> str:
    """Return the terminal color for a completion percentage."""

    if percentage >= 100:
        return Colors.GREEN
    if percentage >= 75:
        return Colors.LIGHT_GREEN
    if percentage >= 50:
        return Colors.YELLOW
    if percentage >= 25:
        return Colors.ORANGE
    return Colors.RED


def load_history(path: Path) -> dict[str, dict[str, object]]:
    """Load saved daily counts, or return an empty history on first run."""

    if not path.exists():
        return {}

    with path.open(encoding="utf-8") as history_file:
        history = json.load(history_file)
    if not isinstance(history, dict):
        raise ValueError(f"History file must contain a JSON object: {path}")
    return history


def save_history(
    path: Path,
    history: dict[str, dict[str, object]],
    snapshot_date: date,
    rows: list[tuple[str, Path, int, float | None]],
) -> None:
    """Save or replace today's snapshot."""

    history[snapshot_date.isoformat()] = {
        "total": sum(row[2] for row in rows),
        "target": REFERENCE_TOTAL_WORDS,
        "chapters": {title: words for title, _path, words, _percentage in rows},
    }
    path.write_text(json.dumps(history, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_progress(
    actual_total: int,
    history: dict[str, dict[str, object]],
    today: date,
    use_color: bool,
    show_history: bool,
) -> bool:
    """Print deadline progress and the most recent saved snapshots."""

    remaining_words = max(REFERENCE_TOTAL_WORDS - actual_total, 0)
    days_remaining = (DEADLINE - today).days
    progress = 100 * actual_total / REFERENCE_TOTAL_WORDS
    daily_quota_met = False

    history_rows = []
    for recorded_date, snapshot in sorted(history.items()):
        try:
            recorded_total = int(snapshot["total"])  # type: ignore
            parsed_date = date.fromisoformat(recorded_date)
        except (KeyError, TypeError, ValueError):
            continue
        history_rows.append((parsed_date, recorded_total))

    previous_day_rows = [
        (recorded_date, recorded_total) for recorded_date, recorded_total in history_rows if recorded_date < today
    ]
    previous_day_total = previous_day_rows[-1][1] if previous_day_rows else None

    print()
    print(f"Deadline: {DEADLINE.isoformat()} ({days_remaining} days remaining)")
    print(f"Progress: {actual_total:,}/{REFERENCE_TOTAL_WORDS:,} words ({progress:.1f}%)")
    print(f"Remaining: {remaining_words:,} words")

    daily_quota = None
    if remaining_words == 0:
        print(colorize("Target reached.", Colors.GREEN, use_color))
        daily_quota = 0
    elif days_remaining > 0:
        daily_quota = (remaining_words + days_remaining - 1) // days_remaining
        print(f"Required pace: about {daily_quota:,} words/day")
    elif days_remaining == 0:
        daily_quota = remaining_words
        print(f"Due today: {remaining_words:,} words remaining")
    else:
        print(colorize("Deadline has passed.", Colors.RED, use_color))

    daily_quota_percentage = None
    daily_quota_color = Colors.YELLOW
    if daily_quota is not None:
        if previous_day_total is None:
            print("Words until daily quota: unavailable (no earlier daily snapshot)")
        else:
            words_written_today = max(actual_total - previous_day_total, 0)
            words_until_quota = max(daily_quota - words_written_today, 0)
            percentage_of_quota = 100 * words_written_today / daily_quota if daily_quota else 0
            percentage_until_quota = 100 * words_until_quota / daily_quota if daily_quota else 0
            daily_quota_percentage = percentage_of_quota
            if words_until_quota == 0:
                daily_quota_met = True
                quota_color = Colors.GREEN
            elif percentage_of_quota <= 50:
                quota_color = Colors.RED
            else:
                quota_color = Colors.YELLOW
            daily_quota_color = quota_color
            print(
                colorize(
                    f"Words until daily quota: {words_until_quota:,} ({percentage_until_quota:.1f}% remaining)",
                    quota_color,
                    use_color,
                )
                + f"  [written today: {words_written_today:,}]"
            )

    history_rows = history_rows[-HISTORY_DAYS_TO_SHOW:]
    if not show_history or not history_rows:
        if daily_quota_percentage is not None:
            print(
                colorize(
                    f"{progress_bar(daily_quota_percentage)} {daily_quota_percentage:.1f}%",
                    daily_quota_color,
                    use_color,
                )
            )
        return daily_quota_met

    print()
    print(f"Recent history (last {HISTORY_DAYS_TO_SHOW} snapshots):")
    print(f"{'Date':<12} {'Total':>10} {'Change':>10}")
    print("-" * 34)
    previous_total = None
    for recorded_date, recorded_total in history_rows:
        change = "—" if previous_total is None else signed_number(recorded_total - previous_total)
        print(f"{recorded_date.isoformat():<12} {recorded_total:>10,} {change:>10}")
        previous_total = recorded_total

    if len(history_rows) >= 2:
        first_date, first_total = history_rows[0]
        last_date, last_total = history_rows[-1]
        elapsed_days = (last_date - first_date).days
        if elapsed_days > 0:
            average_per_day = (last_total - first_total) / elapsed_days
            print(f"Average recent pace: {average_per_day:+,.0f} words/day")
            if average_per_day > 0 and remaining_words > 0:
                projected_days = ceil(remaining_words / average_per_day)
                projected_date = last_date + timedelta(days=projected_days)
                print(f"Projected completion at this pace: {projected_date.isoformat()}")

    if daily_quota_percentage is not None:
        print(
            colorize(
                f"{progress_bar(daily_quota_percentage)} {daily_quota_percentage:.1f}%",
                daily_quota_color,
                use_color,
            )
        )

    return daily_quota_met


def show_confetti_overlay() -> None:
    """Show a temporary, click-through confetti overlay on the primary screen."""

    try:
        from PyQt6.QtCore import QEvent, QTimer, Qt
        from PyQt6.QtGui import QColor, QPainter
        from PyQt6.QtWidgets import QApplication, QWidget
    except ImportError as error:
        print(f"warning: could not show confetti overlay: {error}", file=sys.stderr)
        return

    class ConfettiOverlay(QWidget):
        """Transparent top-level window that animates falling confetti."""

        COLORS = ("red", "yellow", "blue", "green", "orange", "purple")

        def __init__(self, geometry) -> None:
            super().__init__()
            self.setGeometry(geometry)
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
                | Qt.WindowType.WindowDoesNotAcceptFocus
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

            self._particles = [self._create_particle() for _ in range(CONFETTI_PARTICLE_COUNT)]

            self._animation_timer = QTimer(self)
            self._animation_timer.timeout.connect(self._animate)
            self._animation_timer.start(CONFETTI_FRAME_INTERVAL_MS)

            self._close_timer = QTimer(self)
            self._close_timer.setSingleShot(True)
            self._close_timer.timeout.connect(self._finish)
            self._close_timer.start(CONFETTI_DURATION_MS)

        def _create_particle(self) -> dict[str, object]:
            """Create a particle at a random position above the screen."""

            size = random.randint(5, 12)
            return {
                "x": random.uniform(0, max(self.width() - size, 0)),
                "y": random.uniform(-self.height(), 0),
                "size": size,
                "dx": random.uniform(-2, 2),
                "dy": random.uniform(3, 8),
                "color": QColor(random.choice(self.COLORS)),
            }

        def _animate(self) -> None:
            for particle in self._particles:
                particle["x"] += particle["dx"]
                particle["y"] += particle["dy"]

                if particle["y"] > self.height():
                    particle.update(self._create_particle())

            self.update()

        def _finish(self) -> None:
            self._animation_timer.stop()
            self.hide()
            application = QApplication.instance()
            if application is not None:
                application.quit()

        def paintEvent(self, _event) -> None:
            painter = QPainter(self)
            painter.setPen(Qt.PenStyle.NoPen)
            for particle in self._particles:
                painter.setBrush(particle["color"])
                size = particle["size"]
                painter.drawRect(round(particle["x"]), round(particle["y"]), size, size)

    global _QT_APPLICATION

    application = None
    overlay = None
    try:
        application = QApplication.instance()
        if application is None:
            application = QApplication(sys.argv)
            _QT_APPLICATION = application
        screen = application.primaryScreen()
        if screen is None:
            print("warning: could not show confetti overlay: no primary screen detected", file=sys.stderr)
            return

        overlay = ConfettiOverlay(screen.geometry())
        overlay.show()
        overlay.raise_()
        application.exec()
    except Exception as error:
        print(f"warning: could not show confetti overlay: {error}", file=sys.stderr)
    finally:
        if overlay is not None:
            overlay.hide()
            overlay.deleteLater()
        if application is not None:
            application.processEvents()
            application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
            application.processEvents()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--main",
        type=Path,
        default=Path("main.tex"),
        help="main LaTeX file used to discover included chapters (default: main.tex)",
    )
    color_group = parser.add_mutually_exclusive_group()
    color_group.add_argument(
        "--color",
        action="store_true",
        help="force ANSI colors even when stdout is not a terminal",
    )
    color_group.add_argument(
        "--no-color",
        action="store_true",
        help="disable ANSI colors",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="recount and refresh the output every second until interrupted",
    )
    parser.add_argument(
        "--confetti",
        action="store_true",
        help="show the confetti overlay immediately and exit without recounting",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="hide the recent history section",
    )
    parser.add_argument(
        "chapters",
        nargs="*",
        type=Path,
        help="optional chapter files; otherwise chapters are discovered from --main",
    )
    return parser


def run_once(args: argparse.Namespace, use_color: bool) -> tuple[int, bool]:
    try:
        chapters = args.chapters or discover_chapters(args.main)
        if not chapters:
            raise ValueError(f"No chapter files found in {args.main}")

        rows = []
        for chapter_path in chapters:
            if not chapter_path.exists():
                raise ValueError(f"Chapter file does not exist: {chapter_path}")
            title = chapter_title(chapter_path)
            words = count_source_words(chapter_path, args.main.parent)
            percentage = CHAPTER_REFERENCE_PERCENTAGES.get(normalize_title(title))
            rows.append((title, chapter_path, words, percentage))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2, False

    actual_total = sum(row[2] for row in rows)
    print(f"Guideline: ~{REFERENCE_TOTAL_WORDS:,} words (excluding references)")
    print("Count: LaTeX comments, commands, citations/references, math, and numeric-only tokens excluded")
    print()
    print(f"{'Chapter':<24} {'Words':>8} {'Reference':>12} {'Difference':>12} {'Share':>8} {'Completion':>12}")
    print("-" * 85)

    for title, path, words, percentage in rows:
        if percentage is None:
            reference = "n/a"
            difference = "n/a"
        else:
            reference_words = round(REFERENCE_TOTAL_WORDS * percentage / 100)
            reference = f"~{reference_words:,} ({percentage:g}%)"
            difference = signed_number(words - reference_words)
        share = f"{100 * words / actual_total:.1f}%" if actual_total else "n/a"
        completion_percentage = 100 * words / reference_words if percentage is not None else None
        completion = f"{completion_percentage:.1f}%" if completion_percentage is not None else "n/a"
        colored_words = colorize(f"{words:>8,}", Colors.CYAN, use_color)
        colored_reference = colorize(f"{reference:>12}", Colors.YELLOW, use_color)
        if percentage is None:
            colored_difference = difference.rjust(12)
        else:
            difference_color = Colors.GREEN if words >= reference_words else Colors.RED
            colored_difference = colorize(f"{difference:>12}", difference_color, use_color)
        colored_share = colorize(f"{share:>8}", Colors.CYAN, use_color)
        completion_color_value = (
            completion_color(completion_percentage) if completion_percentage is not None else Colors.CYAN
        )
        colored_completion = colorize(f"{completion:>12}", completion_color_value, use_color)
        print(
            f"{title:<24} {colored_words} {colored_reference} {colored_difference} {colored_share} {colored_completion}"
        )
        if percentage is None:
            print(f"  warning: no matching guideline reference for {path}", file=sys.stderr)

    print("-" * 85)
    print(
        f"{'Paper total':<24} "
        f"{colorize(f'{actual_total:>8,}', Colors.CYAN, use_color)} "
        f"{colorize(('~' + format(REFERENCE_TOTAL_WORDS, ',')).rjust(12), Colors.YELLOW, use_color)} "
        f"{colorize(signed_number(actual_total - REFERENCE_TOTAL_WORDS).rjust(12), Colors.RED if actual_total < REFERENCE_TOTAL_WORDS else Colors.GREEN, use_color)} "
        f"{'':>8} {colorize(f'{100 * actual_total / REFERENCE_TOTAL_WORDS:.1f}%'.rjust(12), completion_color(100 * actual_total / REFERENCE_TOTAL_WORDS), use_color)}"
    )

    today = date.today()
    try:
        history = load_history(HISTORY_PATH)
        save_history(HISTORY_PATH, history, today, rows)
    except (OSError, ValueError) as error:
        print(f"warning: could not update {HISTORY_PATH}: {error}", file=sys.stderr)
        history = {}
    daily_quota_met = print_progress(actual_total, history, today, use_color, show_history=not args.no_history)
    return 0, daily_quota_met


def clear_screen() -> None:
    """Clear the terminal before a watch-mode refresh."""

    # Clear the visible screen and scrollback, then move the cursor home.
    print("\033[2J\033[3J\033[H", end="", flush=True)


def main() -> int:
    args = build_parser().parse_args()
    use_color = args.color or (sys.stdout.isatty() and not args.no_color)

    if args.confetti:
        show_confetti_overlay()
        return 0

    if not args.watch:
        result, daily_quota_met = run_once(args, use_color)
        if result == 0 and daily_quota_met:
            show_confetti_overlay()
        return result

    quota_celebrated = False
    try:
        while True:
            clear_screen()
            result, daily_quota_met = run_once(args, use_color)
            if result != 0:
                return result
            if daily_quota_met:
                if not quota_celebrated:
                    show_confetti_overlay()
                    quota_celebrated = True
            else:
                quota_celebrated = False
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
