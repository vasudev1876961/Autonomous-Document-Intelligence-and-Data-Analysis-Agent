"""
Visual Analytics Generator using Matplotlib.
Creates clear, verified charts for period comparisons and segment contributions.
"""
from pathlib import Path
from typing import Optional
import matplotlib
matplotlib.use("Agg") # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from config.settings import settings
from src.tools.numerical_analysis import PeriodComparisonResult, SegmentAnalysisSummary

class ChartGenerator:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or settings.charts_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_period_comparison_chart(
        self,
        result: PeriodComparisonResult,
        filename: str = "period_comparison.png"
    ) -> Path:
        """Bar chart comparing Period 1 and Period 2 values."""
        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
        
        periods = [result.period_1_name, result.period_2_name]
        values = [result.period_1_value, result.period_2_value]
        colors = ["#3b82f6", "#ef4444" if result.direction == "decrease" else "#10b981"]

        bars = ax.bar(periods, values, color=colors, width=0.45, edgecolor="#1e293b", linewidth=1.2)
        
        # Add data labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:,.1f} {result.unit}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=10, fontweight="bold"
            )

        delta_sign = "+" if result.absolute_change > 0 else ""
        pct_text = f" ({delta_sign}{result.percentage_change}%)" if result.percentage_change is not None else ""
        title = f"{result.metric_name}: {result.period_1_name} vs {result.period_2_name}\nChange: {delta_sign}{result.absolute_change} {result.unit}{pct_text}"
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
        ax.set_ylabel(result.unit, fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        
        out_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(out_path, format="png")
        plt.close(fig)
        return out_path

    def generate_segment_contribution_chart(
        self,
        summary: SegmentAnalysisSummary,
        filename: str = "segment_contribution.png"
    ) -> Path:
        """Horizontal bar chart showing each segment's absolute change and percentage contribution."""
        fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

        names = [s.segment_name for s in summary.segments]
        deltas = [s.absolute_change for s in summary.segments]
        contributions = [s.contribution_percentage or 0.0 for s in summary.segments]
        
        colors = ["#ef4444" if d < 0 else "#10b981" if d > 0 else "#94a3b8" for d in deltas]
        
        y_pos = np.arange(len(names))
        bars = ax.barh(y_pos, deltas, color=colors, height=0.5, edgecolor="#1e293b", linewidth=1)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10, fontweight="bold")
        ax.axvline(0, color="#64748b", linewidth=1, linestyle="--")

        for idx, bar in enumerate(bars):
            val = deltas[idx]
            contrib = contributions[idx]
            offset = 4 if val >= 0 else -4
            ha = "left" if val >= 0 else "right"
            ax.annotate(
                f"{val:+,.1f} ({contrib:.1f}% contrib)",
                xy=(val, bar.get_y() + bar.get_height() / 2),
                xytext=(offset, 0),
                textcoords="offset points",
                ha=ha, va="center",
                fontsize=9, fontweight="bold"
            )

        title = f"Segment Contributions to Total Change ({summary.total_absolute_change:+,.1f} {summary.unit})"
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
        ax.set_xlabel(f"Absolute Change ({summary.unit})", fontsize=10)
        ax.grid(axis="x", linestyle="--", alpha=0.4)

        out_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(out_path, format="png")
        plt.close(fig)
        return out_path
