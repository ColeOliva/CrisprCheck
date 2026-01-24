
import argparse
import csv

from . import scoring, search
from .visualization import plot_efficiency, print_summary_statistics


def _write_csv(out_path, rows, fieldnames):
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            # filter out any extra keys so DictWriter doesn't raise
            row_filtered = {k: r.get(k, "") for k in fieldnames}
            writer.writerow(row_filtered)


def _format_rows_for_table(rows, fields):
    # prepare string table rows
    table = []
    for r in rows:
        row = []
        for f in fields:
            v = r.get(f, "")
            if isinstance(v, list):
                v = ",".join(str(x) for x in v)
            elif isinstance(v, float):
                v = f"{v:.2f}"
            row.append(str(v))
        table.append(row)
    return table


def _print_pretty_table(rows, fields):
    table = _format_rows_for_table(rows, fields)
    # compute column widths
    widths = [max(len(h), *(len(r[i]) for r in table)) for i, h in enumerate(fields)]
    # header
    header = "  ".join(h.ljust(widths[i]) for i, h in enumerate(fields))
    print(header)
    print("  ".join("-" * w for w in widths))
    for r in table:
        print("  ".join(r[i].ljust(widths[i]) for i in range(len(fields))))


def search_command(args):
    hits = search.scan_fasta_for_guide(args.guide, args.fasta, pam=args.pam, max_mismatches=args.max_mismatches)
    # score and sort
    score_funcs = {
        "pw": scoring.position_weighted_score,
        "mit": scoring.mit_like_score,
        "cfd": scoring.cfd_score,
        "cfd_full": scoring.cfd_score_full,
    }
    method = getattr(args, "score_method", "pw")
    func = score_funcs.get(method, scoring.position_weighted_score)
    for h in hits:
        # compute all internal scores for completeness
        h["score_pw"] = scoring.position_weighted_score(args.guide, h["target_seq"])
        h["score_mit"] = scoring.mit_like_score(args.guide, h["target_seq"])
        h["score_cfd"] = scoring.cfd_score(args.guide, h["target_seq"], pam=args.pam)
        # user-facing unified score
        h["score"] = func(args.guide, h["target_seq"]) if method != "cfd" else func(args.guide, h["target_seq"], pam=args.pam)

    # sort by the selected score descending
    hits.sort(key=lambda x: x["score"], reverse=True)
    fields = ["seq_id", "start", "end", "strand", "target_seq", "mismatches", "mismatch_positions", "score"]
    out = args.out or "results.csv"
    _write_csv(out, hits, fields)

    if getattr(args, "pretty", False):
        _print_pretty_table(hits, fields)

    print(f"Wrote {len(hits)} hits to {out}")


def main():
    parser = argparse.ArgumentParser(prog="crispr-check")
    sub = parser.add_subparsers(dest="cmd")
    p_search = sub.add_parser("search", help="Search for off-targets for a guide in a FASTA")
    p_search.add_argument("--guide", required=True, help="Guide RNA sequence (required)")
    p_search.add_argument("--pam", default="NGG", help="PAM sequence (default: NGG)")
    p_search.add_argument("--fasta", required=True, help="Path to input FASTA file (required)")
    p_search.add_argument("--out", default="results.csv", help="Output CSV file (default: results.csv)")
    p_search.add_argument("--max-mismatches", type=int, default=4, help="Maximum allowed mismatches (default: 4)")
    p_search.add_argument("--score-method", choices=["pw", "mit", "cfd", "cfd_full"], default="pw", help="Scoring method: pw=position-weighted, mit=MIT-like, cfd=CFD-like, cfd_full=CFD full table approximation")
    p_search.add_argument("--pretty", action="store_true", help="Show a human-friendly table on stdout")
    p_search.add_argument("--cfd-table", default=None, help="Path to CFD table JSON file (optional) for cfd_full scoring")
    args = parser.parse_args()

    # Input validation and helpful error messages
    if args.cmd == "search":
        import os
        errors = []
        if not args.guide or not isinstance(args.guide, str) or len(args.guide.strip()) == 0:
            errors.append("--guide is required and must be a non-empty string.")
        if not args.fasta or not os.path.isfile(args.fasta):
            errors.append(f"--fasta file '{args.fasta}' does not exist.")
        if args.max_mismatches < 0:
            errors.append("--max-mismatches must be non-negative.")
        if args.cfd_table and not os.path.isfile(args.cfd_table):
            errors.append(f"--cfd-table file '{args.cfd_table}' does not exist.")
        if errors:
            print("Input validation error(s):", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            parser.exit(1)
        try:
            search_command(args)
        except Exception as e:
            print(f"Error during search: {e}", file=sys.stderr)
            parser.exit(2)
    else:
        parser.print_help()


if __name__ == "__main__":
    # If the first argument is a click subcommand, use click CLI; else fallback to argparse CLI
    import sys
    click_commands = {"plot", "stats"}
    if len(sys.argv) > 1 and sys.argv[1] in click_commands:
        import click

        @click.group()
        def cli():
            """CRISPRCheck CLI (click-based commands)"""
            pass

        @cli.command()
        @click.argument('csv_path', type=click.Path(exists=True))
        def stats(csv_path):
            """Print summary statistics for efficiency/score columns in a results CSV file."""
            print_summary_statistics(csv_path)

        @cli.command()
        @click.argument('csv_path', type=click.Path(exists=True))
        @click.option('--output', '-o', type=click.Path(), default=None, help='Path to save the plot image.')
        @click.option('--show', is_flag=True, help='Show the plot interactively.')
        def plot(csv_path, output, show):
            """Plot efficiency distribution from a results CSV file."""
            try:
                plot_efficiency(csv_path, output_path=output, show=show)
                click.echo(f"Plot created for {csv_path}.{' Displayed.' if show else ''}{' Saved to ' + output if output else ''}")
            except Exception as e:
                click.echo(f"Error: {e}", err=True)

        cli()
    else:
        main()
