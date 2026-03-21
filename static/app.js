const form = document.getElementById("chat-form");
const messageInput = document.getElementById("message");
const hintInput = document.getElementById("system_hint");
const responseText = document.getElementById("response-text");
const responseMeta = document.getElementById("response-meta");
const statusBadge = document.getElementById("status-badge");
const submitButton = document.getElementById("submit-button");
const runtimeBadge = document.getElementById("runtime-badge");
const responseMode = document.getElementById("response-mode");

async function loadRuntimeMeta() {
  try {
    const response = await fetch("/api/meta");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "无法读取服务信息");
    }

    runtimeBadge.textContent =
      payload.chat_mode === "demo" ? "当前运行：本地演示模式" : "当前运行：模型调用模式";
  } catch (error) {
    runtimeBadge.textContent = "当前运行：服务信息读取失败";
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
      "当前没有成功返回回复。请检查服务是否已启动；如需真实模型结果，请确认 .env 中已正确配置 OPENAI_API_KEY。";
    responseMeta.textContent = String(error);
    responseMode.textContent = "调用失败";
    statusBadge.textContent = "调用失败";
  } finally {
    submitButton.disabled = false;
  }
});

loadRuntimeMeta();
