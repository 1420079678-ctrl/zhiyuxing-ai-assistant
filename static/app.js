// ZhiYuXing Copilot Enterprise Frontend Controller (v1.0.0)

const form = document.getElementById("chat-form");
const messageInput = document.getElementById("message");
const hintInput = document.getElementById("system_hint");
const submitButton = document.getElementById("submit-button");
const runtimeBadge = document.getElementById("runtime-badge");
const providerName = document.getElementById("provider-name");
const modelName = document.getElementById("model-name");
const baseUrl = document.getElementById("base-url");
const modelTargetInput = document.getElementById("model_target");
const toggleCustomTargetBtn = document.getElementById("toggle-custom-target-btn");
const customModelBar = document.getElementById("custom-model-bar");
const closeCustomModelBarBtn = document.getElementById("close-custom-model-bar-btn");
const customTargetProvider = document.getElementById("custom-target-provider");
const customTargetModel = document.getElementById("custom-target-model");
const customTargetBaseUrl = document.getElementById("custom-target-baseurl");
const customTargetApiKey = document.getElementById("custom-target-apikey");
const customFillOrcarouter = document.getElementById("custom-fill-orcarouter");
const customFillSiliconflow = document.getElementById("custom-fill-siliconflow");
const customFillOllama = document.getElementById("custom-fill-ollama");
const responseStyleInput = document.getElementById("response_style");
const modelHelper = document.getElementById("model-helper");
const styleHelper = document.getElementById("style-helper");
const compatibilityButton = document.getElementById("compatibility-button");
const compatibilitySummary = document.getElementById("compatibility-summary");
const compatibilityList = document.getElementById("compatibility-list");
const resetSessionButton = document.getElementById("reset-session-button");
const newChatBtn = document.getElementById("new-chat-btn");
const feedbackHelpfulButton = document.getElementById("feedback-helpful");
const feedbackNeedsMoreButton = document.getElementById("feedback-needs-more");
const feedbackStatus = document.getElementById("feedback-status");
const sessionIdText = document.getElementById("session-id");
const memoryCountText = document.getElementById("memory-count");
const riskLevelText = document.getElementById("risk-level");
const knowledgeCountText = document.getElementById("knowledge-count");
const knowledgeList = document.getElementById("knowledge-list");
const chatTimeline = document.getElementById("chat-timeline");
const promptChipsContainer = document.getElementById("prompt-chips-container");
const sessionNavList = document.getElementById("session-nav-list");
const scenarioPills = document.getElementById("scenario-pills");
const introBody = document.getElementById("intro-body");

// Knowledge modal elements
const knowledgeModal = document.getElementById("knowledge-modal");
const openKnowledgeModalBtn = document.getElementById("open-knowledge-modal-btn");
const quickAddDocBtn = document.getElementById("quick-add-doc-btn");
const closeKnowledgeModalBtn = document.getElementById("close-knowledge-modal-btn");
const modalDocList = document.getElementById("modal-doc-list");
const uploadDocForm = document.getElementById("upload-doc-form");
const uploadDocStatus = document.getElementById("upload-doc-status");
const sidebarDocCount = document.getElementById("sidebar-doc-count");

// Settings modal elements
const settingsModal = document.getElementById("settings-modal");
const openSettingsModalBtn = document.getElementById("open-settings-modal-btn");
const inspectorSettingsBtn = document.getElementById("inspector-settings-btn");
const closeSettingsModalBtn = document.getElementById("close-settings-modal-btn");
const modelSettingsForm = document.getElementById("model-settings-form");
const settingsProviderInput = document.getElementById("settings-provider-input");
const settingsModelNameInput = document.getElementById("settings-modelname-input");
const settingsBaseUrlInput = document.getElementById("settings-baseurl-input");
const settingsKeyInput = document.getElementById("settings-key-input");
const toggleKeyVisibilityBtn = document.getElementById("toggle-key-visibility-btn");
const settingsTemperatureInput = document.getElementById("settings-temperature-input");
const settingsDemoModeCheckbox = document.getElementById("settings-demo-mode-checkbox");
const settingsProbeBtn = document.getElementById("settings-probe-btn");
const settingsResetDemoBtn = document.getElementById("settings-reset-demo-btn");
const settingsStatusBanner = document.getElementById("settings-status-banner");

