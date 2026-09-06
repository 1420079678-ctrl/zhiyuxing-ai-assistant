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
const heroWorkspace = document.getElementById("hero-workspace");
const heroScenarioText = document.getElementById("hero-scenario-text");

// Layout controls
const workspaceGrid = document.getElementById("workspace-grid");
const toggleSidebarBtn = document.getElementById("toggle-sidebar-btn");
const toggleInspectorBtn = document.getElementById("toggle-inspector-btn");
const closeInspectorBtn = document.getElementById("close-inspector-btn");
const themeToggleBtn = document.getElementById("theme-toggle-btn");
const themeIcon = document.getElementById("theme-icon");
const themeText = document.getElementById("theme-text");
const THEME_STORAGE_KEY = "zhiyuxing_app_theme";

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

// Mental Skills Codex elements & state
const openSkillsCodexNavBtn = document.getElementById("open-skills-codex-nav-btn");
const openSkillsCodexBtn = document.getElementById("open-skills-codex-btn");
const closeSkillsCodexBtn = document.getElementById("close-skills-codex-btn");
const closeSkillsCodexFooterBtn = document.getElementById("close-skills-codex-footer-btn");
const skillsCodexModal = document.getElementById("skills-codex-modal");
const codexSkillsGrid = document.getElementById("codex-skills-grid");
const activeSkillCapsule = document.getElementById("active-skill-capsule");
const activeSkillNameEl = document.getElementById("active-skill-name");
const activeSkillTagEl = document.getElementById("active-skill-tag");
const clearActiveSkillBtn = document.getElementById("clear-active-skill-btn");

let activeSkillId = null;
let activeSkillName = null;
let activeSkillTag = null;
let availableSkillsCatalog = [];

const SESSION_STORAGE_KEY = "zhiyuxing_demo_session_id";
const SCENARIO_STORAGE_KEY = "zhiyuxing_active_scenario";

let runtimeMeta = null;
let currentSessionId = window.localStorage.getItem(SESSION_STORAGE_KEY) || "";
let activeScenario = window.localStorage.getItem(SCENARIO_STORAGE_KEY) || "campus";
let currentAssistantMessageId = null;

const SCENARIO_PROMPTS = {
  campus: [
    {
      label: "拖延阻断 · 瑞士奶酪法",
      text: "我最近总拖延，明明知道该学，但一打开书就很烦躁，如何用 3 分钟微步切片破冰？",
      tag: "行动破冰",
      method: "降低行动启动阻力 · 3分钟极小化切片"
    },
    {
      label: "认知重塑 · 学业抗压",
      text: "这周复习任务非常繁重，越想越焦虑完全不敢开始，帮我梳理优先级与精力分配。",
      tag: "焦虑卸载",
      method: "建立确定性控制感 · 漏斗式任务排期"
    },
    {
      label: "心理着陆 · 面试答辩",
      text: "我马上要答辩和面试了，越准备越慌乱，感觉自己不够好，如何做心理着陆与脱敏预演？",
      tag: "脱敏应对",
      method: "结构化心理暴露 · 行为预演支撑"
    },
    {
      label: "精力降噪 · 改善失眠",
      text: "最近连续失眠好几天了，整天没精神，思维反刍严重，带我做一次睡前能量降载。",
      tag: "身心平复",
      method: "4-7-8 呼吸节律 · 睡前大脑思维降噪"
    },
  ],
  enterprise: [
    {
      label: "能量盘点 · 职业倦怠",
      text: "连续高压加班身体透支，感觉心累麻木、严重职业倦怠，帮我做一次精力电量盘点与离线防护。",
      tag: "倦怠修复",
      method: "马斯拉奇量表三维度 · 建立离线心理隔离舱"
    },
    {
      label: "向上管理 · 期望对齐",
      text: "重大业务交付跨部门口径总有分歧，主管又在催进度，如何向上管理和消除协作盲区？",
      tag: "对齐沟通",
      method: "三明治对齐模型 · 明确交付预期与底线"
    },
    {
      label: "复杂任务 · 微步破冰",
      text: "面对千头万绪的复杂交付方案不知道从何下手，如何用微行动拆解消除决策瘫痪？",
      tag: "破冰行动",
      method: "第一米微行动切片 · 阻断拖延内耗"
    },
    {
      label: "工位急救 · 5分钟回血",
      text: "在工位上感到严重的心力消耗与无意义感，如何进行 5 分钟微能量回血与情绪着陆？",
      tag: "情绪急救",
      method: "五感着陆法 · 阻断皮质醇过度分泌"
    },
  ],
};

