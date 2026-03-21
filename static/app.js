const form = document.getElementById("chat-form");
const messageInput = document.getElementById("message");
const hintInput = document.getElementById("system_hint");
const responseText = document.getElementById("response-text");
const responseMeta = document.getElementById("response-meta");
const statusBadge = document.getElementById("status-badge");
const submitButton = document.getElementById("submit-button");
const runtimeBadge = document.getElementById("runtime-badge");
const responseMode = document.getElementById("response-mode");
const providerName = document.getElementById("provider-name");
const modelName = document.getElementById("model-name");
const baseUrl = document.getElementById("base-url");
const pageParams = new URLSearchParams(window.location.search);

function applyPreviewState() {
  if (pageParams.get("preview") !== "1") {
    return;
  }

  document.body.classList.add("preview-capture");
  messageInput.value = "最近总拖延，明明知道该准备考试了，但一打开资料就开始焦虑。";
  hintInput.value = "给出温和且具体的 3 步建议";
  responseText.textContent =
    "这更像是启动成本被焦虑放大了，不一定是你不够自律。\n\n可以先试试这 3 步：\n1. 先不要要求自己完整复习，只做 15 分钟的启动动作，比如整理提纲或标出重点章节。\n2. 把“准备考试”拆成今天能完成的一小步，例如做 5 道题或复盘 1 个知识点，降低大脑的抗拒感。\n3. 完成后立刻记录一个小反馈，比如在清单上打勾，让自己看到已经开始，而不是一直停留在想开始。\n\n如果这种焦虑已经连续影响到睡眠、饮食或日常状态，建议尽快联系学校心理中心、辅导员或可信任的人获得线下支持。";
  responseMeta.textContent =
    "预览态示例：页面展示的是本地演示模式下的回复效果，用于 README 截图和项目展示。";
  responseMode.textContent = "本地演示模式";
  statusBadge.textContent = "已完成";
}

async function loadRuntimeMeta() {
  try {
    const response = await fetch("/api/meta");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "无法读取服务信息");
    }

    runtimeBadge.textContent =
      payload.chat_mode === "demo" ? "当前运行：本地演示模式" : "当前运行：模型调用模式";
    providerName.textContent = payload.provider_name;
    modelName.textContent = payload.model_name;
    baseUrl.textContent = payload.base_url;
  } catch (error) {
    runtimeBadge.textContent = "当前运行：服务信息读取失败";
    providerName.textContent = "读取失败";
    modelName.textContent = "读取失败";
    baseUrl.textContent = "读取失败";
  }
}

document.querySelectorAll(".suggestion-chip").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.message || "";
    messageInput.focus();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  const systemHint = hintInput.value.trim();

  if (!message) {
    return;
  }

  submitButton.disabled = true;
  statusBadge.textContent = "生成中";
  responseText.textContent = "正在调用模型，请稍等...";
  responseMeta.textContent = "";

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        system_hint: systemHint || null,
      }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "请求失败");
    }

    responseText.textContent = payload.reply;
    responseMeta.textContent = payload.note;
    responseMode.textContent = payload.mode === "demo" ? "本地演示模式" : "模型调用模式";
    statusBadge.textContent = "已完成";
  } catch (error) {
    responseText.textContent =
      "当前没有成功返回回复。请检查服务是否已启动；如需真实模型结果，请确认 .env 中已正确配置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY。";
    responseMeta.textContent = String(error);
    responseMode.textContent = "调用失败";
    statusBadge.textContent = "调用失败";
  } finally {
    submitButton.disabled = false;
  }
});

applyPreviewState();
loadRuntimeMeta();
