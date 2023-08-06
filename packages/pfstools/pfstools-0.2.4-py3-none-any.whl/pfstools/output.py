import os
import csv

import pyodbc
import pandas as pd
from math import floor


def xlcol(col: "str | int"):
    """

    Converts integer column number to Excel letters, and vice versa

    """

    if isinstance(col, str):
        return sum(
            [
                (ord(col[len(col) - i - 1]) - 64) * 26**i
                for i in reversed(range(len(col)))
            ]
        )
    else:
        if col <= 26:
            ret = chr(64 + col)
        else:
            ret = xlcol((col - 1) // 26) + xlcol((col - 1) % 26 + 1)
        return ret


def to_excel(
    df,
    excel_path,
    sheet_name="sheet1",
    money_cols=[],
    perc_cols=[],
    num_cols=[],
    text_cols=[],
    date_cols=[],
    total_cols=[],
    outindex=False,
    format_table="Table Style Light 18",
    total_percs={},
    close_file=True,
    start_row=0,
    start_col=0,
):

    """
    Exports a dataframe to an excel file with common formatting.
    Fields with names ending in '_amount', '_amt', '$' get formatted as currency.
    Fields with names ending in '_perc', '%' get formatted as percentage.
    Fields with names ending in 'date' get date formatting

    Should I look at column types as well as names?
    """
    # write dataframe to excel
    if type(excel_path) is pd.io.excel._XlsxWriter:
        outfile = excel_path
    else:
        outfile = pd.ExcelWriter(excel_path, engine="xlsxwriter")

    columns = [
        str(c) for c in (list(df.index.names) if outindex else []) + list(df.columns)
    ]

    df.to_excel(
        outfile,
        index=outindex,
        sheet_name=sheet_name,
        startrow=start_row,
        startcol=start_col,
    )

    max_row = df.shape[0] + start_row
    max_col = len(columns) + start_col

    if len(df.index) > 0:

        workbook = outfile.book
        ws = outfile.sheets[sheet_name]

        if len(format_table) > 0:
            # --------------------
            #    TABLE
            # --------------------
            column_settings = [{"header": str(column)} for column in columns]
            ws.add_table(
                start_row,
                start_col,
                max_row,
                max_col - 1,
                {"columns": column_settings, "style": format_table, "total_row": False},
            )

        # --------------------
        #    TOTALS
        # --------------------
        if len(total_cols):
            max_row += 1

            total_fmt = workbook.add_format({"align": "right", "bold": True, "top": 6})
            total_money_fmt = workbook.add_format(
                {"align": "right", "num_format": "$#,##0", "bold": True, "top": 6}
            )

            total_percent_fmt = workbook.add_format(
                {"align": "right", "num_format": "0.0%", "bold": True, "top": 6}
            )
            column_numbers = {}

            # total values so that they show up in email preview
            totals = df[total_cols].sum()

            for i in range(len(columns)):
                column_numbers[columns[i]] = i + 1 + start_col
                val = ""
                write_style = 0
                cur_col = f"{xlcol(column_numbers[columns[i]])}"
                cell_ref = f"{cur_col}{max_row+1}"
                fmt = total_fmt

                if i == 0:
                    val = "Totals"
                    write_style = 1
                elif columns[i] in total_cols:
                    formula = f"=SUBTOTAL(109,{cur_col}{2}:{cur_col}{max_row})"
                    val = totals[columns[i]]
                    write_style = 2
                    if (columns[i][-1] == "$") or (columns[i] in money_cols):
                        fmt = total_money_fmt

                elif columns[i] in total_percs:
                    (numer_column, denom_column) = total_percs[columns[i]]
                    formula = f"=-{xlcol(column_numbers[numer_column])}{max_row+1}/{xlcol(column_numbers[denom_column])}{max_row+1}"
                    val = -totals[numer_column] / totals[denom_column]
                    write_style = 2
                    fmt = total_percent_fmt

                # print(f"{i} {cell_ref} ... {columns[i]} ... {val}")

                if write_style == 1:
                    ws.write(cell_ref, val, fmt)
                elif write_style == 2:
                    ws.write_formula(cell_ref, formula, fmt, val)

        # --------------------
        #  FORMATTING
        # --------------------

        perc_fmt = workbook.add_format({"num_format": "0.0%", "bold": False})
        money_fmt = workbook.add_format({"num_format": "$#,##0.00", "bold": False})
        count_fmt = workbook.add_format({"num_format": "0", "bold": False})
        date_fmt = workbook.add_format({"num_format": "d/m/yyyy"})
        text_fmt = workbook.add_format({"num_format": "@"})

        cell_by_cell = start_row > 5 and (max_row - start_row < 1000)
        if cell_by_cell:
            print("format cell by cell instead of whole column")
        else:
            print("format whole column")
        # --------------------
        #  COLUMN LENGTH
        # --------------------
        col_lengths = {
            c: min(
                100,
                max(10, len(str(c)), floor(df[c].astype(str).map(len).max() * 1.25)),
            )
            for c in df
        }

        for c in [c for c in columns if not c in df]:
            col_lengths[c] = max(10, len(str(c)))

        # --------------------
        #  COLUMN FORMATS
        # --------------------
        col_formats = {}
        for c in columns:
            if (c[-1] == "$") or (c in money_cols):
                col_formats[c] = money_fmt
            elif (c[-1] == "#") or (c in num_cols):
                col_formats[c] = count_fmt
            elif (c[-1] == "%") or (c in perc_cols):
                col_formats[c] = perc_fmt
            elif c in date_cols:
                col_formats[c] = date_fmt
            else:
                col_formats[c] = text_fmt

        col = start_col
        for c in columns:
            if not cell_by_cell:
                # print(f"formatting column {col}, {c}, length: {col_lengths[c]}, format: {col_formats[c]}")
                ws.set_column(col, col, col_lengths[c], col_formats[c])
            else:
                if c in df.columns:
                    r = start_row + 1
                    for v in df[c]:
                        ws.write(r, col, v, col_formats[c])
                        r += 1
            col += 1

        if 1 == 0:
            for a in columns:
                if not a in col_lengths:
                    ws.set_column(col, col, max(10, len(a)))
                elif (a[-1] == "$") or (a in money_cols):
                    ws.set_column(col, col, max(10, col_lengths[a]), money_fmt)
                elif (a[-1] == "#") or (a in num_cols):
                    ws.set_column(col, col, max(7, col_lengths[a]), count_fmt)
                elif (a[-1] == "%") or (a in perc_cols):
                    ws.set_column(col, col, max(10, col_lengths[a]), perc_fmt)
                elif a in text_cols:
                    ws.set_column(col, col, max(10, col_lengths[a]), text_fmt)
                elif a in date_cols:
                    ws.set_column(col, col, max(10, col_lengths[a]), date_fmt)
                else:
                    ws.set_column(col, col, col_lengths[a])
                col += 1

    # outfile.save()
    if close_file:
        #outfile.save()
        outfile.close()
        return excel_path
    else:
        return outfile


def to_access(df, accdb_path, target_table):
    """
    Exports dataframe data to an Access accdb file, via an intermediary csv file.
    This is considerably faster than dataframe.to_sql.
    target_table is assumed to exist and have the exact same columns as df.

    Future additions could include creating the target table, and/or specifying
    column mappings.


    """
    acc_cnx = pyodbc.connect(
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=" + accdb_path
    )
    ######
    # send df data to temp csv file
    output_path = os.getcwd()
    tempcsv = f"tempcsvdatafor{target_table}.csv"
    df.to_csv(f"{output_path}\\{tempcsv}", index=False, quoting=csv.QUOTE_NONNUMERIC)

    # move data from csv to accdb

    with pyodbc.connect(
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=" + accdb_path
    ) as acc_cnx:
        with acc_cnx.cursor() as cur:
            cur.execute(
                rf"""INSERT INTO [{target_table}]
                             SELECT *
                             FROM [text;HDR=Yes;FMT=Delimited(,);Database={output_path}].{tempcsv} t"""
            )
            cur.commit()

    # delete csv file
    os.remove(f"{output_path}\\{tempcsv}")
    return "success"


def to_dbf(df, filename):
    pass
