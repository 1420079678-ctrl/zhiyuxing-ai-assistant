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
const modelTargetInput = document.getElementById("model_target");
const responseStyleInput = document.getElementById("response_style");
const modelHelper = document.getElementById("model-helper");
const styleHelper = document.getElementById("style-helper");
const compatibilityButton = document.getElementById("compatibility-button");
const compatibilitySummary = document.getElementById("compatibility-summary");
const compatibilityList = document.getElementById("compatibility-list");
const resetSessionButton = document.getElementById("reset-session-button");
const feedbackHelpfulButton = document.getElementById("feedback-helpful");
const feedbackNeedsMoreButton = document.getElementById("feedback-needs-more");
const feedbackStatus = document.getElementById("feedback-status");
const sessionIdText = document.getElementById("session-id");
const memoryCountText = document.getElementById("memory-count");
const riskLevelText = document.getElementById("risk-level");
const knowledgeCountText = document.getElementById("knowledge-count");
const historyList = document.getElementById("history-list");
const knowledgeList = document.getElementById("knowledge-list");
const pageParams = new URLSearchParams(window.location.search);
const previewMode = pageParams.get("preview") === "1";
const SESSION_STORAGE_KEY = "zhiyuxing_demo_session_id";

let runtimeMeta = null;
let currentSessionId = window.localStorage.getItem(SESSION_STORAGE_KEY) || "";
let currentAssistantMessageId = null;

function buildPreviewMeta() {
  return {
    chat_mode: "demo",
    provider_name: "Local Demo",
    model_name: "builtin-demo",
    base_url: "local://preview",
    knowledge_document_count: 5,
    available_models: [
      {
        id: "configured",
        label: "当前配置（预览态）",
        provider_name: "Local Demo",
        model_name: "builtin-demo",
        mode: "demo",
        available: true,
        reason: "预览态不会发起真实模型调用。",
      },
      {
        id: "demo",
        label: "本地演示模式",
        provider_name: "Local Demo",
        model_name: "builtin-demo",
        mode: "demo",
        available: true,
      },
    ],
    available_styles: [
      { id: "balanced", label: "平衡建议", helper_text: "兼顾共情、行动建议和安全提醒" },
      { id: "warm", label: "温和陪伴", helper_text: "更重视情绪承接与安抚" },
      { id: "structured", label: "三步计划", helper_text: "用更清晰的分步结构给建议" },
      { id: "encouraging", label: "鼓励支持", helper_text: "语气更积极，强调可恢复性" },
      { id: "brief", label: "简洁直接", helper_text: "减少铺垫，更快给出核心建议" },
    ],
  };
}

function riskLabel(level) {
  if (level === "high") {
    return "高风险表达";
  }
  if (level === "medium") {
    return "需要额外关注";
  }
  return "常规支持场景";
}

function setRiskAppearance(level, label) {
  riskLevelText.textContent = label;
  riskLevelText.className = `risk-indicator risk-indicator-${level || "low"}`;
}

function formatKnowledgeSummary(hitCount) {
  const total = runtimeMeta?.knowledge_document_count || 0;
  if (!total) {
    return `${hitCount} 命中`;
  }
  return `${hitCount} 命中 / ${total} 文档`;
}

function updateSessionBadge() {
  sessionIdText.textContent = currentSessionId || "新会话（发送后创建）";
}

function setFeedbackState(enabled, text) {
  feedbackHelpfulButton.disabled = !enabled;
  feedbackNeedsMoreButton.disabled = !enabled;
  feedbackStatus.textContent = text;
}

function renderCompatibilityStatus(status) {
  if (status === "ok") {
    return "检查通过";
  }
  if (status === "warning") {
    return "存在提醒";
  }
  return "需要修正";
}

function updateModelHelper() {
  if (!runtimeMeta) {
    return;
  }

  const option = runtimeMeta.available_models.find((item) => item.id === modelTargetInput.value);
  if (!option) {
    modelHelper.textContent = "当前模型目标不可用。";
    return;
  }

  if (option.id === "configured") {
    modelHelper.textContent =
      option.reason || "使用 .env 中的默认模型配置；如果没配密钥，会自动回退到本地演示模式。";
    return;
  }

  if (option.id === "demo") {
    modelHelper.textContent = "不调用真实模型，适合展示页面流程、记忆和知识检索效果。";
    return;
  }

  modelHelper.textContent = option.available
    ? `将尝试调用 ${option.provider_name} / ${option.model_name}。`
    : option.reason || "当前模型不可用。";
}

function updateStyleHelper() {
  if (!runtimeMeta) {
    return;
  }

  const option = runtimeMeta.available_styles.find((item) => item.id === responseStyleInput.value);
  styleHelper.textContent = option ? option.helper_text : "当前风格不可用。";
}

