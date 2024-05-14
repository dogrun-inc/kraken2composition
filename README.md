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


```
{
"bioproject": "PRJDB0000",
"compositions":
    [
        {
            "run":"DRR0000",
            "ranks":{
                phylum: {
                    "composition":{
                        "taxonomy 1": num,
                        "taxonomy 2": num,
                    }
                },
                class: {
                    "composition":{
                        "taxonomy 1": num,
                        "taxonomy 2": num,
                    }
                },,
            }
            
        },
    ]
} 
```


## 環境

Python3.9以上

## 利用方法

- ディレクトリを指定して変換

ディレクトリを指定してディレクトリ内に含まれる（子階層も含めて）ファイルを変換し、BioProjectでネストしてJSONとして書き出します。

```

```

- ファイルを指定して変換

ファイルを指定して直接kraken2compositionを呼ぶことでサンプル単位でJSONを生成することもできます。"output file"を省略した場合は標準出力にJSONを渡します。

```
python kraken2composition.py -i <input file> -o <output file>
```