const SESSION_STORAGE_KEY = "zhiyuxing_demo_session_id";
const SCENARIO_STORAGE_KEY = "zhiyuxing_active_scenario";

let runtimeMeta = null;
let currentSessionId = window.localStorage.getItem(SESSION_STORAGE_KEY) || "";
let activeScenario = window.localStorage.getItem(SCENARIO_STORAGE_KEY) || "campus";
let currentAssistantMessageId = null;

const SCENARIO_PROMPTS = {
  campus: [
    { label: "学业压力", text: "这周复习任务很多，越想越焦虑，完全不敢开始。" },
    { label: "拖延内耗", text: "我最近总拖延，明明知道该学，但一打开书就很烦躁。" },
    { label: "面试焦虑", text: "我马上要答辩和面试了，越准备越慌，感觉自己不够好。" },
    { label: "失眠疲惫", text: "最近连续失眠好几天了，整天没精神，特别疲惫。" },
  ],
  enterprise: [
    { label: "职业倦怠", text: "连续加班身体透支，感觉心累麻木、严重职业倦怠，想设立心理离线边界。" },
    { label: "向上管理与对齐", text: "大方案跨部门对齐口径总有分歧，主管又在催进度，如何向上管理和消除盲区？" },
    { label: "复杂方案破冰", text: "面对复杂的业务交付方案不知道从何下手，如何用微行动拆解破冰？" },
    { label: "工位精力回血", text: "在工位上感到严重的心力消耗与无意义感，如何进行 5 分钟微能量回血？" },
  ],
};

const SCENARIO_INTROS = {
  campus: "您好！我是知愈星高校青年成长伴读教练。聚焦学业压力排解、拖延内耗阻断、考研答辩与求职抗压，为您提供温和、具体、可执行的支持性建议。",
  enterprise: "您好！我是知愈星企业员工关怀 (EAP) 赋能顾问。面向职场人士与企业团队，聚焦职业倦怠(Burnout)修复、高压交付应对、任务切片破冰与沟通对齐。",
};

function setScenario(scenario) {
  activeScenario = scenario;
  window.localStorage.setItem(SCENARIO_STORAGE_KEY, scenario);

  document.querySelectorAll(".scenario-pill, .scenario-btn").forEach((pill) => {
    pill.classList.toggle("active", pill.getAttribute("data-scenario") === scenario);
  });

  if (introBody) {
    introBody.textContent = SCENARIO_INTROS[scenario] || SCENARIO_INTROS.campus;
  }

  renderPromptChips();
}