function populateModelOptions(options) {
  modelTargetInput.innerHTML = "";

  options.forEach((option) => {
    const element = document.createElement("option");
    element.value = option.id;
    element.textContent = option.available ? option.label : `${option.label}（${option.reason || "未配置"}）`;
    element.disabled = !option.available;
    if (option.id === "configured") {
      element.selected = true;
    }
    modelTargetInput.appendChild(element);
  });
}

function populateStyleOptions(options) {
  responseStyleInput.innerHTML = "";

  options.forEach((option) => {
    const element = document.createElement("option");
    element.value = option.id;
    element.textContent = option.label;
    if (option.id === "balanced") {
      element.selected = true;
    }
    responseStyleInput.appendChild(element);
  });
}

function renderCompatibilityReport(payload) {
  compatibilitySummary.textContent = `${renderCompatibilityStatus(payload.status)}：${payload.summary}`;
  compatibilityList.innerHTML = "";

  (payload.checks || []).forEach((item) => {
    const element = document.createElement("li");
    element.className = `compatibility-item compatibility-item-${item.status}`;
    element.textContent = `[${String(item.status || "").toUpperCase()}] ${item.message}`;
    compatibilityList.appendChild(element);
  });

  if (payload.recommended_setups && payload.recommended_setups.length > 0) {
    payload.recommended_setups.forEach((item) => {
      const element = document.createElement("li");
      element.className = "compatibility-item compatibility-item-setup";
      element.textContent = `可直接执行：${item.command}`;
      compatibilityList.appendChild(element);
    });
  }
}

function renderHistory(messages) {
  historyList.innerHTML = "";

  if (!messages || messages.length === 0) {
    historyList.innerHTML = "<li>当前会显示最近几轮对话，便于确认会话记忆和本地持久化已生效。</li>";
    return;
  }

  messages.forEach((message) => {
    const item = document.createElement("li");
    item.className = `history-item history-item-${message.role}`;

    const title = document.createElement("div");
    title.className = "history-item-title";
    const roleText = message.role === "user" ? "你" : "助手";
    const modelText = message.provider_name ? ` · ${message.provider_name}` : "";
    title.textContent = `${roleText}${modelText}`;

    const content = document.createElement("p");
    content.className = "history-item-content";
    content.textContent = message.content;

    item.appendChild(title);
    item.appendChild(content);
    historyList.appendChild(item);
  });
}

function renderKnowledgeHits(hits) {
  knowledgeList.innerHTML = "";

  if (!hits || hits.length === 0) {
    knowledgeList.innerHTML = "<li>本轮没有命中知识库片段，会直接按常规对话生成回复。</li>";
    knowledgeCountText.textContent = formatKnowledgeSummary(0);
    return;
  }

  hits.forEach((hit) => {
    const item = document.createElement("li");
    item.className = "knowledge-item";

    const title = document.createElement("div");
    title.className = "knowledge-item-title";
    title.textContent = `${hit.title} · ${hit.score}`;

    const excerpt = document.createElement("p");
    excerpt.className = "knowledge-item-excerpt";
    excerpt.textContent = hit.excerpt;

    const source = document.createElement("span");
    source.className = "knowledge-item-source";
    source.textContent = hit.source_path;

    item.appendChild(title);
    item.appendChild(excerpt);
    item.appendChild(source);
    knowledgeList.appendChild(item);
  });

  knowledgeCountText.textContent = formatKnowledgeSummary(hits.length);
}

function resetChatPanels() {
  responseText.textContent = "这里会显示回复内容，也可以先点击上方建议问题快速体验。";
  responseMeta.textContent = "";
  responseMode.textContent = "等待对话";
  memoryCountText.textContent = "0";
  renderHistory([]);
  renderKnowledgeHits([]);
  setRiskAppearance("low", "常规支持场景");
  setFeedbackState(false, "反馈功能会在生成回复后启用。");
}

function rememberSession(sessionId) {
  currentSessionId = sessionId;
  if (sessionId) {
    window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  } else {
    window.localStorage.removeItem(SESSION_STORAGE_KEY);
  }
  updateSessionBadge();
}

function restoreLatestAssistantMessage(messages) {
  const latestAssistant = [...messages].reverse().find((message) => message.role === "assistant");
  if (!latestAssistant) {
    return;
  }

  currentAssistantMessageId = latestAssistant.id;
  responseText.textContent = latestAssistant.content;
  responseMeta.textContent = "已从本地持久化记录恢复最近一次对话。";
  responseMode.textContent = latestAssistant.provider_name
    ? `${latestAssistant.provider_name} / ${latestAssistant.model_name || "unknown"}`
    : "历史记录";
  setFeedbackState(true, "你也可以对最近一条回复继续补充反馈。");
  setRiskAppearance(latestAssistant.risk_level || "low", riskLabel(latestAssistant.risk_level || "low"));
}

