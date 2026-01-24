"""
Streamlit app for CRISPRCheck: upload results, visualize efficiency, and view summary statistics.
"""
import io

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from crispr_check.visualization import (plot_efficiency,
                                        print_summary_statistics)

st.title("CRISPRCheck Results Explorer")

uploaded_file = st.file_uploader("Upload results CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("## Data Preview", df.head())

    # Efficiency/score columns
    eff_cols = [col for col in df.columns if 'eff' in col.lower() or 'score' in col.lower()]
    if eff_cols:
        eff_col = st.selectbox("Select efficiency/score column to plot", eff_cols)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(df[eff_col], bins=20, color='skyblue', edgecolor='black')
        ax.set_title(f'Efficiency Distribution ({eff_col})')
        ax.set_xlabel(eff_col)
        ax.set_ylabel('Count')
        st.pyplot(fig)
        # Download plot as PNG
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        st.download_button("Download plot as PNG", buf.getvalue(), file_name="efficiency_plot.png", mime="image/png")
        plt.close(fig)
        # Show summary statistics
        st.write("## Summary Statistics", df[eff_col].describe())
        # Download summary as CSV
        stats_csv = df[eff_col].describe().to_csv()
        st.download_button("Download summary as CSV", stats_csv, file_name="summary_stats.csv", mime="text/csv")
    else:
        st.warning("No efficiency or score columns found in uploaded CSV.")
else:
    st.info("Upload a results CSV to begin.")
