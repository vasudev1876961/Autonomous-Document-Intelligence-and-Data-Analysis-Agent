"""
Complex Table Structure Recognition and Multi-Page Stitching Engine.
Handles irregular merged cells (rowspan/colspan), hierarchical multi-level headers,
and continuous financial statements spanning multiple PDF pages.
"""
from typing import Any, Optional
import pandas as pd
from pydantic import BaseModel, Field


class StructuredTableCell(BaseModel):
    row_idx: int
    col_idx: int
    text: str
    is_header: bool = False
    rowspan: int = 1
    colspan: int = 1
    bbox: Optional[tuple[float, float, float, float]] = None


class RecognizedTable(BaseModel):
    table_id: str
    page_number: int
    num_rows: int
    num_cols: int
    headers: list[str] = Field(default_factory=list)
    has_hierarchical_headers: bool = False
    is_multi_page_continuation: bool = False
    csv_representation: str = ""
    cell_matrix: list[list[str]] = Field(default_factory=list)


class ComplexTableRecognizer:
    """
    Cleans, normalizes, and reconstructs irregular and multi-page tabular statements.
    """

    @classmethod
    def process_raw_table(
        cls,
        raw_rows: list[list[str]],
        table_id: str = "tab_1",
        page_number: int = 1
    ) -> RecognizedTable:
        """
        Cleans raw extracted table rows, resolving empty spanning cells and detecting headers.
        """
        if not raw_rows or len(raw_rows) < 1:
            return RecognizedTable(
                table_id=table_id,
                page_number=page_number,
                num_rows=0,
                num_cols=0
            )

        # 1. Normalize column count across rows
        max_cols = max(len(r) for r in raw_rows)
        normalized_rows: list[list[str]] = []
        for r in raw_rows:
            cleaned_row = [str(cell).strip() if cell is not None else "" for cell in r]
            if len(cleaned_row) < max_cols:
                cleaned_row.extend([""] * (max_cols - len(cleaned_row)))
            normalized_rows.append(cleaned_row)

        # 2. Hierarchical header detection: check if first 2 rows both look like headers
        has_hierarchical = False
        headers = []
        if len(normalized_rows) >= 2:
            r0 = normalized_rows[0]
            r1 = normalized_rows[1]
            # If row 0 has empty cells followed by labels and row 1 has sub-labels
            if any(c == "" for c in r0) and any(c != "" for c in r1):
                # Hierarchical combination
                has_hierarchical = True
                combined_headers = []
                parent = ""
                for h0, h1 in zip(r0, r1):
                    if h0:
                        parent = h0
                    name = f"{parent} - {h1}" if parent and h1 and parent != h1 else (h1 or parent or "Col")
                    combined_headers.append(name.strip())
                headers = combined_headers
                data_rows = normalized_rows[2:]
            else:
                headers = [h or f"Column_{i+1}" for i, h in enumerate(normalized_rows[0])]
                data_rows = normalized_rows[1:]
        else:
            headers = [h or f"Column_{i+1}" for i, h in enumerate(normalized_rows[0])]
            data_rows = []

        # 3. Merged cell forward-fill for row labels (first column)
        clean_matrix = [headers]
        last_category = ""
        for row in data_rows:
            if row[0] != "":
                last_category = row[0]
            elif last_category:
                row[0] = f"{last_category} (Cont.)"
            clean_matrix.append(row)

        df = pd.DataFrame(data_rows, columns=headers) if data_rows else pd.DataFrame(columns=headers)
        csv_repr = df.to_csv(index=False)

        return RecognizedTable(
            table_id=table_id,
            page_number=page_number,
            num_rows=len(clean_matrix),
            num_cols=max_cols,
            headers=headers,
            has_hierarchical_headers=has_hierarchical,
            csv_representation=csv_repr,
            cell_matrix=clean_matrix
        )

    @classmethod
    def stitch_multi_page_tables(
        cls,
        tables: list[RecognizedTable]
    ) -> list[RecognizedTable]:
        """
        Detects tables split across page boundaries that share continuous schema
        and merges them into a single consolidated statement.
        """
        if not tables or len(tables) <= 1:
            return tables

        stitched: list[RecognizedTable] = []
        skip_indices = set()

        for i in range(len(tables)):
            if i in skip_indices:
                continue

            current = tables[i]
            # Check if next table is on consecutive page with matching headers
            if i + 1 < len(tables):
                next_t = tables[i + 1]
                if next_t.page_number == current.page_number + 1 and next_t.headers == current.headers:
                    # Stitch next table's data rows into current table
                    merged_matrix = list(current.cell_matrix)
                    merged_matrix.extend(next_t.cell_matrix[1:])  # Skip repeated header row
                    merged_df = pd.DataFrame(merged_matrix[1:], columns=current.headers)

                    current = RecognizedTable(
                        table_id=f"{current.table_id}_stitched",
                        page_number=current.page_number,
                        num_rows=len(merged_matrix),
                        num_cols=current.num_cols,
                        headers=current.headers,
                        has_hierarchical_headers=current.has_hierarchical_headers,
                        is_multi_page_continuation=True,
                        csv_representation=merged_df.to_csv(index=False),
                        cell_matrix=merged_matrix
                    )
                    skip_indices.add(i + 1)

            stitched.append(current)

        return stitched
