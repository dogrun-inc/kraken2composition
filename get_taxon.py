import csv
import json
import re
import glob
import argparse
from typing import List, Dict
from collections import defaultdict


ranks = ["phylum", "class", "order", "family", "genus", "species"]
headers = ["count", "superkingdom", "phylum", "class", "order", "family", "genus", "species", "strain"
           "filename", "sig_name", "sig_md5", "total_counts"]


def get_args():
    parser = argparse.ArgumentParser(description="This script takes in a directory of kraken2 output files and creates a composition file for each sample")
    parser.add_argument("-i", "--input", help="Path to input directory of kraken2 output files")
    return parser.parse_args()

def tax_list(compositions: dict) -> dict:
    """
    - 開発用にサンプルの系統組成データからtax情報を取得する
    - 入力はjson変換した系統組成データ
    - サンプルに利用してしてるkraken2の出力ファイルが二つあるためこの二つの和集合を取得する
    - 実際(本番API)は共通するtaxonomyセットを作ってもらう
    - rankごとのtaxonomyのリストを返す
    """
    tax_sets = defaultdict(set)

    # compositonsの中のranks/{hoge}/compositionの中のkeyを取得する
    # keyはsetに入れて重複を除去する
    for rank in ranks:
        tax_sets[rank].update(compositions[rank].keys())
    return tax_sets


def read_kraken2report(file_path: str) -> List[list]:
    with open(file_path, "r") as f:
        d = csv.reader(f, delimiter=",")
        # 先頭行はヘッダ行
        rows = [row for row in d]
        return rows


def select_by_rank(rows: list, rank: str) -> List[list]:
    # 引数で指定したrankのカラムの序数を取得する
    i = headers.index(rank)
    if i == -1:
        raise ValueError("rank is not found in headers")
    elif rank == "strain":
        # rank == "strain"のケースのみstrainのカラムに値がある行を返す. strainとspeciesのカラムの序数をハードコードしている
        selected_rows = [row for row in rows if row[7] != "" and row[8] != ""]
    else:
        # 指定したrankのカラムに値があり、rankの次のカラムに値がない行 = 指定したrankの値が含まれる行を抽出する
        # csvに空行が含まれるケースも想定されるため
        selected_rows = [row for row in rows if len(row) > 0 and row[i] != "" and row[i+1] == ""]

    # taxonomy nameのprefixを除去、countとtaxonomy nameのみのリストを返す
    selected_rows = [[row[i].split("__")[1], int(row[0])] for row in selected_rows]
    composition = {x[0]:x[1] for x in selected_rows if x[1] != ""}
    return {rank: composition}


if __name__ == "__main__":
    """
     開発用データ（taxon名のベクトル）を生成するためのスクリプト
     限られたサンプルからtaxon名のリストを取得するが、これで得られたtaxonomy空間は本番用ではないことを留意する
    """
    args = get_args()
    input_path = args.input
    files = glob.glob(f"{input_path}/*")

    tax_list_by_ranks = defaultdict(set)

    for file in files:
        # 1. read kraken2 report and return as list of list
        rows = read_kraken2report(file)
        composition = {}
        for rank in ranks:
            composition.update(select_by_rank(rows, rank))

        # 2. 組成からtaxonomyのみ取得する
        dct = tax_list(composition)

        # 3. rankごとにdefaultdictに追加する
        for rank in ranks:
            tax_list_by_ranks[rank].update(dct[rank])

    d = {k: sorted(list(v)) for k,v in dict(tax_list_by_ranks).items()}

    with open("tax_list.json", "w") as f:
        json.dump(d, f, indent=4)