function renderPromptChips() {
  if (!promptChipsContainer) return;
  promptChipsContainer.innerHTML = "";
  const prompts = SCENARIO_PROMPTS[activeScenario] || SCENARIO_PROMPTS.campus;
  prompts.forEach((item) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "prompt-chip";
    chip.textContent = `${item.label}: ${item.text.slice(0, 16)}...`;
    chip.title = item.text;
    chip.addEventListener("click", () => {
      messageInput.value = item.text;
      messageInput.focus();
    });
    promptChipsContainer.appendChild(chip);
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatMarkdown(text) {
  if (!text) return "";
  let html = escapeHtml(text);
  // Code block
  html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
  // Inline code
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  return html;
}

function appendMessageBubble(role, content, meta = {}) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role === "user" ? "user-bubble" : "assistant-bubble"}`;

  const avatar = document.createElement("div");
  avatar.className = `bubble-avatar ${role === "user" ? "user-avatar" : "assistant-avatar"}`;
  avatar.textContent = role === "user" ? "👤" : "✨";

  const contentDiv = document.createElement("div");
  contentDiv.className = "bubble-content-box bubble-content";

  const header = document.createElement("div");
  header.className = "bubble-top-meta bubble-header";
  const nameStrong = document.createElement("strong");
  nameStrong.className = "sender-name";
  nameStrong.textContent = role === "user" ? "您" : meta.name || "知愈星 AI";
  const timeSpan = document.createElement("span");
  timeSpan.className = "bubble-time";
  timeSpan.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  header.appendChild(nameStrong);
  header.appendChild(timeSpan);

  const body = document.createElement("div");
  body.className = "bubble-body";
  body.innerHTML = formatMarkdown(content);

  contentDiv.appendChild(header);
  contentDiv.appendChild(body);

  if (meta.footerText) {
    const footer = document.createElement("div");
    footer.className = "bubble-meta-footer";
    footer.textContent = meta.footerText;
    contentDiv.appendChild(footer);
  }

  bubble.appendChild(avatar);
  bubble.appendChild(contentDiv);

  chatTimeline.appendChild(bubble);
  chatTimeline.scrollTop = chatTimeline.scrollHeight;

  return { bubble, body, contentDiv };
}

async function loadSessionsList() {
  try {
    const res = await fetch("/api/sessions?limit=25");
    if (!res.ok) return;
    const data = await res.json();
    if (!sessionNavList) return;

    sessionNavList.innerHTML = "";

    // Active session item
    const currentItem = document.createElement("li");
    currentItem.className = `session-nav-item ${!currentSessionId ? "active" : ""}`;
    currentItem.innerHTML = `
      <span class="session-title">✨ 当前新会话</span>
    `;
    currentItem.addEventListener("click", () => {
      startNewChat();
    });
    sessionNavList.appendChild(currentItem);

    data.sessions.forEach((s) => {
      const li = document.createElement("li");
      li.className = `session-nav-item ${currentSessionId === s.session_id ? "active" : ""}`;
      li.innerHTML = `
        <span class="session-title" title="${escapeHtml(s.title)}">${escapeHtml(s.title || s.session_id)}</span>
        <button class="session-del-btn" title="删除会话" type="button">×</button>
      `;

      li.querySelector(".session-title").addEventListener("click", () => {
        switchSession(s.session_id);
      });

      li.querySelector(".session-del-btn").addEventListener("click", async (e) => {
        e.stopPropagation();
        if (confirm(`确定清除该会话吗？`)) {
          await deleteSession(s.session_id);
        }
      });

      sessionNavList.appendChild(li);
    });
  } catch (err) {
    console.error("加载会话列表失败:", err);
  }
}

async function switchSession(sessionId) {
  currentSessionId = sessionId;
  window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  sessionIdText.textContent = sessionId;

  document.querySelectorAll(".session-nav-item").forEach((item) => item.classList.remove("active"));
  loadSessionsList();

  // Load session history
  try {
    const res = await fetch(`/api/session/${encodeURIComponent(sessionId)}`);
    if (!res.ok) return;
    const data = await res.json();

    chatTimeline.innerHTML = "";
    data.messages.forEach((msg) => {
      appendMessageBubble(msg.role, msg.content, {
        name: msg.role === "user" ? "您" : `${msg.provider_name || "知愈星"} · ${msg.model_name || ""}`,
      });
      if (msg.role === "assistant") {
        currentAssistantMessageId = msg.id;
      }
    });

    memoryCountText.textContent = String(data.messages.length);
    feedbackHelpfulButton.disabled = !currentAssistantMessageId;
    feedbackNeedsMoreButton.disabled = !currentAssistantMessageId;
    feedbackStatus.textContent = "已加载历史会话记录。";
  } catch (err) {
    console.error("加载会话历史失败:", err);
  }
}

async function deleteSession(sessionId) {
  try {
    const res = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, { method: "DELETE" });
    if (res.ok) {
      if (currentSessionId === sessionId) {
        startNewChat();
      } else {
        loadSessionsList();
      }
    }
  } catch (err) {
    console.error("删除会话失败:", err);
  }
}

function startNewChat() {
  currentSessionId = "";
  window.localStorage.removeItem(SESSION_STORAGE_KEY);
  currentAssistantMessageId = null;
  sessionIdText.textContent = "新会话（发送后创建）";
  memoryCountText.textContent = "0";
  knowledgeCountText.textContent = "0";
  riskLevelText.textContent = "常规场景";
  riskLevelText.className = "risk-indicator risk-indicator-low";
  knowledgeList.innerHTML = '<li class="empty-hint">发送消息后，系统将自动检索匹配的知识库切片并在此穿透展示。</li>';
  feedbackHelpfulButton.disabled = true;
  feedbackNeedsMoreButton.disabled = true;
  feedbackStatus.textContent = "反馈功能在生成回复后就绪";

  chatTimeline.innerHTML = `
    <div class="chat-bubble assistant-bubble intro-bubble">
      <div class="bubble-avatar">✨</div>
      <div class="bubble-content">
        <div class="bubble-header">
          <strong>知愈星 AI (ZhiYuXing Copilot)</strong>
          <span class="bubble-time">系统</span>
        </div>
        <div class="bubble-body" id="intro-body">
          ${SCENARIO_INTROS[activeScenario] || SCENARIO_INTROS.campus}
        </div>
      </div>
    </div>
  `;

  loadSessionsList();
  messageInput.focus();
}

function renderKnowledgeHits(hits) {
  knowledgeList.innerHTML = "";
  if (!hits || hits.length === 0) {
    knowledgeList.innerHTML = '<li class="empty-hint">本轮未触发特定知识库切片（基于基础模型常识回答）。</li>';
    return;
  }
  hits.forEach((hit) => {
    const card = document.createElement("li");
    card.className = "knowledge-card";
    card.innerHTML = `
      <div class="knowledge-card-header">
        <span>${escapeHtml(hit.title)}</span>
        <span class="knowledge-card-score">★ ${hit.score}</span>
      </div>
      <div class="knowledge-card-excerpt">${escapeHtml(hit.excerpt)}</div>
    `;
    knowledgeList.appendChild(card);
  });
}

function updateRiskBadge(safety) {
  if (!safety) return;
  riskLevelText.textContent = safety.label || "常规场景";
  riskLevelText.className = `risk-indicator risk-indicator-${safety.level || "low"}`;
}

async function handleSendMessage(e) {
  e.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;

  const hint = hintInput.value.trim();
  let modelTarget = modelTargetInput.value || "configured";
  let customProvider = undefined;
  let customBaseUrl = undefined;
  let customApiKey = undefined;

  if (customModelBar && customModelBar.style.display !== "none") {
    const p = (customTargetProvider.value || "").trim();
    const m = (customTargetModel.value || "").trim();
    const u = (customTargetBaseUrl.value || "").trim();
    const k = (customTargetApiKey.value || "").trim();

    if (m) modelTarget = `custom:${m}`;
    if (p) customProvider = p;
    if (u) customBaseUrl = u;
    if (k) customApiKey = k;
  }
  const responseStyle = responseStyleInput.value || "balanced";

  // 1. Append user message bubble
  appendMessageBubble("user", message);
  messageInput.value = "";
  submitButton.disabled = true;

  // 2. Prepare assistant placeholder bubble
  const { body, contentDiv } = appendMessageBubble("assistant", "", { name: "知愈星 AI" });
  body.innerHTML = '<span class="cursor-blink"></span>';

  let accumulatedText = "";
  let metaReceived = false;

  try {
    const payload = {
      message,
      system_hint: hint || undefined,
      model_target: modelTarget,
      custom_provider: customProvider,
      custom_base_url: customBaseUrl,
      custom_api_key: customApiKey,
      response_style: responseStyle,
      scenario: activeScenario,
      session_id: currentSessionId || undefined,
    };

    const response = await fetch("/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // Keep incomplete chunk

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const eventData = JSON.parse(line.slice(6));

            if (eventData.event === "start") {
              metaReceived = true;
              currentSessionId = eventData.session_id;
              window.localStorage.setItem(SESSION_STORAGE_KEY, currentSessionId);
              sessionIdText.textContent = currentSessionId;
              memoryCountText.textContent = String(eventData.memory_messages_used || 0);
              knowledgeCountText.textContent = String(eventData.knowledge_hits ? eventData.knowledge_hits.length : 0);
              renderKnowledgeHits(eventData.knowledge_hits);
              updateRiskBadge(eventData.safety);
              loadSessionsList();
            } else if (eventData.event === "delta") {
              accumulatedText += eventData.content;
              body.innerHTML = formatMarkdown(accumulatedText) + '<span class="cursor-blink"></span>';
              chatTimeline.scrollTop = chatTimeline.scrollHeight;
            } else if (eventData.event === "done") {
              body.innerHTML = formatMarkdown(eventData.reply || accumulatedText);
              currentAssistantMessageId = eventData.assistant_message_id;
              feedbackHelpfulButton.disabled = !currentAssistantMessageId;
              feedbackNeedsMoreButton.disabled = !currentAssistantMessageId;
              feedbackStatus.textContent = eventData.note || "回复已生成。";

              const footer = document.createElement("div");
              footer.className = "bubble-meta-footer";
              footer.textContent = eventData.note || "";
              contentDiv.appendChild(footer);

              loadSessionsList();
            } else if (eventData.event === "error") {
              body.innerHTML = `<span style="color:var(--risk-high)">${escapeHtml(eventData.message)}</span>`;
            }
          } catch (parseErr) {
            console.warn("SSE parse error:", parseErr);
          }
        }
      }
    }
  } catch (err) {
    console.error("对话调用失败:", err);
    body.innerHTML = `<span style="color:var(--risk-high)">请求异常：${escapeHtml(err.message)}</span>`;
  } finally {
    submitButton.disabled = false;
    messageInput.focus();
  }
}

async function sendFeedback(rating) {
  if (!currentSessionId || !currentAssistantMessageId) return;
  try {
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: currentSessionId,
        assistant_message_id: currentAssistantMessageId,
        rating,
      }),
    });
    if (res.ok) {
      feedbackStatus.textContent = rating === "helpful" ? "感谢支持！我们会继续保持。" : "已记录反馈，后续将更细化拆解步骤。";
      feedbackHelpfulButton.disabled = true;
      feedbackNeedsMoreButton.disabled = true;
    }
  } catch (err) {
    console.error("提交反馈失败:", err);
  }
}

// Knowledge Modal Logic
async function openKnowledgeModal() {
  knowledgeModal.style.display = "flex";
  await refreshDocList();
}

function closeKnowledgeModal() {
  knowledgeModal.style.display = "none";
}

async function refreshDocList() {
  try {
    const res = await fetch("/api/knowledge/documents");
    if (!res.ok) return;
    const data = await res.json();
    modalDocList.innerHTML = "";

    sidebarDocCount.textContent = `当前挂载 ${data.total_documents} 篇政策与干预指南`;

    data.documents.forEach((doc) => {
      const li = document.createElement("li");
      li.className = "doc-item";
      const isCustom = doc.category === "custom";
      li.innerHTML = `
        <div>
          <span class="doc-item-title">${escapeHtml(doc.title)}</span>
          <span class="doc-item-badge ${isCustom ? "doc-item-badge-custom" : ""}">${isCustom ? "自定义" : "内置"}</span>
        </div>
        ${isCustom ? `<button class="text-btn doc-del-btn" style="color:#ef4444;" type="button">删除</button>` : ""}
      `;

      if (isCustom) {
        li.querySelector(".doc-del-btn").addEventListener("click", async () => {
          if (confirm(`确定删除自定义文档 "${doc.title}" 吗？`)) {
            const delRes = await fetch(`/api/knowledge/documents/${encodeURIComponent(doc.document_id)}`, { method: "DELETE" });
            if (delRes.ok) {
              refreshDocList();
            }
          }
        });
      }

      modalDocList.appendChild(li);
    });
  } catch (err) {
    console.error("获取文档列表失败:", err);
  }
}

async function handleUploadDoc(e) {
  e.preventDefault();
  const title = document.getElementById("doc-title-input").value.trim();
  const docId = document.getElementById("doc-id-input").value.trim();
  const content = document.getElementById("doc-content-input").value.trim();

  if (content.length < 20) {
    uploadDocStatus.textContent = "内容长度至少需 20 字符。";
    uploadDocStatus.style.color = "var(--risk-high)";
    return;
  }

  try {
    uploadDocStatus.textContent = "上传写入中...";
    const res = await fetch("/api/knowledge/documents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        document_id: docId || undefined,
        content,
      }),
    });

    if (res.ok) {
      uploadDocStatus.textContent = "文档已成功写入知识库！";
      uploadDocStatus.style.color = "var(--risk-low)";
      uploadDocForm.reset();
      refreshDocList();
    } else {
      const err = await res.json();
      uploadDocStatus.textContent = err.detail || "上传失败";
      uploadDocStatus.style.color = "var(--risk-high)";
    }
  } catch (err) {
    uploadDocStatus.textContent = `上传出错: ${err.message}`;
    uploadDocStatus.style.color = "var(--risk-high)";
  }
}

// Compatibility Check
async function runCompatibilityCheck() {
  compatibilitySummary.textContent = "检测中...";
  compatibilityList.innerHTML = "";
  try {
    const res = await fetch("/api/compatibility");
    if (!res.ok) return;
    const data = await res.json();
    compatibilitySummary.textContent = data.summary;

    data.checks.forEach((check) => {
      const li = document.createElement("li");
      li.className = `compat-item ${check.status === "ok" ? "compat-ok" : "compat-warn"}`;
      li.innerHTML = `
        <strong>${escapeHtml(check.label)}</strong>: ${escapeHtml(check.detail)}
      `;
      compatibilityList.appendChild(li);
    });
  } catch (err) {
    compatibilitySummary.textContent = `检测失败: ${err.message}`;
  }
}

// Settings Modal Logic
const PRESETS = {
  "orcarouter": {
    provider: "OrcaRouter",
    model_name: "deepseek/deepseek-chat",
    base_url: "https://api.orcarouter.com/v1",
    placeholder: "sk-or-...",
  },
  "deepseek-chat": {
    provider: "DeepSeek",
    model_name: "deepseek-chat",
    base_url: "https://api.deepseek.com",
    placeholder: "sk-...",
  },
  "deepseek-r1": {
    provider: "DeepSeek",
    model_name: "deepseek-reasoner",
    base_url: "https://api.deepseek.com",
    placeholder: "sk-...",
  },
  "openai": {
    provider: "OpenAI",
    model_name: "gpt-4o",
    base_url: "https://api.openai.com/v1",
    placeholder: "sk-proj-...",
  },
  "qwen": {
    provider: "Qwen",
    model_name: "qwen-plus",
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    placeholder: "sk-...",
  },
  "moonshot": {
    provider: "Moonshot",
    model_name: "moonshot-v1-8k",
    base_url: "https://api.moonshot.cn/v1",
    placeholder: "sk-...",
  },
  "zhipu": {
    provider: "Zhipu",
    model_name: "glm-4-flash",
    base_url: "https://open.bigmodel.cn/api/paas/v4",
    placeholder: "your-api-key.id",
  },
  "siliconflow": {
    provider: "SiliconFlow",
    model_name: "deepseek-ai/DeepSeek-V3",
    base_url: "https://api.siliconflow.cn/v1",
    placeholder: "sk-...",
  },
  "groq": {
    provider: "Groq",
    model_name: "llama-3.3-70b-versatile",
    base_url: "https://api.groq.com/openai/v1",
    placeholder: "gsk_...",
  },
  "ollama": {
    provider: "Ollama",
    model_name: "qwen2.5:7b",
    base_url: "http://localhost:11434/v1",
    placeholder: "ollama (私有化部署可留空或输入任意值)",
  },
  "custom": {
    provider: "Custom Gateway",
    model_name: "custom-model-id",
    base_url: "https://your-custom-api-domain.com/v1",
    placeholder: "sk-...",
  },
};

function openSettingsModal() {
  if (!settingsModal) return;
  settingsModal.style.display = "flex";
  hideSettingsStatus();

  // Populate form from runtimeMeta if available
  if (runtimeMeta) {
    settingsProviderInput.value = runtimeMeta.provider_name || "DeepSeek";
    settingsModelNameInput.value = runtimeMeta.model_name || "deepseek-chat";
    settingsBaseUrlInput.value = runtimeMeta.base_url || "https://api.deepseek.com";
    settingsDemoModeCheckbox.checked = runtimeMeta.chat_mode === "demo";
  }
}

function closeSettingsModal() {
  if (settingsModal) {
    settingsModal.style.display = "none";
  }
}

function showSettingsStatus(message, isError = false) {
  if (!settingsStatusBanner) return;
  settingsStatusBanner.style.display = "block";
  settingsStatusBanner.textContent = message;
  settingsStatusBanner.className = `settings-status-banner ${isError ? "status-error" : "status-success"}`;
}

function hideSettingsStatus() {
  if (!settingsStatusBanner) return;
  settingsStatusBanner.style.display = "none";
  settingsStatusBanner.textContent = "";
}

function applyPreset(presetKey) {
  const cfg = PRESETS[presetKey];
  if (!cfg) return;
  settingsProviderInput.value = cfg.provider;
  settingsModelNameInput.value = cfg.model_name;
  settingsBaseUrlInput.value = cfg.base_url;
  settingsKeyInput.placeholder = cfg.placeholder;
  settingsDemoModeCheckbox.checked = false;
  showSettingsStatus(`已填入 ${cfg.provider} (${cfg.model_name}) 推荐配置，请输入您的 API Key 后点击测试或保存。`, false);
}

async function handleSettingsProbe() {
  const provider = settingsProviderInput.value.trim();
  const model_name = settingsModelNameInput.value.trim();
  const base_url = settingsBaseUrlInput.value.trim();
  const api_key = settingsKeyInput.value.trim();

  if (!base_url) {
    showSettingsStatus("请先填写有效的 API Base URL。", true);
    return;
  }

  showSettingsStatus("⏳ 正在向远端发起连通性探测 (Probe)... 请稍候", false);
  settingsProbeBtn.disabled = true;

  try {
    const res = await fetch("/api/settings/probe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: provider || undefined,
        model_name: model_name || undefined,
        base_url,
        api_key: api_key || undefined,
      }),
    });

    const data = await res.json();
    if (res.ok && data.status === "ok") {
      showSettingsStatus(`✅ 探测成功！${data.message} 延迟: ${data.latency_ms}ms`, false);
    } else {
      showSettingsStatus(`❌ 探测失败: ${data.message || data.detail || "无法连接到指定服务"}`, true);
    }
  } catch (err) {
    showSettingsStatus(`❌ 网络探测异常: ${err.message}`, true);
  } finally {
    settingsProbeBtn.disabled = false;
  }
}

async function handleSaveSettings(e) {
  e.preventDefault();
  const provider = settingsProviderInput.value.trim();
  const model_name = settingsModelNameInput.value.trim();
  const base_url = settingsBaseUrlInput.value.trim();
  const api_key = settingsKeyInput.value.trim();
  const temperature = parseFloat(settingsTemperatureInput.value) || 0.7;
  const demo_mode = settingsDemoModeCheckbox.checked;

  const saveBtn = document.getElementById("settings-save-btn");
  if (saveBtn) saveBtn.disabled = true;

  try {
    const res = await fetch("/api/settings/model", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider,
        model_name,
        base_url,
        api_key: api_key || undefined,
        temperature,
        demo_mode,
      }),
    });

    if (res.ok) {
      const data = await res.json();
      showSettingsStatus(`✅ 保存成功！当前模式: ${data.mode === "demo" ? "本地演示" : "商业模型已就绪"}`, false);

      // Refresh meta & compatibility
      await refreshMetaAndUI();
      await runCompatibilityCheck();

      setTimeout(() => {
        closeSettingsModal();
      }, 1000);
    } else {
      const err = await res.json();
      showSettingsStatus(`❌ 保存失败: ${err.detail || "请检查输入项"}`, true);
    }
  } catch (err) {
    showSettingsStatus(`❌ 提交失败: ${err.message}`, true);
  } finally {
    if (saveBtn) saveBtn.disabled = false;
  }
}

async function handleResetToDemo() {
  settingsDemoModeCheckbox.checked = true;
  settingsKeyInput.value = "";
  showSettingsStatus("已切换为演示模式开关。点击'保存并应用生效'即时切回本地离线模式。", false);
}

async function refreshMetaAndUI() {
  try {
    const res = await fetch("/api/meta");
    if (res.ok) {
      runtimeMeta = await res.json();
      providerName.textContent = runtimeMeta.provider_name || "-";
      modelName.textContent = runtimeMeta.model_name || "-";
      baseUrl.textContent = runtimeMeta.base_url || "-";
      runtimeBadge.textContent = runtimeMeta.chat_mode === "demo" ? "本地演示模式 (无需Key)" : "模型服务已就绪";

      // Populate models
      modelTargetInput.innerHTML = "";
      runtimeMeta.available_models.forEach((m) => {
        const opt = document.createElement("option");
        opt.value = m.id;
        opt.textContent = `${m.label}${m.available ? "" : " (需配置Key)"}`;
        modelTargetInput.appendChild(opt);
      });

      // Populate styles
      responseStyleInput.innerHTML = "";
      runtimeMeta.available_styles.forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = s.label;
        responseStyleInput.appendChild(opt);
      });

      if (runtimeMeta.knowledge_document_count) {
        sidebarDocCount.textContent = `当前挂载 ${runtimeMeta.knowledge_document_count} 篇政策与干预指南`;
      }
    }
  } catch (err) {
    console.warn("刷新元信息失败:", err);
  }
}

// Bootstrapping
async function init() {
  // 1. Setup scenario
  setScenario(activeScenario);
  document.querySelectorAll(".scenario-pill, .scenario-btn").forEach((pill) => {
    pill.addEventListener("click", () => {
      setScenario(pill.getAttribute("data-scenario"));
    });
  });

  // 2. Fetch meta
  await refreshMetaAndUI();

  // 3. Load initial sessions
  if (currentSessionId) {
    switchSession(currentSessionId);
  } else {
    startNewChat();
  }

  // 4. Bind event listeners
  form.addEventListener("submit", handleSendMessage);
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  if (toggleCustomTargetBtn && customModelBar) {
    toggleCustomTargetBtn.addEventListener("click", () => {
      const isVisible = customModelBar.style.display !== "none";
      customModelBar.style.display = isVisible ? "none" : "block";
      toggleCustomTargetBtn.classList.toggle("active", !isVisible);
      if (!isVisible && customTargetProvider) {
        customTargetProvider.focus();
      }
    });
  }

  if (closeCustomModelBarBtn && customModelBar) {
    closeCustomModelBarBtn.addEventListener("click", () => {
      customModelBar.style.display = "none";
      if (toggleCustomTargetBtn) toggleCustomTargetBtn.classList.remove("active");
    });
  }

  if (customFillOrcarouter) {
    customFillOrcarouter.addEventListener("click", () => {
      if (customTargetProvider) customTargetProvider.value = "OrcaRouter";
      if (customTargetModel) customTargetModel.value = "deepseek/deepseek-chat";
      if (customTargetBaseUrl) customTargetBaseUrl.value = "https://api.orcarouter.com/v1";
      if (customTargetApiKey) customTargetApiKey.placeholder = "sk-or-...";
    });
  }

  if (customFillSiliconflow) {
    customFillSiliconflow.addEventListener("click", () => {
      if (customTargetProvider) customTargetProvider.value = "SiliconFlow";
      if (customTargetModel) customTargetModel.value = "deepseek-ai/DeepSeek-V3";
      if (customTargetBaseUrl) customTargetBaseUrl.value = "https://api.siliconflow.cn/v1";
      if (customTargetApiKey) customTargetApiKey.placeholder = "sk-...";
    });
  }

  if (customFillOllama) {
    customFillOllama.addEventListener("click", () => {
      if (customTargetProvider) customTargetProvider.value = "Ollama";
      if (customTargetModel) customTargetModel.value = "qwen2.5:7b";
      if (customTargetBaseUrl) customTargetBaseUrl.value = "http://localhost:11434/v1";
      if (customTargetApiKey) customTargetApiKey.value = "ollama";
    });
  }

  resetSessionButton.addEventListener("click", startNewChat);
  newChatBtn.addEventListener("click", startNewChat);

  feedbackHelpfulButton.addEventListener("click", () => sendFeedback("helpful"));
  feedbackNeedsMoreButton.addEventListener("click", () => sendFeedback("needs_more"));

  compatibilityButton.addEventListener("click", runCompatibilityCheck);

  openKnowledgeModalBtn.addEventListener("click", openKnowledgeModal);
  quickAddDocBtn.addEventListener("click", openKnowledgeModal);
  closeKnowledgeModalBtn.addEventListener("click", closeKnowledgeModal);
  uploadDocForm.addEventListener("submit", handleUploadDoc);

  // Settings modal event listeners
  if (openSettingsModalBtn) openSettingsModalBtn.addEventListener("click", openSettingsModal);
  if (inspectorSettingsBtn) inspectorSettingsBtn.addEventListener("click", openSettingsModal);
  if (closeSettingsModalBtn) closeSettingsModalBtn.addEventListener("click", closeSettingsModal);
  if (modelSettingsForm) modelSettingsForm.addEventListener("submit", handleSaveSettings);
  if (settingsProbeBtn) settingsProbeBtn.addEventListener("click", handleSettingsProbe);
  if (settingsResetDemoBtn) settingsResetDemoBtn.addEventListener("click", handleResetToDemo);

  if (toggleKeyVisibilityBtn && settingsKeyInput) {
    toggleKeyVisibilityBtn.addEventListener("click", () => {
      if (settingsKeyInput.type === "password") {
        settingsKeyInput.type = "text";
        toggleKeyVisibilityBtn.textContent = "🔒 隐藏";
      } else {
        settingsKeyInput.type = "password";
        toggleKeyVisibilityBtn.textContent = "👁️ 显示";
      }
    });
  }

  // Preset buttons
  document.querySelectorAll(".preset-pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      const preset = btn.getAttribute("data-preset");
      applyPreset(preset);
    });
  });

  // Initial compatibility run
  runCompatibilityCheck();
}

window.addEventListener("DOMContentLoaded", init);

