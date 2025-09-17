# 分子XYZ座標から分子性結晶CIFファイル生成ツール

このツールは、分子のXYZ座標ファイルを読み込み、その分子から構成される最適化された分子性結晶のCIFファイルを生成します。

## 必要な依存関係

- PyXtal
- pymatgen
- numpy

## 使用方法

### 基本的な使用方法

```bash
python scripts/generate_molecular_crystal.py input.xyz
```

これにより、`crystal.cif` ファイルが生成されます。

### オプション付きの使用方法

```bash
# 出力ファイル名を指定
python scripts/generate_molecular_crystal.py water.xyz -o water_crystal.cif

# 単位格子中の分子数を変更（デフォルト: 4）
python scripts/generate_molecular_crystal.py benzene.xyz -n 8

# 体積因子を調整（デフォルト: 1.1、大きくすると分子間距離が広くなる）
python scripts/generate_molecular_crystal.py molecule.xyz -f 1.2

# 特定の空間群のみを試行
python scripts/generate_molecular_crystal.py molecule.xyz -s 1,2,14,15

# 詳細な出力
python scripts/generate_molecular_crystal.py molecule.xyz --verbose

# 最大試行回数を変更
python scripts/generate_molecular_crystal.py molecule.xyz --max-attempts 50
```

## XYZファイル形式

XYZファイルは以下の形式である必要があります：

```
原子数
コメント行（分子名など）
元素記号 x座標 y座標 z座標
元素記号 x座標 y座標 z座標
...
```

### 例：水分子 (water.xyz)

```
3
Water molecule
O    0.000000    0.000000    0.000000
H    0.757000    0.586000    0.000000
H   -0.757000    0.586000    0.000000
```

### 例：ベンゼン分子 (benzene.xyz)

```
6
Benzene molecule
C   0.000000  1.396000  0.000000
C   1.209000  0.698000  0.000000
C   1.209000 -0.698000  0.000000
C   0.000000 -1.396000  0.000000
C  -1.209000 -0.698000  0.000000
C  -1.209000  0.698000  0.000000
```

## パラメータの説明

- **num-mols (-n)**: 単位格子中の分子数。一般的には2, 4, 8などの値を使用
- **factor (-f)**: 体積因子。1.0より大きい値で分子間距離を調整
- **space-groups (-s)**: 試行する空間群。デフォルトでは分子性結晶でよく使われる空間群を自動選択
- **max-attempts**: 最大試行回数。構造生成が困難な場合は増やす

## デフォルト空間群

スクリプトはデフォルトで以下の空間群を試行します（分子性結晶で一般的なもの）：

- P1 (1)
- P-1 (2) 
- P21/c (14)
- C2/c (15)
- P212121 (19)
- Pbca (61)
- Pnma (62)
- Cmcm (63)
- Fddd (64)
- Cmmm (65)
- P42/ncm (92)
- P43212 (96)
- I41/acd (142)
- P3 (143)
- P31 (144)
- P32 (145)

## 出力

生成されるCIFファイルには以下の情報が含まれます：

- 結晶の組成
- 空間群情報
- 格子パラメータ（a, b, c, α, β, γ）
- 原子座標（分数座標）
- 対称性情報

## トラブルシューティング

### 「有効な分子性結晶を生成できませんでした」エラー

以下を試してください：

1. 体積因子を増やす: `-f 1.3` または `-f 1.5`
2. 分子数を変更する: `-n 2` または `-n 8`
3. 最大試行回数を増やす: `--max-attempts 200`
4. 特定の空間群を試す: `-s 1,2,14`

### メモリやパフォーマンスの問題

- 大きな分子の場合は、`-n 2` で分子数を減らす
- `--max-attempts` を小さくして試行回数を制限

## 注意点

- 生成される結晶構造は初期構造であり、実際の物理的安定性を保証するものではありません
- より正確な構造を得るには、生成後にDFTなどを用いた構造最適化が推奨されます
- 分子間相互作用は簡単なvan der Waals半径に基づいており、水素結合などは考慮されていません