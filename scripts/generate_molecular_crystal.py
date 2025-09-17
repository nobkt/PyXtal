#!/usr/bin/env python3
"""
分子のxyz座標から最適化分子性結晶のcifファイルを生成するスクリプト

このスクリプトは、分子のXYZ座標ファイルを読み込み、その分子から構成される
最適化された分子性結晶のCIFファイルを生成します。

使用方法:
    python generate_molecular_crystal.py input.xyz [オプション]

必要な引数:
    input.xyz          入力分子のXYZファイル

オプション:
    -o, --output       出力CIFファイル名 (デフォルト: crystal.cif)
    -n, --num-mols     単位格子中の分子数 (デフォルト: 4)
    -f, --factor       体積因子 (デフォルト: 1.1)
    -s, --space-groups 試行する空間群のリスト (デフォルト: 自動選択)
    --max-attempts     最大試行回数 (デフォルト: 100)
    --seed             ランダムシード (デフォルト: None)
    -v, --verbose      詳細な出力

Examples:
    # 基本的な使用方法
    python generate_molecular_crystal.py water.xyz
    
    # カスタム設定
    python generate_molecular_crystal.py benzene.xyz -o benzene_crystal.cif -n 8 -f 1.2
    
    # 特定の空間群を指定
    python generate_molecular_crystal.py molecule.xyz -s 1,2,14,15
"""

import argparse
import sys
import os
import time
from pathlib import Path
import numpy as np
from typing import List, Optional, Tuple

from pymatgen.core.structure import Molecule
from pymatgen.io.cif import CifWriter
from pyxtal import pyxtal
from pyxtal.molecule import pyxtal_molecule


