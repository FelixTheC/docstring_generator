import sys
from pathlib import Path


def print_results(
    all_results: dict[str, dict], strict: bool = False, threshold: float | None = None
):
    export_json(all_results, strict, threshold)
    """Renders a pure ASCII table from the metrics dictionary."""
    # Define table structure and column widths
    header_fmt = "| {:<30} | {:>7} | {:>8} | {:>7} | {:>7} | {:>6} |"
    row_fmt = "| {:<30} | {:>7} | {:>8} | {:>7} | {:>7} | {:>5.1f}% |"
    divider = (
        "+"
        + "-" * 32
        + "+"
        + "-" * 9
        + "+"
        + "-" * 10
        + "+"
        + "-" * 9
        + "+"
        + "-" * 9
        + "+"
        + "-" * 8
        + "+"
    )

    print("\n" + divider)
    print(header_fmt.format("File Path", "Checked", "Complete", "Partial", "Missing", "Score"))
    print(divider)

    total_checked = 0
    total_passing = 0

    for filepath, metrics in all_results.items():
        total = metrics.get("num_functions_checked", 0)
        if total == 0:
            continue

        comp = metrics.get("complete_docstrings", 0)
        part = metrics.get("partial_docstrings", 0)
        miss = metrics.get("no_docstrings", 0)

        # Apply strict mode evaluation logic
        passing_for_file = comp if strict else (comp + part)
        file_score = (passing_for_file / total) * 100

        total_checked += total
        total_passing += passing_for_file

        # Shorten filenames from the left if they exceed 30 chars
        display_name = filepath
        if len(display_name) > 30:
            display_name = "..." + display_name[-27:]

        print(row_fmt.format(display_name, total, comp, part, miss, file_score))

    print(divider)

    # Calculate summary numbers
    if total_checked > 0:
        overall_score = (total_passing / total_checked) * 100
        print(f"\nOverall System Score: {overall_score:.1f}%")
        if strict:
            print("Note: Strict mode active (Partial counted as missing)")

        if threshold is not None:
            if overall_score < threshold:
                sys.stderr.write("[X] FAILURE: Docstring coverage criteria not met.")
                return 1
            else:
                print("\n[V] SUCCESS: Docstring coverage passed threshold requirements.")
                return 0
    return 0


def export_json(all_results: dict[str, dict], strict: bool = False, threshold: float | None = None):
    data = {}

    total_checked = 0
    total_passing = 0
    overall_score = 0
    any_failed_threshold = False

    for filepath, metrics in all_results.items():
        total = metrics.get("num_functions_checked", 0)
        if total == 0:
            continue

        comp = metrics.get("complete_docstrings", 0)
        part = metrics.get("partial_docstrings", 0)
        miss = metrics.get("no_docstrings", 0)

        # Apply strict mode evaluation logic
        passing_for_file = comp if strict else (comp + part)
        file_score = (passing_for_file / total) * 100

        total_checked += total
        total_passing += passing_for_file

        if threshold and file_score < threshold:
            any_failed_threshold = True

        data[filepath] = {
            "total": total,
            "complete": comp,
            "partial": part,
            "missing": miss,
            "score": file_score,
        }

    if total_checked > 0:
        overall_score = (total_passing / total_checked) * 100

    result = {
        "overall_score": overall_score,
        "threshold": threshold,
        "passing": overall_score > threshold or not any_failed_threshold,
        "total_checked": total_checked,
        "total_passing": total_passing,
        "any_failed_threshold": any_failed_threshold,
        "files": data,
    }

    import json

    with Path(Path.cwd(), "gendocs_check_output.json").open("w") as output_file:
        json.dump(result, output_file, indent=4)
