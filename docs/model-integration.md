# 模型接入说明

这份文档专门说明 Web 端如何接入不同大模型，以及为什么钉钉版可以“直接用模型”，而本地 Web 项目需要单独配置模型后端。

## 先说结论

- 当前 Web 项目使用的是 `OpenAI Python SDK`
- 后端走的是 `OpenAI 兼容接口`
- 只要模型提供商兼容 OpenAI 的 Chat Completions 接口，就可以通过改 `.env` 接入
- 当前仓库已支持：
  - 本地演示模式
  - OpenAI 兼容模型调用模式
  - `OPENAI_API_KEY` 或 `DEEPSEEK_API_KEY` 两种密钥命名方式

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
| `MODEL_TEMPERATURE` | 温度参数，部分模型会自动忽略 |
| `DEMO_MODE` | 强制启用本地演示模式 |

## 如何切换不同模型

### 1. 本地演示模式

适合调试页面，不依赖任何真实模型：

```env
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
MODEL_PROVIDER=Local Demo
MODEL_TEMPERATURE=0.7
DEMO_MODE=true
```

### 2. OpenAI 模型

```env
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
MODEL_PROVIDER=OpenAI
MODEL_TEMPERATURE=0.7
DEMO_MODE=false
```

### 3. DeepSeek Chat

```env
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
MODEL_PROVIDER=DeepSeek
MODEL_TEMPERATURE=0.7
DEMO_MODE=false
```

### 4. DeepSeek R1 / Reasoner

```env
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-reasoner
MODEL_PROVIDER=DeepSeek
MODEL_TEMPERATURE=0.7
DEMO_MODE=false
```

说明：当前代码已经对 `deepseek-reasoner` 做了兼容处理，不会再强行传 `temperature` 参数。

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

当前页面左侧还支持直接下拉选择：

- 模型目标
- 辅导风格

这样别人打开 Web 页面时，不需要翻代码也能知道它当前接的是哪一类模型。

## 已接入的兼容处理

- 未配置密钥时自动进入本地演示模式
- 配置 `OPENAI_API_KEY` 或 `DEEPSEEK_API_KEY` 都可以
- `deepseek-reasoner` 会自动跳过不适合的 `temperature` 参数

## 参考资料

- [DeepSeek API 快速开始](https://api-docs.deepseek.com/zh-cn/)
- [DeepSeek 模型与价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)
- [DeepSeek Reasoning Model](https://api-docs.deepseek.com/guides/reasoning_model)
