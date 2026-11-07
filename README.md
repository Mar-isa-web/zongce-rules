# zongce-rules · 高校综合测评评分细则开放数据集

**Open dataset of comprehensive-evaluation scoring rules for Chinese universities.**

224 条结构化的综合测评加分规则，覆盖五育（德/智/体/美/劳）17 个类别，
来自某高校 2026 年修订的官方评分细则——经 OCR 与人工结构化，
**已在生产环境驱动一个真实班级的综测自动核算系统**（Next.js + SQLite，
公网部署，累计核算全班的学年综测分数）。

## 数据速览

| 指标 | 值 |
|---|---|
| 规则条数 | 224 |
| 五育覆盖 | 德育 76 · 智育 60 · 体育 56 · 美育 20 · 劳育 12 |
| 类别 | 17 类（竞赛/论文/专利/证书/运动会/学生干部…） |
| 分值范围 | 0.25 ~ 35（志愿类支持按量计分：分值 × 小时数） |
| 学年版本 | 2025-2026 |

字段定义见 [SCHEMA.md](SCHEMA.md)。

## 快速使用

```bash
python validate.py          # 结构校验（CI 每次推送自动跑）
```

```python
import json
rules = json.load(open("data/rules.v1.json", encoding="utf-8"))
comp = [r for r in rules if r["category"] == "竞赛" and r["level"] == "国家级"]
print([(r["grade"], r["points"]) for r in comp[:5]])
```

## 为什么开源这个

综合测评（综测）是内地高校普遍运行的量化评价体系，但评分细则通常只是
一份 PDF/纸质表格，**没有机器可读的版本**。这意味着每个做综测工具的
学生开发者都要从零 OCR、从零结构化一遍。

这个仓库把其中一所高校的完整细则做成带校验的开源数据，希望：

1. **做同类工具的同学**直接拿去当测试数据或种子数据；
2. **其他学校的同学**按同一格式提交自己学校的细则（见下），
   逐步长成一个跨校的综测规则语料库。

## 用你学校的规则做贡献

1. Fork 本仓库，在 `data/` 下新建子目录（如 `data/<school-code>/rules.v1.json`）；
2. 按同样 11 字段结构化你校细则；**抹去校名**（字段化重述，勿照搬原文）；
3. 在 `validate.py` 顶部的 `BANNED_SUBSTRINGS` 里加上你校名称，
   确保敏感词永远进不了仓库；
4. `python validate.py data/<school-code>/rules.v1.json` 通过后提 PR。

### 匿名化红线（CI 强制）

- 不得出现任何真实校名、学院名；
- 不得出现连续 ≥8 位数字（疑似学号/证件号）；
- 不得出现任何学生个人信息。

## License

数据与本仓库代码均以 [CC BY-NC-SA 4.0](LICENSE) 提供：署名、非商业、相同方式共享。

## Roadmap

- [ ] 多校目录结构与贡献模板
- [ ] 规则英译版（术语表对齐）
- [ ] 最小核算引擎参考实现（五育加权/封顶/排名的纯函数）
