# 模型接入说明

[中文](model-integration.md) | [English](model-integration.en.md)

这份文档专门说明 Web 端如何接入不同大模型，以及为什么钉钉版可以“直接用模型”，而本地 Web 项目需要单独配置模型后端。

## 先说结论

- 当前 Web 项目使用的是 `OpenAI Python SDK`
- 后端走的是 `OpenAI 兼容接口`
- 只要模型提供商兼容 OpenAI 的 Chat Completions 接口，就可以通过改 `.env` 接入
- 当前仓库已支持：
  - 本地演示模式
  - OpenAI 兼容模型调用模式
  - `OPENAI_API_KEY` 或 `DEEPSEEK_API_KEY` 两种密钥命名方式
  - `MODEL_API_KEY_ENV` 显式指定当前模型该读取哪个密钥变量
  - 一键配置脚本和启动前兼容性检查

## 为什么钉钉版不用你自己填 API Key，Web 端却要？

钉钉版之所以能直接调用模型，通常是因为模型能力托管在钉钉平台或你在钉钉应用后台已经完成了平台侧绑定。也就是说：

- 模型凭证和调用链路在钉钉平台内部
- 你的 Web 项目并不会自动继承这部分平台能力
- Web 项目是独立后端，必须自己知道“调哪个模型服务、用什么地址、用什么密钥”

所以，钉钉里能直接用 `DeepSeek R1`，不等于本地 FastAPI 服务也能自动调用它。

## 当前项目的接入方式

当前项目默认从 `.env` 读取下面这些配置：

| 变量名 | 作用 |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI 兼容接口密钥 |
| `DEEPSEEK_API_KEY` | DeepSeek 密钥，未填 `OPENAI_API_KEY` 时会回退使用 |
| `OPENAI_BASE_URL` | 模型服务地址 |
| `MODEL_NAME` | 使用的模型名称 |
| `MODEL_PROVIDER` | 页面展示用的提供商名称 |
| `MODEL_API_KEY_ENV` | 当前模型应优先读取哪个密钥变量 |
| `MODEL_TEMPERATURE` | 温度参数，部分模型会自动忽略 |
| `DEMO_MODE` | 强制启用本地演示模式 |

## 先用一键脚本，而不是手改

项目根目录现在提供了 3 组可直接执行的脚本：

```powershell
.\setup-openai.ps1
.\setup-deepseek-chat.ps1
.\setup-deepseek-r1.ps1
```

也可以双击对应的 `.bat` 文件。

这些脚本会自动：

- 初始化 `.env`
- 写入正确的 `OPENAI_BASE_URL`
- 写入 `MODEL_NAME`
- 写入 `MODEL_PROVIDER`
- 写入 `MODEL_API_KEY_ENV`
- 尽量保留其他已有配置

但这 3 个脚本并不代表“不需要 API Key”。

它们的含义是：项目已经内置了这 3 种常用接入预设，方便你快速切到对应供应商。

- `.\setup-openai.ps1`：写入 OpenAI 官方接口配置，真实调用仍需要 `OPENAI_API_KEY`
- `.\setup-deepseek-chat.ps1`：写入 DeepSeek Chat 配置，真实调用仍需要 `DEEPSEEK_API_KEY`
- `.\setup-deepseek-r1.ps1`：写入 DeepSeek R1 配置，真实调用仍需要 `DEEPSEEK_API_KEY`

如果没有填写对应 Key，脚本也能执行成功，但服务只会回退到本地演示模式，不会真正调用远程模型。

如果你接的不是 OpenAI 或 DeepSeek 官方接口，也可以直接复用同一个脚本写入自定义 OpenAI 兼容配置，例如：

```powershell
.\.venv\Scripts\python scripts\setup_model_config.py `
  --preset openai `
  --provider-name OpenAI-Compatible `
  --base-url https://your-provider.example.com/v1 `
  --model-name your-model-name `
  --api-key-env OPENAI_API_KEY `
  --api-key your_api_key
