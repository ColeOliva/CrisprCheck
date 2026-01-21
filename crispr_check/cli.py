import argparse
import csv
from . import search, scoring


def _write_csv(out_path, rows, fieldnames):
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def search_command(args):
    hits = search.scan_fasta_for_guide(args.guide, args.fasta, pam=args.pam, max_mismatches=args.max_mismatches)
    # score and sort
    for h in hits:
        h["score_pw"] = scoring.position_weighted_score(args.guide, h["target_seq"])
        h["score_mit"] = scoring.mit_like_score(args.guide, h["target_seq"])
    hits.sort(key=lambda x: x["score_pw"], reverse=True)
    fields = ["seq_id", "start", "end", "strand", "target_seq", "mismatches", "mismatch_positions", "score_pw", "score_mit"]
    out = args.out or "results.csv"
    _write_csv(out, hits, fields)
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
    args = parser.parse_args()
    if args.cmd == "search":
        search_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
