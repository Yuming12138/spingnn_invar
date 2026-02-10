# AFM1 自动分批提交说明

## 脚本

- submit_afm1_array.sh: 单个作业数组脚本
- submit_afm1_batches.sh: 一次性提交三组数组（high/medium/low）
- auto_submit_afm1_batches.sh: 自动分批提交并等待上一批完成

## 推荐用法

自动分批并等待上一批完成后再提交下一批：

```bash
bash /fs1/home/liummm3/WORK/chenguangming/1.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/0.batch_submit/auto_submit_afm1_batches.sh
```

## 参数

可以通过环境变量调整提交行为：

- TOTAL: 结构总数，默认 505
- BATCH_SIZE: 每批结构数，默认 10
- CONCURRENCY: 每个强度数组并发数，默认 1
- POLL_SECONDS: 轮询间隔秒数，默认 60

示例：

```bash
TOTAL=505 BATCH_SIZE=10 CONCURRENCY=1 POLL_SECONDS=60 bash auto_submit_afm1_batches.sh
```

## 说明

- 自动脚本会依次提交 high/medium/low 三个数组
- 每批次会等待三组全部完成后再进入下一批
- 如果希望后台运行，可配合 nohup 或 tmux 使用
