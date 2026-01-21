# First issues to open (Week 1 kickoff)

1. **Implement basic PAM-aware scanning and mismatch counting**
   - Implement naive FASTA scan that finds candidate sites according to PAM and reports mismatch positions and counts.

2. **Add MIT/CFD scoring implementation + tests**
   - Implement position-weighted score and a simple MIT-like score with unit tests.

3. **CLI argument parsing + CSV output**
   - Provide `crispr-check search` command, arguments for guide, pam, fasta, and out file.

4. **Genome annotation helper (GTF parser stub)**
   - Add scaffolding to accept GTF and annotate hits with gene/exon flags (Week 2 target).

5. **Minimal Streamlit UI to upload FASTA and guide and show table**
   - Create `web_app/streamlit_app.py` placeholder.

6. **Add Dockerfile and GitHub Actions test workflow**
   - Add Dockerfile skeleton and CI workflow to run tests.

---

Add more detail to each issue when opening on GitHub (labels: `good first issue`, `area:core`, `priority:high`).