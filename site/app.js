const form = document.getElementById("chat-form");
const messageInput = document.getElementById("message");
const responseText = document.getElementById("response-text");
const responseMeta = document.getElementById("response-meta");
const responseMode = document.getElementById("response-mode");
const responseStyleInput = document.getElementById("response_style");
const statusBadge = document.getElementById("status-badge");

const STYLE_OPENERS = {
  balanced: "I can hear that the pressure is piling up, so the goal right now is not perfection but getting back a little control.",
  warm: "It makes sense that this feels heavy right now. You do not have to fix everything at once.",
  structured: "A clearer sequence usually helps here: steady yourself first, shrink the task second, then decide the next move.",
  encouraging: "This looks more like overload than inability. You can get traction again by starting very small.",
  brief: "The issue is probably the size of the mental load, not a lack of effort.",
};

function detectTopic(message) {
  const text = message.toLowerCase();
  if (/interview|resume|offer|job|intern/.test(text)) return "interview";
  if (/exam|final|study|review|thesis|defense/.test(text)) return "exam";
  if (/sleep|insomnia|tired|exhausted/.test(text)) return "sleep";
  if (/future|direction|career|confused|path/.test(text)) return "future";
  if (/procrastinat|cannot start|can't start|stuck|delay/.test(text)) return "procrastination";
  if (/stress|anxious|anxiety|panic|pressure/.test(text)) return "pressure";
  return "general";
}

function topicSteps(topic) {
  const map = {
    interview: [
      "Reduce preparation to the 3 questions you are most likely to get, instead of trying to prepare for everything at once.",
      "Write only 3 keywords for each answer first so you do not lock yourself into overly rigid scripts.",
      "Do one short mock answer out loud and check whether the problem is content, structure, or pace.",
    ],
    exam: [
      "Shrink the current goal to one review block, such as one chapter, one problem set, or three concepts.",
      "Replace 'I need to finish everything' with 'I need to complete one useful block today.'",
      "After that block, write down the two points that still feel unclear and let those define the next round.",
    ],
    sleep: [
      "Treat rest as part of the solution, not as something you must earn after being productive.",
      "Keep only one essential task for today and explicitly allow the rest to move later.",
      "If sleep or exhaustion has been ongoing, consider reaching out for offline support instead of trying to carry it alone.",
    ],
    future: [
      "Do not force a full future decision right now; choose one direction worth exploring over the next few weeks.",
      "Turn 'What should I do with my future?' into smaller questions such as what attracts you, what worries you, and what information is missing.",
      "Take one low-cost exploration step, like reading a role description or talking to someone slightly ahead of you.",
    ],
    procrastination: [
      "Lower the entry cost by making the first step tiny, such as opening the file, writing a title, or outlining 3 bullets.",
      "Set a 10 to 15 minute starting block instead of demanding a full productive session from yourself.",
      "Mark that first block as completed so your brain gets evidence that you already started.",
    ],
    pressure: [
      "Choose the easiest meaningful task you can start within 15 minutes.",
      "Write down the one worry that keeps looping, then pair it with one action you can finish today.",
      "Pause briefly after the first step and decide calmly whether to continue instead of forcing a full recovery at once.",
    ],
    general: [
      "Name the most concrete part of the problem so it stops feeling like one large fog.",
      "Pick one action small enough to finish today, even if it only moves the situation a little.",
      "After that, reassess the next best step instead of trying to solve the whole problem immediately.",
    ],
  };
  return map[topic];
}

function topicClosing(topic) {
  const map = {
    interview: "If you want, you can keep going by typing the interview question you fear most and use this demo as a rehearsal starting point.",
    exam: "Exams usually become more manageable once the task is broken into blocks instead of carried as one giant total.",
    sleep: "If this state is affecting your basic functioning for days, offline support would matter more than pushing harder.",
    future: "Direction often becomes clearer through experiments and feedback, not by forcing a final answer in one sitting.",
    procrastination: "A small start is still real progress. The point is to lower the barrier enough that momentum can return.",
    pressure: "You do not need to become fully efficient today. You only need one grounded step to interrupt the spiral.",
    general: "If this were a real support session, the next move would be to narrow the situation a little further and continue from there.",
  };
  return map[topic];
}

function buildReply(message, style) {
  const topic = detectTopic(message);
  const opening = STYLE_OPENERS[style] || STYLE_OPENERS.balanced;
  const steps = topicSteps(topic);
  const closing = topicClosing(topic);
  const label =
    style === "brief"
      ? "Start with these 3 actions:"
      : style === "structured"
        ? "Try this 3-step sequence:"
        : "You can try these 3 steps:";

  return `${opening}\n\n${label}\n1. ${steps[0]}\n2. ${steps[1]}\n3. ${steps[2]}\n\n${closing}`;
}

document.querySelectorAll(".suggestion-chip").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.message || "";
    messageInput.focus();
  });
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  const style = responseStyleInput.value;

  if (!message) {
    return;
  }

  statusBadge.textContent = "Generating";
  responseText.textContent = buildReply(message, style);
  responseMeta.textContent =
    "This public site uses browser-side demo logic so the experience stays online without API keys. The repository itself still supports FastAPI backend mode and real provider integration.";
  responseMode.textContent = `Demo style: ${style}`;
  statusBadge.textContent = "Done";
});