async function loadSessionHistory(sessionId, options = {}) {
  const shouldRestoreLatest = options.restoreLatest !== false;

  if (!sessionId || previewMode) {
    renderHistory([]);
    return;
  }

  try {
    const response = await fetch(`/api/session/${encodeURIComponent(sessionId)}`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "无法读取会话记录");
    }

    renderHistory(payload.messages || []);
    if (shouldRestoreLatest) {
      restoreLatestAssistantMessage(payload.messages || []);
    }
  } catch (error) {
    historyList.innerHTML = `<li class="compatibility-item compatibility-item-error">${String(error)}</li>`;
  }
}

function applyPreviewState() {
  document.body.classList.add("preview-capture");
  modelTargetInput.value = "demo";
  responseStyleInput.value = "structured";
  messageInput.value = "最近总拖延，明明知道该准备考试了，但一打开资料就开始焦虑。";
  hintInput.value = "更关注考试前启动困难";
  responseText.textContent =
    "这更像是启动成本被焦虑放大了，不一定是你不够自律。\n\n当前更适合的顺序是：先稳住情绪，再缩小任务，最后决定是否继续推进。\n\n建议按下面 3 步来：\n1. 先不要要求自己完整复习，只做 15 分钟的启动动作，比如整理提纲或标出重点章节。\n2. 把“准备考试”拆成今天能完成的一小步，例如做 5 道题或复盘 1 个知识点，降低大脑的抗拒感。\n3. 完成后立刻记录一个小反馈，比如在清单上打勾，让自己看到已经开始，而不是一直停留在想开始。\n\n额外提醒：如果这种焦虑已经连续影响到睡眠、饮食或日常状态，建议尽快联系学校心理中心、辅导员或可信任的人获得线下支持。";
  responseMeta.textContent = "预览态示例：页面展示了会话记忆、知识检索和风险提醒在一次完整回复中的呈现方式。";
  responseMode.textContent = "Local Demo / builtin-demo";
  statusBadge.textContent = "预览态";
  compatibilitySummary.textContent = "预览态示例：这里会显示 API 接入检查结果。";
  compatibilityList.innerHTML = "<li>预览态下不实际请求接口，仅用于页面展示。</li>";

  rememberSession("preview-session");
  memoryCountText.textContent = "4";
  setRiskAppearance("medium", "需要额外关注");
  knowledgeCountText.textContent = formatKnowledgeSummary(2);
  renderHistory([
    { role: "user", content: "最近总拖延，越想开始越焦虑。" },
    { role: "assistant", content: "先把目标压缩到 15 分钟，只处理一个最小动作。" },
    { role: "user", content: "我快考试了，一打开书就紧张。" },
    { role: "assistant", content: "这次回复会继续沿用前面的状态判断和学习建议节奏。" },
  ]);
  renderKnowledgeHits([
    {
      title: "拖延与启动困难",
      excerpt: "把任务切成 10 到 15 分钟的启动动作，先恢复最小的执行感。",
      source_path: "knowledge_base/02-study-actions.md",
      score: 4.2,
    },
    {
      title: "考试压力与恢复",
      excerpt: "当考试焦虑已经影响睡眠时，建议同时安排线下支持和短时复习块。",
      source_path: "knowledge_base/04-sleep-and-recovery.md",
      score: 3.8,
    },
  ]);
  setFeedbackState(true, "预览态下展示反馈入口，不会真正提交。");
}

async function loadCompatibility() {
  if (previewMode) {
    return;
  }

  compatibilityButton.disabled = true;
  compatibilitySummary.textContent = "正在检查当前模型接入配置...";

  try {
    const response = await fetch("/api/compatibility");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "无法读取兼容性信息");
    }

    renderCompatibilityReport(payload);
  } catch (error) {
    compatibilitySummary.textContent = "兼容性检查失败，请确认服务已正常启动。";
    compatibilityList.innerHTML = `<li class="compatibility-item compatibility-item-error">${String(error)}</li>`;
  } finally {
    compatibilityButton.disabled = false;
  }
}

function syncRuntimeInfo(payload) {
  runtimeBadge.textContent =
    payload.chat_mode === "demo" ? "当前运行：本地演示模式" : "当前运行：模型调用模式";
  providerName.textContent = payload.provider_name;
  modelName.textContent = payload.model_name;
  baseUrl.textContent = payload.base_url;
  knowledgeCountText.textContent = formatKnowledgeSummary(0);
  updateSessionBadge();
  if (!currentSessionId) {
    setRiskAppearance("low", "常规支持场景");
  }
}

