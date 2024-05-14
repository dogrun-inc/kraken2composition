import csv
from typing import List, NewType
import argparse
import re
import json

Filepath = NewType("Filepath", str)

# kraken2 reportのヘッダ
headers = ["count", "superkingdom", "phylum", "class", "order", "family", "genus", "species", "strain"
           "filename", "sig_name", "sig_md5", "total_counts"]
# 出力する階級をリストで指定
ranks = ["phylum", "class", "order", "family", "genus", "species"]

# 標準taxon空間の定義ファイル
taxonomy_list_file = "./sample/test/tax_list.json"

def get_args():
    parser = argparse.ArgumentParser(description="This script takes in a directory of kraken2 output files and creates a composition file for each sample")
    parser.add_argument("-i", "--input", help="Path to input directory of kraken2 output files")
    parser.add_argument("-o", "--output", help="Path to output directory of composition files")
    return parser.parse_args()


def read_kraken2report(file_path: str) -> List[list]:
    """
    kraken2 reportファイル」を読みこんでlistを返す
    :return:
    """
    with open(file_path, "r") as f:
        d = csv.reader(f, delimiter=",")
        # 先頭行はヘッダ行
        rows = [row for row in d]
        return rows


def select_by_rank(rows: list, rank: str) -> List[list]:
    """
    rowsからその行の分類rankが引数で指定した値の行（count, taxonomy）だけを抽出して返す。
    rankの一致の判定は最も細分化されたrankが指定したrankかどうかを判定する。
    taxonomy nameはreportで付加されたprefixを除去して返す。
    :param rows:
    :param rank:
    :return:
    """
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


def get_run_id(input_path: Filepath) -> str:
    """_summary_
    ファイル名からrun_idを取得する。
    想定するファイル名はrun id + _n.fastq.sam.mapped.bam...txtのような文字列なので
    ファイル名先頭のアルファベット＋数字分部分を利用する。
        file_name (_type_): _description_
    Returns: RUN ID
    """
    file_name = input_path.split("/")[-1]
    # 三頭のアルファベット＋数字分部分を取得
    run_id = re.findall(r'^[a-zA-Z0-9]+', file_name)
    return run_id[0]


def create_composition():
    """
    kraken2形式のreportファイルを読みこみ、プロジェクト、分類階級、taxonomy、サンプルでまとめた組成データをJSON形式で出力する。
    """
    args = get_args()
    input_path = args.input
    output_path = args.output

    # 1. read kraken2 report and return as list of list
    rows = read_kraken2report(input_path)
    # 2. select by rank
    composition = {}
    for rank in ranks:
        composition.update(select_by_rank(rows, rank))

    if output_path is None:
        return composition
    else:
        with open(output_path, "w") as f:
            f.write(json.dumps(composition))


def create_table(compositons:dict, run_id:str) -> list:
    """
    - 入力された系統組成データをテーブル形式に変換する
    - 二次元配列を作成する
    """
    for rank in ranks:
        header = [rank, run_id]
        composition = compositons[rank]
        rows = [[k, v]for k, v in composition.items()]
        rows.insert(0, header)
        with open(f"./sample/test/{rank}_table.tsv", "w") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerows(rows)


class TaxonomyList:
    def __init__(self):
        """
        rankを引数にサービスのデータセットに共通するscientific nameのリストを返す
        Args:
            rank (str): 取得する階級名
        """
        with open(taxonomy_list_file, "r") as f:
            self.tax_list = json.load(f)

    def name_list(self, rank:str):
        return self.tax_list[rank]


def completion(composition:dict) -> dict:
    """
    入力したサンプルの系統組成データをサービスの設定する全長のデータで補完し、
    サンプルに存在しないtaxonの値は0で埋める
    """
    taxonomy = TaxonomyList()
    for rank in ranks:
        # 標準の名前リストを取得
        name_list = taxonomy.name_list(rank)
        # 入力されたデータの名前リストを取得
        sample_name_list = composition[rank].keys()

        # 標準の名前リストと入力された名前リストを比較して、存在しないサンプルを0で埋めて補完する
        for name in name_list:
            if name not in sample_name_list:
                composition[rank][name] = 0
    return composition


if __name__ == "__main__":
    """
    サンプルごとの系統組成データを取得しJSON形式に変換する
    コマンドラインで呼び出す場合入力するファイル名は -iオプションで指定する
    """
    # 1. 系統組成データをdict形式で生成する
    compositions = create_composition()
    # 2. 標準のtaxon空間でtaxonomyを補完する
    complemented_compositions = completion(compositions)
    # 3. 補完された系統組成データを生成し、テーブル形式に変換する
    args = get_args()
    run_id = get_run_id(args.input)
    tbl = create_table(complemented_compositions, run_id)
