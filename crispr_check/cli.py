import argparse
import csv

from . import scoring, search


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
    p_search.add_argument("--guide", required=True)
    p_search.add_argument("--pam", default="NGG")
    p_search.add_argument("--fasta", required=True)
    p_search.add_argument("--out", default="results.csv")
    p_search.add_argument("--max-mismatches", type=int, default=4)
    p_search.add_argument("--score-method", choices=["pw", "mit", "cfd", "cfd_full"], default="pw", help="Scoring method: pw=position-weighted, mit=MIT-like, cfd=CFD-like, cfd_full=CFD full table approximation")
    p_search.add_argument("--pretty", action="store_true", help="Show a human-friendly table on stdout")
    p_search.add_argument("--cfd-table", default=None, help="Path to CFD table JSON file (optional) for cfd_full scoring")
    args = parser.parse_args()
    if args.cmd == "search":
        search_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
