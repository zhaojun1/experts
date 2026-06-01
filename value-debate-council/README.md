# Value Debate Council - 价值投资辨论会

四位不同投资哲学的分析师逐轮辩论，通过正反交锋、数据裁决、格局定论，辩出经得起考验的投资结论。

## 类型

Team 型（多角色协作团队）

## 辩论文本流程

1. **Phase 1（并行独立研判）**：四位分析师各自独立分析——质量护城河、逆向风险、财务估值、战略竞争
2. **Phase 2（串行辩论交锋）**：
   - 回合 1：质量派 vs 怀疑派 正反对决
   - 回合 2：财务派用数字裁决
   - 回合 3：战略派从行业格局定论
3. **Phase 3（汇编结论）**：主理人综合辩论成果，输出最终投资判断

## 团队成员

| 角色 | 花名 | 投资哲学 | 风格 |
|------|------|---------|------|
| 研究主编 | 顾览之 | — | 编排、主持、汇编 |
| 质量护城河分析师 | 巴品优 | 巴菲特 + 段永平 | 力主买入的乐观派 |
| 逆向风险分析师 | 芒审否 | 芒格 | 天生说"不"的怀疑派 |
| 财务估值分析师 | 唐析财 | 老唐（唐朝） | 只看数字的务实派 |
| 战略竞争分析师 | 波策观 | 波特 + 柯林斯 | 拉开镜头的全局派 |

## 使用示例

- 帮我辨论分析XX公司，值得投吗？
- 帮我看XX的护城河和竞争格局怎么样
- 帮我算算XX现在估值合不合理

## 头像

头像已自动生成在 `avatars/` 目录下。如需替换为自定义头像，要求：
- 格式：PNG（推荐）或 JPG
- 尺寸：512×512 px
- 大小：单张不超过 500KB

## 安装

将专家包目录放到以下路径：

```
~/.workbuddy/plugins/marketplaces/my-experts/plugins/value-debate-council/
```

然后运行注册命令使其在 WorkBuddy 中可见：

```bash
python3 scripts/register_expert.py ~/.workbuddy/plugins/marketplaces/my-experts/plugins/value-debate-council/
```

## 打包分享

```bash
zip -r value-debate-council.zip value-debate-council/
```
