# FeNi 结构批量生成脚本说明

## 脚本位置

build_all_structures.py

## 功能

- 从 combined_dataset.xyz 读取全部结构
- 生成对应的结构文件夹与 POSCAR
- 按指定磁序与强度生成 INCAR（包含 MAGMOM）
- 软链接 KPOINTS、POTCAR、submit_vasp.sh

## 用法

```bash
python /home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/0.source/build_all_structures.py --mode AFM1 --intensity high
```

## 参数

- --mode: FM | AFM1 | AFM2 | random
- --intensity: high | medium | low
- --dry-run: 只打印结构总数，不生成文件

## 示例

```bash
python /home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/0.source/build_all_structures.py --mode FM --intensity medium
```

```bash
python /home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/0.source/build_all_structures.py --mode AFM2 --intensity low --dry-run
```
