def print_summary_statistics(csv_path):
    """
    Print summary statistics (mean, median, std, min, max) for efficiency/score columns in a results CSV.
    Args:
        csv_path (str): Path to the results CSV file.
    """
    import pandas as pd
    df = pd.read_csv(csv_path)
    # Find columns with efficiency or score
    eff_cols = [col for col in df.columns if 'eff' in col.lower() or 'score' in col.lower()]
    if not eff_cols:
        print("No efficiency or score columns found in results CSV.")
        return
    for col in eff_cols:
        print(f"\nSummary statistics for '{col}':")
        print(df[col].describe())
"""
Visualization utilities for CRISPR results.
"""

def plot_efficiency(csv_path, output_path=None, show=False):
    """
    Plot efficiency results from a CSV file.
    Args:
        csv_path (str): Path to the results CSV file.
        output_path (str, optional): Path to save the plot image. If None, does not save.
        show (bool): Whether to display the plot interactively.
    """
    import matplotlib.pyplot as plt
    import pandas as pd
    df = pd.read_csv(csv_path)
    # Try to find a column with efficiency or score
    eff_cols = [col for col in df.columns if 'eff' in col.lower() or 'score' in col.lower()]
    if not eff_cols:
        raise ValueError("No efficiency or score column found in results CSV.")
    eff_col = eff_cols[0]
    plt.figure(figsize=(8, 5))
    plt.hist(df[eff_col], bins=20, color='skyblue', edgecolor='black')
    plt.title(f'Efficiency Distribution ({eff_col})')
    plt.xlabel(eff_col)
    plt.ylabel('Count')
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    if show:
        plt.show()
    plt.close()