const SCENARIO_INTROS = {
  campus: "您好！我是知愈星高校青年成长伴读教练。聚焦学业压力排解、拖延内耗阻断、考研答辩与求职抗压，为您提供温和、具体、可执行的支持性建议。",
  enterprise: "您好！我是知愈星企业员工关怀 (EAP) 赋能顾问。面向职场人士与企业团队，聚焦职业倦怠(Burnout)修复、高压交付应对、任务切片破冰与沟通对齐。",
};

function autoResizeTextarea(el) {
  if (!el) return;
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 200) + "px";
}

function setScenario(scenario) {
  activeScenario = scenario;
  window.localStorage.setItem(SCENARIO_STORAGE_KEY, scenario);

  document.querySelectorAll(".scenario-pill, .scenario-btn").forEach((pill) => {
    pill.classList.toggle("active", pill.getAttribute("data-scenario") === scenario);
  });

  if (heroScenarioText) {
    heroScenarioText.textContent = scenario === "enterprise"
      ? "企业员工 EAP 关怀 · 职场能量枢纽"
      : "高校青年成长 · CBT 认知赋能引擎";
  }

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
    const card = document.createElement("button");
    card.type = "button";
    card.className = "hero-prompt-card";
    card.innerHTML = `
      <div class="card-head">
        <span class="card-tag">${escapeHtml(item.tag)}</span>
        <span class="card-arrow">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </span>
      </div>
      <div class="card-title">${escapeHtml(item.label)}</div>
      <p class="card-text">${escapeHtml(item.text)}</p>
      <div class="card-footer-hint">${escapeHtml(item.method)}</div>
    `;
    card.addEventListener("click", () => {
      messageInput.value = item.text;
      autoResizeTextarea(messageInput);
      messageInput.focus();
    });
    promptChipsContainer.appendChild(card);
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

  // 1. Code block with language tag & copy button
  html = html.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (_match, lang, code) => {
    return `<div class="code-block-wrapper"><div class="code-block-header"><span>${lang || "code"}</span></div><pre><code>${code.trim()}</code></pre></div>`;
  });
  html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");

  // 2. Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

  // 3. Bold & Italic
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");

  // 4. Headings
  html = html.replace(/^#### (.*$)/gim, '<h4 class="editorial-h4">$1</h4>');
  html = html.replace(/^### (.*$)/gim, '<h3 class="editorial-h3">$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2 class="editorial-h2">$1</h2>');

  // 5. Blockquotes (escapeHtml turned > into &gt;)
  html = html.replace(/^&gt; (.*$)/gim, '<blockquote class="editorial-blockquote">$1</blockquote>');

  // 6. Milestone Stage headers
  html = html.replace(/【(第[一二三四五]阶段[：:].*?)】/g, '<span class="editorial-stage-pill">$1</span>');

  // 7. Lists
  html = html.replace(/^[•\-\*] (.*$)/gim, '<li class="editorial-list-item">$1</li>');
  html = html.replace(/^(\d+)\. (.*$)/gim, '<li class="editorial-list-item-num" data-num="$1">$2</li>');

  // Wrap consecutive list items
  html = html.replace(/(<li class="editorial-list-item">[\s\S]*?<\/li>)/g, '<ul class="editorial-ul">$1</ul>');
  html = html.replace(/<\/ul>\s*<ul class="editorial-ul">/g, "");

  html = html.replace(/(<li class="editorial-list-item-num"[^>]*>[\s\S]*?<\/li>)/g, '<ol class="editorial-ol">$1</ol>');
  html = html.replace(/<\/ol>\s*<ol class="editorial-ol">/g, "");

  // 8. Paragraphs
  const paragraphs = html.split(/\n\n+/);
  html = paragraphs
    .map((p) => {
      p = p.trim();
      if (!p) return "";
      if (
        p.startsWith("<h") ||
        p.startsWith("<blockquote") ||
        p.startsWith("<ul") ||
        p.startsWith("<ol") ||
        p.startsWith("<div class=\"code-block") ||
        p.startsWith("<pre")
      ) {
        return p;
      }
      return `<p class="editorial-paragraph">${p.replace(/\n/g, "<br>")}</p>`;
    })
    .join("\n");

  return html;
}

function appendMessageBubble(role, content, meta = {}) {
  if (heroWorkspace) heroWorkspace.style.display = "none";
  if (chatTimeline) chatTimeline.style.display = "flex";

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role === "user" ? "user-bubble" : "assistant-bubble editorial-card"}`;

  const avatar = document.createElement("div");
  avatar.className = `bubble-avatar ${role === "user" ? "user-avatar" : "assistant-avatar"}`;
  avatar.innerHTML = role === "user"
    ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`
    : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
         <defs>
           <linearGradient id="bubble-star-grad-${Date.now()}" x1="0%" y1="0%" x2="100%" y2="100%">
             <stop offset="0%" stop-color="#3b82f6" />
             <stop offset="100%" stop-color="#6366f1" />
           </linearGradient>
         </defs>
         <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" fill="url(#bubble-star-grad-${Date.now()})"/>
         <circle cx="12" cy="12" r="2.2" fill="#ffffff"/>
       </svg>`;

  const contentDiv = document.createElement("div");
  contentDiv.className = "bubble-content-box bubble-content";

  const header = document.createElement("div");
  header.className = "bubble-top-meta bubble-header";

  const headerLeft = document.createElement("div");
  headerLeft.className = "bubble-header-left";

  const nameStrong = document.createElement("strong");
  nameStrong.className = "sender-name";
  nameStrong.textContent = role === "user" ? "您" : meta.name || "知愈星 Copilot";
  headerLeft.appendChild(nameStrong);

  let skillBadgeEl = null;
  function updateSkillBadge(sName) {
    if (!sName) return;
    if (!skillBadgeEl) {
      skillBadgeEl = document.createElement("span");
      skillBadgeEl.className = "bubble-skill-badge";
      headerLeft.appendChild(skillBadgeEl);
    }
    skillBadgeEl.innerHTML = `<span class="sparkle">✦</span> <span>${escapeHtml(sName)}</span>`;
  }

  if (meta.skill_name) {
    updateSkillBadge(meta.skill_name);
  }

  const headerRight = document.createElement("div");
  headerRight.className = "bubble-header-right";

  const timeSpan = document.createElement("span");
  timeSpan.className = "bubble-time";
  timeSpan.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  headerRight.appendChild(timeSpan);

  header.appendChild(headerLeft);
  header.appendChild(headerRight);

  const body = document.createElement("div");
  body.className = "bubble-body";
  body.innerHTML = formatMarkdown(content);

  contentDiv.appendChild(header);
  contentDiv.appendChild(body);

  let ribbon = null;
  if (role === "assistant") {
    ribbon = document.createElement("div");
    ribbon.className = "bubble-action-ribbon";

    // 1. Copy
    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "ribbon-btn";
    copyBtn.title = "复制回复正文";
    copyBtn.innerHTML = `
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
      <span>复制</span>
    `;
    copyBtn.addEventListener("click", () => {
      const textToCopy = body.innerText || content;
      navigator.clipboard.writeText(textToCopy).then(() => {
        copyBtn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg><span style="color:#10b981">已复制</span>`;
        setTimeout(() => {
          copyBtn.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
            <span>复制</span>
          `;
        }, 2000);
      });
    });

    // 2. Helpful
    const thumbUpBtn = document.createElement("button");
    thumbUpBtn.type = "button";
    thumbUpBtn.className = "ribbon-btn";
    thumbUpBtn.title = "采纳并认同此方案";
    thumbUpBtn.innerHTML = `
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h3"/><path d="M12 2a2 2 0 0 1 2 2v1.88"/></svg>
      <span>有启发</span>
    `;
    thumbUpBtn.addEventListener("click", () => {
      sendFeedback("helpful");
      thumbUpBtn.classList.add("ribbon-btn-active");
      thumbUpBtn.disabled = true;
    });

    // 3. Needs more
    const needsMoreBtn = document.createElement("button");
    needsMoreBtn.type = "button";
    needsMoreBtn.className = "ribbon-btn";
    needsMoreBtn.title = "需要进一步细化或补充";
    needsMoreBtn.innerHTML = `
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-3"/><path d="M12 22a2 2 0 0 1-2-2v-1.88"/></svg>
      <span>需更具体</span>
    `;
    needsMoreBtn.addEventListener("click", () => {
      sendFeedback("needs_more");
      needsMoreBtn.classList.add("ribbon-btn-active");
      needsMoreBtn.disabled = true;
    });

    // 4. Bookmark
    const bookmarkBtn = document.createElement("button");
    bookmarkBtn.type = "button";
    bookmarkBtn.className = "ribbon-btn";
    bookmarkBtn.title = "收藏此观点";
    bookmarkBtn.innerHTML = `
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>
      <span>收藏观点</span>
    `;
    bookmarkBtn.addEventListener("click", () => {
      bookmarkBtn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="#6366f1" stroke="#6366f1" stroke-width="2"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg><span style="color:#6366f1">已收录</span>`;
      setTimeout(() => {
        bookmarkBtn.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>
          <span>收藏观点</span>
        `;
      }, 2500);
    });

    ribbon.appendChild(copyBtn);
    ribbon.appendChild(thumbUpBtn);
    ribbon.appendChild(needsMoreBtn);
    ribbon.appendChild(bookmarkBtn);
    contentDiv.appendChild(ribbon);
  }

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

  return { bubble, body, contentDiv, updateSkillBadge, ribbon };
}

// ===================================================================
// Mental Skills Codex Protocol Engine UI Controllers
// ===================================================================

async function loadSkillsCatalog() {
  try {
    const res = await fetch("/api/skills");
    if (res.ok) {
      availableSkillsCatalog = await res.json();
      renderCodexGrid();
    }
  } catch (err) {
    console.warn("加载心理技能失败:", err);
  }
}

function renderCodexGrid() {
  if (!codexSkillsGrid || !availableSkillsCatalog.length) return;
  codexSkillsGrid.innerHTML = "";

  availableSkillsCatalog.forEach((skill) => {
    const isCurActive = activeSkillId === skill.id;
    const card = document.createElement("div");
    card.className = `codex-card ${isCurActive ? "codex-card-active" : ""}`;

    const stepsHtml = (skill.protocol_steps || [])
      .map((step) => `<li class="codex-step-item"><span class="step-glyph">✦</span><span>${escapeHtml(step)}</span></li>`)
      .join("");

    card.innerHTML = `
      <div class="codex-card-header">
        <div class="codex-card-top-row">
          <span class="codex-cat-pill">${escapeHtml(skill.category || "认知专精")}</span>
          <span class="codex-tag-pill">${escapeHtml(skill.tag || "临床循证")}</span>
        </div>
        <h3 class="codex-card-title">${escapeHtml(skill.name)}</h3>
        <span class="codex-clinical-base">理论基石：${escapeHtml(skill.clinical_base)}</span>
      </div>
      <p class="codex-card-desc">${escapeHtml(skill.summary)}</p>
      <div class="codex-card-steps">
        <div class="steps-heading">四阶段临床推导架构：</div>
        <ul class="steps-ul">${stepsHtml}</ul>
      </div>
      <div class="codex-card-actions">
        <button type="button" class="btn-codex-activate ${isCurActive ? "btn-codex-active" : ""}" data-skill-id="${skill.id}">
          ${isCurActive ? "✓ 技能已在当前挂载" : "✦ 挂载此心理技能"}
        </button>
        <button type="button" class="btn-codex-try" data-skill-id="${skill.id}" title="填入此技能典型演练案例">
          演练提示
        </button>
      </div>
    `;

    card.querySelector(".btn-codex-activate").addEventListener("click", () => {
      selectSkill(skill);
      closeSkillsCodex();
    });

    card.querySelector(".btn-codex-try").addEventListener("click", () => {
      selectSkill(skill);
      if (skill.recommended_prompt) {
        messageInput.value = skill.recommended_prompt;
        autoResizeTextarea(messageInput);
      }
      closeSkillsCodex();
      messageInput.focus();
    });

    codexSkillsGrid.appendChild(card);
  });
}

function selectSkill(skill) {
  activeSkillId = skill.id;
  activeSkillName = skill.name;
  activeSkillTag = skill.tag || "心理技能";

  if (activeSkillCapsule) {
    activeSkillCapsule.style.display = "flex";
    if (activeSkillNameEl) activeSkillNameEl.textContent = skill.name;
    if (activeSkillTagEl) activeSkillTagEl.textContent = skill.tag || "心理技能";
  }
  renderCodexGrid();
}

function clearActiveSkill() {
  activeSkillId = null;
  activeSkillName = null;
  activeSkillTag = null;
  if (activeSkillCapsule) {
    activeSkillCapsule.style.display = "none";
  }
  renderCodexGrid();
}

function openSkillsCodex() {
  if (skillsCodexModal) {
    renderCodexGrid();
    skillsCodexModal.style.display = "flex";
  }
}

function closeSkillsCodex() {
  if (skillsCodexModal) {
    skillsCodexModal.style.display = "none";
  }
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
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
      <span class="session-title">当前新会话</span>
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
    if (data.messages && data.messages.length > 0) {
      if (heroWorkspace) heroWorkspace.style.display = "none";
      if (chatTimeline) chatTimeline.style.display = "flex";
      data.messages.forEach((msg) => {
        appendMessageBubble(msg.role, msg.content, {
          name: msg.role === "user" ? "您" : `${msg.provider_name || "知愈星"} · ${msg.model_name || ""}`,
        });
        if (msg.role === "assistant") {
          currentAssistantMessageId = msg.id;
        }
      });
    } else {
      if (heroWorkspace) heroWorkspace.style.display = "flex";
      if (chatTimeline) chatTimeline.style.display = "none";
    }

    memoryCountText.textContent = String(data.messages ? data.messages.length : 0);
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

  if (heroWorkspace) {
    heroWorkspace.style.display = "flex";
  }
  if (chatTimeline) {
    chatTimeline.innerHTML = "";
    chatTimeline.style.display = "none";
  }

  renderPromptChips();
  loadSessionsList();
  messageInput.value = "";
  autoResizeTextarea(messageInput);
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
  const { body, contentDiv, updateSkillBadge } = appendMessageBubble("assistant", "", {
    name: "知愈星 AI",
    skill_name: activeSkillName || undefined,
  });
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
      skill_id: activeSkillId || undefined,
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
              if (eventData.skill_name) {
                updateSkillBadge(eventData.skill_name);
              }
              loadSessionsList();
            } else if (eventData.event === "delta") {
              accumulatedText += eventData.content;
              body.innerHTML = formatMarkdown(accumulatedText) + '<span class="cursor-blink"></span>';
              chatTimeline.scrollTop = chatTimeline.scrollHeight;
            } else if (eventData.event === "done") {
              body.innerHTML = formatMarkdown(eventData.reply || accumulatedText);
              if (eventData.skill_name) {
                updateSkillBadge(eventData.skill_name);
              }
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
        toggleKeyVisibilityBtn.textContent = "隐藏密钥";
      } else {
        settingsKeyInput.type = "password";
        toggleKeyVisibilityBtn.textContent = "显示明文";
      }
    });
  }

  // Auto-resize message textarea on typing
  if (messageInput) {
    messageInput.addEventListener("input", () => autoResizeTextarea(messageInput));
  }

  // Custom target indicator listener
  function updateCustomTargetIndicator() {
    const hasCustom = Boolean(customTargetProvider?.value?.trim() || customTargetBaseUrl?.value?.trim());
    if (toggleCustomTargetBtn) {
      toggleCustomTargetBtn.classList.toggle("has-custom-config", hasCustom);
    }
  }
  customTargetProvider?.addEventListener("input", updateCustomTargetIndicator);
  customTargetBaseUrl?.addEventListener("input", updateCustomTargetIndicator);
  customTargetApiKey?.addEventListener("input", updateCustomTargetIndicator);

  // Preset buttons
  document.querySelectorAll(".preset-pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      const preset = btn.getAttribute("data-preset");
      applyPreset(preset);
    });
  });

  // Layout toggles
  const SIDEBAR_COLLAPSED_KEY = "zhiyuxing_sidebar_collapsed";
  const INSPECTOR_OPEN_KEY = "zhiyuxing_inspector_open";

  if (window.localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === "true") {
    workspaceGrid?.classList.add("sidebar-collapsed");
  }
  // Default inspector open state: check storage, default to false (collapsed) for clean spacious chat
  const inspectorStored = window.localStorage.getItem(INSPECTOR_OPEN_KEY);
  if (inspectorStored === "true") {
    workspaceGrid?.classList.add("inspector-open");
    toggleInspectorBtn?.classList.add("active");
  }

  if (toggleSidebarBtn && workspaceGrid) {
    toggleSidebarBtn.addEventListener("click", () => {
      const isCollapsed = workspaceGrid.classList.toggle("sidebar-collapsed");
      window.localStorage.setItem(SIDEBAR_COLLAPSED_KEY, isCollapsed ? "true" : "false");
    });
  }

  if (toggleInspectorBtn && workspaceGrid) {
    toggleInspectorBtn.addEventListener("click", () => {
      const isOpen = workspaceGrid.classList.toggle("inspector-open");
      toggleInspectorBtn.classList.toggle("active", isOpen);
      window.localStorage.setItem(INSPECTOR_OPEN_KEY, isOpen ? "true" : "false");
    });
  }

  if (closeInspectorBtn && workspaceGrid) {
    closeInspectorBtn.addEventListener("click", () => {
      workspaceGrid.classList.remove("inspector-open");
      toggleInspectorBtn?.classList.remove("active");
      window.localStorage.setItem(INSPECTOR_OPEN_KEY, "false");
    });
  }

  // Theme initialization (defaults to light mode)
  let currentTheme = window.localStorage.getItem(THEME_STORAGE_KEY) || "light";
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
    if (themeIcon) {
      themeIcon.innerHTML = theme === "dark"
        ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>`
        : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>`;
    }
    if (themeText) themeText.textContent = theme === "dark" ? "深色" : "浅色";
  }
  applyTheme(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      currentTheme = currentTheme === "light" ? "dark" : "light";
      applyTheme(currentTheme);
    });
  }

  // Mental Skills Codex event listeners
  if (openSkillsCodexBtn) {
    openSkillsCodexBtn.addEventListener("click", openSkillsCodex);
  }
  if (openSkillsCodexNavBtn) {
    openSkillsCodexNavBtn.addEventListener("click", openSkillsCodex);
  }
  if (closeSkillsCodexBtn) {
    closeSkillsCodexBtn.addEventListener("click", closeSkillsCodex);
  }
  if (closeSkillsCodexFooterBtn) {
    closeSkillsCodexFooterBtn.addEventListener("click", closeSkillsCodex);
  }
  if (clearActiveSkillBtn) {
    clearActiveSkillBtn.addEventListener("click", clearActiveSkill);
  }

  // Close Codex modal on overlay click
  if (skillsCodexModal) {
    skillsCodexModal.addEventListener("click", (e) => {
      if (e.target === skillsCodexModal) {
        closeSkillsCodex();
      }
    });
  }

  // Load Codex skills catalog
  loadSkillsCatalog();

  // Initial compatibility run
  runCompatibilityCheck();
}

window.addEventListener("DOMContentLoaded", init);

