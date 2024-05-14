import re
from kraken2composition import read_kraken2report, select_by_rank


def get_file_names(input_path) -> list:
    """_summary_
    指定したディレクトリ以下のファイル名を取得する
    Args:
        input_path (_type_): _description_
    Returns:
        list: ディレクトリに含まれる全tsvファイルのリスト
    """
    
    # 子階層の任意のディレクトリ名にマッチするワイルドカードを追加
    file_names = glob.glob(input_path + '/*/*.' + file_extension)
    return file_names


def get_run_id(file_name) -> str:
    """_summary_
    ファイル名からrun_idを取得する。
    想定するファイル名はrun id + _n.fastq.sam.mapped.bam...txtのような文字列なので
    ファイル名先頭のアルファベット＋数字分部分を利用する。
        file_name (_type_): _description_
    Returns:
        str: run_id
    """
    # input_path=子階層/ファイル名なのでファイル名部分のみに修正
    file_name = file_name.split("/")[-1]
    # 三頭のアルファベット＋数字分部分を取得
    run_id = re.findall(r'^[a-zA-Z0-9]+', file_name)
    return run_id[0]


def parse_filename():
    # ファイルパスから子階層+ファイル名を取得する
    # file_names = [f.split("/")[-1] for f in file_names if f.endswith(file_extension)]
    file_names = ["/".join(f.split("/")[-2:]) for f in file_names if f.endswith(file_extension)]
    run_list = []
    for file_name in file_names:
        # Todo: file_nameはパス名を含むので、パス名を除いたファイル名のみを取得する
        run_id = get_run_id(file_name)
        run_list.append(run_id)


if __name__ == "__main__":
    """_summary_
    - kraken2形式の系統組成が出力されたディレクトリを指定し、
    RUN-BioProjectのrelationを取得してBioProjectにネストした構造として系統組成データを出力する
    - BioProjectに紐づくrunごとの系統組成データはkraken2composition.pyで出力する
    """