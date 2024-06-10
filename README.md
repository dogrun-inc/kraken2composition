# kraken2composition

1. kraken2形式のテーブルを系統組成のrank,taxonomyの階層のjsonに変換します
2. 同様にkraken2形式のテーブルを（json変換後に）taxonomyのランクごとにtax x sampleのtsvファイルに出力します

＊APIとしてはmetadata APIと同様にtsvファイルを（あるいはJSONを）渡すようなAPIとする

## input形式

- 以下のようなヘッダを持ったkraken2の出力形式を持ったcsvファイルを入力として想定しています。
- 

```
count,superkingdom,phylum,class,order,family,genus,species,strain,filename,sig_name,sig_md5,total_counts
```

### 出力

対象となるディレクトリからファイル名を収集しRUN IDに変換したうえで
RUNに紐づく組成データをBioProjectにネストし出力します。

例 phylum.tsv (値は同じサンプルをidを変えて複製したもの)
```
taxonomy        SRR7723005      SRR7723001
Bacteroidota    81.4176652335257        81.4176652335257
Actinomycetota  9.260924294191692       9.260924294191692
Pseudomonadota  6.472021055729021       6.472021055729021
Bacillota       2.011574111915777       2.011574111915777
Bacillota_C     0.8378153046378185      0.8378153046378185
```


## 環境

Python3.9以上

## 利用方法

- ディレクトリを指定して変換

ディレクトリを指定してディレクトリ内に含まれる（子階層も含めて）ファイルを変換し、プロジェクトに含まれるサンプルの系統組成をrankごとにtab textで書き出します。


- ファイルを指定して変換

ファイルを指定して直接kraken2compositionを呼ぶことでサンプル単位でJSONを生成することもできます。"output file"を省略した場合は標準出力にJSONを渡します。

```
python kraken2composition.py -i ./private/megap -o ./public/project
```
*入力と出力のパスは実行環境に合わせる

- -i: inputファイルのディレクトリを指定
- -o: アウトプットファイルのディレクトリを指定
- -e: 読み込む対象となるファイルの拡張子を指定。デフォルトで"csv"が指定されている






