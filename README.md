# Source Grounded Writing

材料驱动的文档编写与审核。先建立可复用项目资料，再根据模板、可选填写示例和事实材料写文档，审核要求覆盖、事实与图文，最后润色交付。

适用于报告、项目申报、案例说明、验收和测评举证。模板、参考例子、事实和生成稿分别管理；没有参考例子也可以使用。

## 安装到 WorkBuddy

下载 [WorkBuddy 导入包 v1.1.0](https://github.com/XguihuaX/source-grounded-writing/releases/download/v1.1.0/source-grounded-writing-workbuddy-v1.1.0.zip)，无需解压，也无需另外安装 Humanizer：

1. 打开 **专家·技能·连接器 → 技能 → 添加技能 → 上传技能**。
2. 选择上述 ZIP，按客户端提示完成安装，在“已安装”中启用。
3. 新建任务，上传资料或指定工作文件夹，明确使用“材料驱动的文档编写与审核”。

这是 WorkBuddy 官方提供的本地包导入途径。包内按开放平台格式提供技能元数据；结构及脚本已在构建环境检查，WorkBuddy 客户端导入和模型实际执行仍须在目标客户端验证。

- [官方导入说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)
- [官方技能结构与元数据](https://open.workbuddy.cn/docs/skill)

同事安装请选择文件名含 `workbuddy` 的 ZIP；`standard` 包用于其他支持标准 Skill 的宿主，GitHub 自动生成的 Source code 包用于查看源码。

发布到 GitHub 后，可通过仓库或 Release 链接下载。WorkBuddy 官方文档说明，对话搜索安装面向技能市场，自行上传的技能包通过“上传技能”导入；本项目尚未上架 WorkBuddy 技能市场。

## 第一次使用

```text
使用 source-grounded-writing。先整理我提供的材料，建立项目资料库。
先检查是否有可以复用的汇总；需要脱敏的内容列出具体位置，由我确认。
已有解读能用就直接复用，只有缺失部分才补读。先给我项目理解，不开始写报告。
```

项目汇总确认后：

```text
使用刚才确认的项目资料，按我上传的模板编写完整文档。
参考例子只借鉴写法。先给编写框架，确认后再写，并完成事实、图文和要求审核。
```

后续补充：

```text
这份纪要补入已有项目，只更新受影响的汇总和正在编写的部分，其他内容保留。
```

## 两个工作模式

- **资料准备**：接收分类 → 人工确定脱敏范围 → 复用或补充解读 → 项目汇总 → 用户审核保存。
- **编写审核**：读取要求与可选例子 → 匹配证据 → 框架确认 → 完整编写 → 二次审核 → 自然化交付。

已有资料库直接复用；不因为开始新文稿就重新转录全部视频。新材料只处理变化部分。生成文稿不自动成为事实来源。

本包已内置 `op7418/Humanizer-zh` 的现有本地快照，润色步骤会读取完整规则执行。同事只需导入本包，无需单独下载安装 Humanizer。上游正文、README 和 MIT 许可证原样保留；来源、文件校验值及版本限制见 `references/humanizer-zh/SOURCE.json`。本包的事实、文体与模板约束仍优先，不为润色增加个人经历或业务结果。

## 视频材料的当前使用方式

由材料准备端先在本地完成视频转录、关键画面阅读和图文汇总，再向 WorkBuddy 提供汇总、实际图片及覆盖说明。已有解读直接复用；只有不足的具体问题需要局部补读。本版本暂不迁移语音转录或下载工具，也不会自动上传视频到外部 ASR。Markdown 配图随汇总一同提供，或交接内嵌图片的 Word，避免跨电脑缺图。

## 能力与环境

核心流程是文本指令与模板，使用宿主已有的文件、文档和图片读取工具。视频解读需要能取得字幕/转录及画面；图片编辑、Office 导出依赖实际工具。缺少某工具时保留可完成的工作并准确说明范围。

可选初始化工具只需 Python 3.8+ 标准库，不需要安装库，不访问网络，不读取客户材料。没有 Python 时可由宿主文件工具建立相同结构。

```text
python "<技能目录>/scripts/init_library.py" --root "<资料库目录>" --project "<项目名称>"
```

## 其他宿主与源码

`skills/source-grounded-writing/` 是标准 SKILL.md 目录。将该目录安装到目标宿主支持的技能位置即可；使用前按该宿主的安装说明操作。WorkBuddy 版本与标准版使用相同正文和资源，仅调整元数据。

本仓库只含通用规则、模板和初始化代码，不含用户项目资料、私人路径或真实客户案例。用户资料保存在自己的工作目录，不保存到技能安装目录。

## 本地校验与打包

```text
python -m unittest discover -s tests -v
python tools/build_release.py
```

产物位于 `dist/`：WorkBuddy 导入 ZIP、标准技能 ZIP 和 SHA256 校验值。构建脚本只打包技能目录的明确文件，不递归打包工作区或客户资料。

## GitHub 分发

仓库：[XguihuaX/source-grounded-writing](https://github.com/XguihuaX/source-grounded-writing)。下载入口：[Releases](https://github.com/XguihuaX/source-grounded-writing/releases)。

维护者：[XguihuaX](https://github.com/XguihuaX)。源码与可导入包一起发布；技能市场上架及搜索目录收录另行完成。

本仓库工作流和脚本采用 MIT 许可，内置 Humanizer 保留其上游作者与独立 MIT 许可证，不将其标为本项目原创。README 中的客户资料使用约定只约束本工具执行，不替代用户组织的材料使用决定。