async function loadRuntimeMeta() {
  try {
    if (!previewMode) {
      const response = await fetch("/api/meta");
      const metaPayload = await response.json();
      if (!response.ok) {
        throw new Error(metaPayload.detail || "无法读取服务信息");
      }
      runtimeMeta = metaPayload;
    } else {
      runtimeMeta = buildPreviewMeta();
    }

    populateModelOptions(runtimeMeta.available_models || []);
    populateStyleOptions(runtimeMeta.available_styles || []);
    syncRuntimeInfo(runtimeMeta);
    updateModelHelper();
    updateStyleHelper();

    if (previewMode) {
      applyPreviewState();
      return;
    }

    if (currentSessionId) {
      await loadSessionHistory(currentSessionId);
      statusBadge.textContent = "已恢复会话";
    }

    await loadCompatibility();
  } catch (error) {
    runtimeBadge.textContent = "当前运行：服务信息读取失败";
    providerName.textContent = "读取失败";
    modelName.textContent = "读取失败";
    baseUrl.textContent = "读取失败";
    compatibilitySummary.textContent = "兼容性检查不可用";
    compatibilityList.innerHTML = `<li class="compatibility-item compatibility-item-error">${String(error)}</li>`;
  }
}

async function submitFeedback(rating) {
  if (previewMode) {
    feedbackStatus.textContent = "预览态不提交反馈；本地启动后会写入 SQLite。";
    return;
  }

  if (!currentSessionId || !currentAssistantMessageId) {
    feedbackStatus.textContent = "当前没有可提交反馈的回复。";
    return;
  }

  setFeedbackState(false, "正在提交反馈...");

  try {
    const response = await fetch("/api/feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: currentSessionId,
        assistant_message_id: currentAssistantMessageId,
        rating,
        comment: null,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "反馈提交失败");
    }

    feedbackStatus.textContent =
      rating === "helpful" ? "反馈已记录：这条回复对你有帮助。" : "反馈已记录：后续可继续把建议做得更具体。";
  } catch (error) {
    feedbackStatus.textContent = `反馈提交失败：${String(error)}`;
  } finally {
    setFeedbackState(true, feedbackStatus.textContent);
  }
}

document.querySelectorAll(".suggestion-chip").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.message || "";
    messageInput.focus();
  });
});

modelTargetInput.addEventListener("change", updateModelHelper);
responseStyleInput.addEventListener("change", updateStyleHelper);
compatibilityButton.addEventListener("click", loadCompatibility);
resetSessionButton.addEventListener("click", () => {
  rememberSession("");
  currentAssistantMessageId = null;
  resetChatPanels();
  statusBadge.textContent = "已重置";
});
feedbackHelpfulButton.addEventListener("click", () => submitFeedback("helpful"));
feedbackNeedsMoreButton.addEventListener("click", () => submitFeedback("needs_more"));

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (previewMode) {
    statusBadge.textContent = "预览态";
    feedbackStatus.textContent = "预览态不真正发请求；本地启动后可体验真实接口。";
    return;
  }

  const message = messageInput.value.trim();
  const systemHint = hintInput.value.trim();
  const modelTarget = modelTargetInput.value;
  const responseStyle = responseStyleInput.value;

  if (!message) {
    return;
  }

  submitButton.disabled = true;
  statusBadge.textContent = "生成中";
  responseText.textContent = "正在生成回复，请稍等...";
  responseMeta.textContent = "";
  setFeedbackState(false, "等待本轮回复返回后再提交反馈。");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        system_hint: systemHint || null,
        model_target: modelTarget || "configured",
        response_style: responseStyle || "balanced",
        session_id: currentSessionId || null,
      }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "请求失败");
    }

    currentAssistantMessageId = payload.assistant_message_id;
    rememberSession(payload.session_id);
    providerName.textContent = payload.provider_name;
    modelName.textContent = payload.model_name;
    responseText.textContent = payload.reply;
    responseMeta.textContent = payload.note;
    responseMode.textContent = `${payload.provider_name} / ${payload.model_name} / ${payload.mode}`;
    memoryCountText.textContent = String(payload.memory_messages_used);
    renderKnowledgeHits(payload.knowledge_hits || []);
    setRiskAppearance(payload.safety.level, payload.safety.label);
    setFeedbackState(true, "可以对本条回复提交反馈。");
    statusBadge.textContent = "已完成";
    await loadSessionHistory(payload.session_id, { restoreLatest: false });
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

resetChatPanels();
loadRuntimeMeta();