def read_xyz_file(file_path: str) -> Molecule:
    """
    XYZファイルを読み込んでpymatgen Moleculeオブジェクトを作成
    
    Args:
        file_path: XYZファイルのパス
        
    Returns:
        pymatgen Molecule オブジェクト
        
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        ValueError: ファイル形式が正しくない場合
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"XYZファイルが見つかりません: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # 最初の行は原子数
        num_atoms = int(lines[0].strip())
        
        # 2行目はコメント（スキップ）
        
        # 3行目以降は原子の座標
        species = []
        coords = []
        
        for i in range(2, 2 + num_atoms):
            parts = lines[i].strip().split()
            if len(parts) < 4:
                raise ValueError(f"行 {i+1} の形式が正しくありません: {lines[i].strip()}")
            
            species.append(parts[0])
            coords.append([float(parts[1]), float(parts[2]), float(parts[3])])
        
        coords = np.array(coords)
        return Molecule(species, coords)
        
    except (IndexError, ValueError) as e:
        raise ValueError(f"XYZファイルの読み込みエラー: {e}")


def generate_molecular_crystal(
    molecule: Molecule,
    num_mols: int = 4,
    factor: float = 1.1,
    space_groups: Optional[List[int]] = None,
    max_attempts: int = 100,
    seed: Optional[int] = None,
    verbose: bool = False
) -> Optional[pyxtal]:
    """
    分子から最適化された分子性結晶を生成
    
    Args:
        molecule: 分子のpymatgen Moleculeオブジェクト
        num_mols: 単位格子中の分子数
        factor: 体積因子
        space_groups: 試行する空間群のリスト
        max_attempts: 最大試行回数
        seed: ランダムシード
        verbose: 詳細な出力フラグ
        
    Returns:
        成功した場合はpyxtalオブジェクト、失敗した場合はNone
    """
    
    # デフォルトの空間群リスト（分子性結晶で一般的なもの）
    if space_groups is None:
        space_groups = [1, 2, 14, 15, 19, 61, 62, 63, 64, 65, 92, 96, 142, 143, 144, 145]
    
    if verbose:
        print(f"分子性結晶の生成を開始...")
        print(f"分子: {molecule.composition}")
        print(f"原子数: {len(molecule.species)}")
        print(f"単位格子中の分子数: {num_mols}")
        print(f"体積因子: {factor}")
        print(f"試行する空間群: {space_groups}")
    
    # 各空間群を試行
    best_crystal = None
    best_volume = float('inf')
    attempts = 0
    
    for sg in space_groups:
        if attempts >= max_attempts:
            break
            
        for trial in range(max_attempts // len(space_groups) + 1):
            if attempts >= max_attempts:
                break
                
            attempts += 1
            
            try:
                if verbose:
                    print(f"試行 {attempts}: 空間群 {sg}, トライアル {trial + 1}")
                
                start_time = time.time()
                
                # pyxtal分子性結晶を生成
                crystal = pyxtal(molecular=True)
                crystal.from_random(
                    dim=3,
                    group=sg,
                    species=[molecule],
                    numIons=[num_mols],
                    factor=factor,
                    seed=seed
                )
                
                if crystal.valid:
                    # より小さい体積（高密度）の結晶を優先
                    volume = crystal.lattice.volume
                    
                    if verbose:
                        elapsed = time.time() - start_time
                        print(f"  成功! 体積: {volume:.2f} Ų, 時間: {elapsed:.2f}秒")
                    
                    if volume < best_volume:
                        best_crystal = crystal
                        best_volume = volume
                        
                        if verbose:
                            print(f"  新しい最良結晶を発見 (体積: {volume:.2f} Ų)")
                
                else:
                    if verbose:
                        elapsed = time.time() - start_time
                        print(f"  失敗, 時間: {elapsed:.2f}秒")
                        
            except Exception as e:
                if verbose:
                    print(f"  エラー: {e}")
                continue
    
    if verbose:
        if best_crystal:
            print(f"\n最良の結晶:")
            print(f"  空間群: {best_crystal.group.number} ({best_crystal.group.symbol})")
            print(f"  体積: {best_volume:.2f} Ų")
            print(f"  格子パラメータ: {best_crystal.lattice}")
        else:
            print(f"\n{attempts}回の試行後、有効な結晶を生成できませんでした。")
    
    return best_crystal


def write_cif_file(crystal: pyxtal, output_path: str, verbose: bool = False):
    """
    pyxtal結晶からCIFファイルを書き出し
    
    Args:
        crystal: pyxtalオブジェクト
        output_path: 出力CIFファイルのパス
        verbose: 詳細な出力フラグ
    """
    try:
        # pymatgen構造に変換
        pmg_struct = crystal.to_pymatgen()
        
        # CIFファイルを作成
        cif_writer = CifWriter(pmg_struct, symprec=0.1)
        cif_content = str(cif_writer)
        
        # ファイルに書き込み
        with open(output_path, 'w') as f:
            f.write(cif_content)
        
        if verbose:
            print(f"CIFファイルを出力しました: {output_path}")
            print(f"結晶情報:")
            print(f"  組成: {pmg_struct.composition}")
            print(f"  空間群: {crystal.group.number} ({crystal.group.symbol})")
            print(f"  格子パラメータ: a={crystal.lattice.a:.3f}, b={crystal.lattice.b:.3f}, c={crystal.lattice.c:.3f}")
            print(f"  格子角: α={crystal.lattice.alpha:.1f}°, β={crystal.lattice.beta:.1f}°, γ={crystal.lattice.gamma:.1f}°")
            print(f"  体積: {crystal.lattice.volume:.2f} Ų")
            print(f"  サイト数: {len(pmg_struct.sites)}")
        
    except Exception as e:
        raise RuntimeError(f"CIFファイルの書き込みエラー: {e}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="分子のXYZ座標から最適化分子性結晶のCIFファイルを生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s water.xyz
  %(prog)s benzene.xyz -o benzene_crystal.cif -n 8 -f 1.2
  %(prog)s molecule.xyz -s 1,2,14,15 --verbose
        """
    )
    
    parser.add_argument(
        'input_xyz',
        help='入力分子のXYZファイル'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='crystal.cif',
        help='出力CIFファイル名 (デフォルト: crystal.cif)'
    )
    
    parser.add_argument(
        '-n', '--num-mols',
        type=int,
        default=4,
        help='単位格子中の分子数 (デフォルト: 4)'
    )
    
    parser.add_argument(
        '-f', '--factor',
        type=float,
        default=1.1,
        help='体積因子 (デフォルト: 1.1)'
    )
    
    parser.add_argument(
        '-s', '--space-groups',
        help='試行する空間群のリスト（カンマ区切り、例: 1,2,14,15）'
    )
    
    parser.add_argument(
        '--max-attempts',
        type=int,
        default=100,
        help='最大試行回数 (デフォルト: 100)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='ランダムシード'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='詳細な出力'
    )
    
    args = parser.parse_args()
    
    try:
        # XYZファイルを読み込み
        if args.verbose:
            print(f"XYZファイルを読み込み中: {args.input_xyz}")
        
        molecule = read_xyz_file(args.input_xyz)
        
        # 空間群リストを解析
        space_groups = None
        if args.space_groups:
            try:
                space_groups = [int(sg.strip()) for sg in args.space_groups.split(',')]
            except ValueError:
                print("エラー: 空間群リストの形式が正しくありません。例: 1,2,14,15", file=sys.stderr)
                sys.exit(1)
        
        # 分子性結晶を生成
        crystal = generate_molecular_crystal(
            molecule=molecule,
            num_mols=args.num_mols,
            factor=args.factor,
            space_groups=space_groups,
            max_attempts=args.max_attempts,
            seed=args.seed,
            verbose=args.verbose
        )
        
        if crystal is None:
            print("エラー: 有効な分子性結晶を生成できませんでした。", file=sys.stderr)
            print("パラメータを変更して再試行してください。", file=sys.stderr)
            sys.exit(1)
        
        # CIFファイルを出力
        write_cif_file(crystal, args.output, args.verbose)
        
        print(f"成功: 最適化された分子性結晶を {args.output} に保存しました。")
        
    except KeyboardInterrupt:
        print("\n処理が中断されました。")
        sys.exit(1)
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()