const form = document.getElementById("chat-form");
const messageInput = document.getElementById("message");
const hintInput = document.getElementById("system_hint");
const responseText = document.getElementById("response-text");
const responseMeta = document.getElementById("response-meta");
const statusBadge = document.getElementById("status-badge");
const submitButton = document.getElementById("submit-button");

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
    statusBadge.textContent = "已完成";
  } catch (error) {
    responseText.textContent =
      "当前演示没有成功返回模型结果。请检查 .env 是否已配置 OPENAI_API_KEY，并确认服务端依赖已经安装。";
    responseMeta.textContent = String(error);
    statusBadge.textContent = "调用失败";
  } finally {
    submitButton.disabled = false;
  }
});
