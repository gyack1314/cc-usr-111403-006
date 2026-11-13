# 湖表CHECK约束 · 在线验证与生效栅栏

这里保存园区成本、原料及供销资料的基础读取接口，样例值为开发用合成记录，不对应真实交易。table.py是单目录实例的同步CAS表替身，完整日志可导出，尚无约束目录或验证任务。checks.py已有行谓词，但当前表提交未安装CHECK门禁。服务重启可由快照及日志复建，新增验证状态需自行保存。

`lake/checks.py`、`lake/table.py`描述当前接口。`lake/storage.py`使用有序JSON编码、SHA256内容身份及不可变正文；`data/source.json`保存现有资料。字段约定见[资料契约](docs/contracts.md)，字段缺失与显式null不同。

使用Python 3.11。依赖在requirements.txt固定，空清单表示仅标准库。

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q lake tests
python -m lake
```

以上入口读取当前资料及检查已有接口。它不执行新增查询，输出资料分区名称和正文摘要。可在Linux容器执行相同入口：

```sh
docker build -t park-lake .
docker run --rm --network=none park-lake python -m unittest discover -s tests -v
docker run --rm --network=none park-lake python -m lake
```

运行生成的正文与临时文件存放在`.runtime/`；不得把本机配置或凭据放入资料正文。