```

这时就不再默认宣称“完美兼容”，而是建议你立刻跑一遍 `check_model_config.py`，必要时再加 `--probe` 做真实探测。

配置完成后，建议立刻执行：

```powershell
.\.venv\Scripts\python scripts\check_model_config.py
```

它会直接告诉你当前配置是否真的能调用模型，而不是等到 Web 端报错后再排查。

如果已经填入真实密钥，还可以继续执行：

```powershell
.\.venv\Scripts\python scripts\check_model_config.py --probe
```

这会实际发起一次最小请求，用来验证“当前 API 能不能被本项目真实调通”。

## 如何切换不同模型

### 1. 本地演示模式

适合调试页面，不依赖任何真实模型：

```env
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
MODEL_PROVIDER=Local Demo
MODEL_API_KEY_ENV=OPENAI_API_KEY
MODEL_TEMPERATURE=0.7
DEMO_MODE=true
```

### 2. OpenAI 模型

```env
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
MODEL_PROVIDER=OpenAI
MODEL_API_KEY_ENV=OPENAI_API_KEY
MODEL_TEMPERATURE=0.7
DEMO_MODE=false
```

### 3. DeepSeek Chat

```env
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
MODEL_PROVIDER=DeepSeek
MODEL_API_KEY_ENV=DEEPSEEK_API_KEY
MODEL_TEMPERATURE=0.7
DEMO_MODE=false
```

### 4. DeepSeek R1 / Reasoner

```env
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-reasoner
MODEL_PROVIDER=DeepSeek
MODEL_API_KEY_ENV=DEEPSEEK_API_KEY
MODEL_TEMPERATURE=0.7
DEMO_MODE=false
```

说明：当前代码已经对 `deepseek-reasoner` 做了兼容处理，不会再强行传 `temperature` 参数。

## 现在“兼容”的判断标准是什么

这里要说清楚一个边界：不是所有自称“OpenAI 兼容”的接口，都一定和本项目百分百无缝兼容。

同样也要说清楚：仓库里提供了 `setup-openai.ps1`、`setup-deepseek-chat.ps1`、`setup-deepseek-r1.ps1`，并不等于这些模型可以不填 Key 直接调用，它们只是项目内置的 3 个接入模板。

当前仓库对下面两类接口可以做到明确支持：

- OpenAI 官方接口
- DeepSeek 官方接口

原因是这两类接口的地址、模型名和已知参数差异，项目里都做了明确适配。

对于其他 OpenAI 兼容服务，是否“完美兼容”取决于对方是否同时满足：

- 支持 Chat Completions 调用方式
- 支持当前使用的模型名
- 接受当前消息格式
- 不要求额外的鉴权头或特殊字段
- 不拒绝 `temperature` 等常用参数

如果你的服务不满足这些条件，就不能简单算作“完美兼容”。

所以当前项目的策略是：

- 用 `MODEL_API_KEY_ENV` 明确当前模型该读取哪个密钥
- 用 `/api/compatibility` 和 `scripts/check_model_config.py` 提前做基础检查
- 对已知差异模型直接做兼容处理，比如 `deepseek-reasoner`

这比只在 README 里写“支持 OpenAI 兼容接口”更可靠，也更适合别人拿去直接接自己的模型服务。

## 如何体现“不同模型提供不同心理辅导”

需要分清两层：

### 第一层：模型本身不同

- `deepseek-chat` 更偏快速直接
- `deepseek-reasoner` 更偏推理和多步展开
- 不同模型对同一个心理支持问题，本来就可能给出不同风格、不同结构的回复

### 第二层：系统提示词和策略不同

即使使用同一个模型，也可以通过不同提示词策略让它扮演不同的辅导角色，例如：

- 温和陪伴型
- 行动拆解型
- 学习计划型
- 更简洁的快速建议型

当前 Web 端已经支持在“补充要求”里输入：

- `更简洁`
- `更鼓励`
- `更温柔`
- `按 3 步计划说`

如果后续要做成真正的“多模型 + 多辅导策略”，建议再往前走一步：把“模型选择”和“辅导风格”拆成两个独立配置，而不是都塞进同一个提示词里。

## Web 页面现在能看到什么

当前页面右侧已经会显示：

- 当前提供商
- 当前模型
- API 地址
- 当前接入兼容检查结果

当前页面左侧还支持直接下拉选择：

- 模型目标
- 辅导风格

这样别人打开 Web 页面时，不需要翻代码也能知道它当前接的是哪一类模型。

## 已接入的兼容处理

- 未配置密钥时自动进入本地演示模式
- 配置 `OPENAI_API_KEY` 或 `DEEPSEEK_API_KEY` 都可以
- 会根据 `MODEL_API_KEY_ENV` 优先读取正确的密钥变量
- `deepseek-reasoner` 会自动跳过不适合的 `temperature` 参数
- 提供一键配置脚本和兼容性检查接口

## 参考资料

- [DeepSeek API 快速开始](https://api-docs.deepseek.com/zh-cn/)
- [DeepSeek 模型与价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)
- [DeepSeek Reasoning Model](https://api-docs.deepseek.com/guides/reasoning_model)

## OrcaRouter

OrcaRouter 可通过现有通用配置脚本作为 OpenAI 兼容提供商接入。参阅 [OrcaRouter 接入指南](orcarouter.md)，按步骤配置独立的 `ORCAROUTER_API_KEY`、API 地址、模型名，并验证真实请求。
