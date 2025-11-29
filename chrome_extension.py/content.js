console.log("Content Script Loaded");

// ======================================================
// UNIVERSAL WHATSAPP MESSAGE EXTRACTOR FOR YOUR DOM
// ======================================================
function getMessageInnerSpan(node) {
  return node.querySelector(
    "div.copyable-text span._ao3e.selectable-text.copyable-text > span"
  );
}

function extractMessageText(innerSpan) {
  if (!innerSpan) return "";
  return innerSpan.innerText.trim();
}


// ======================================================
// MALICIOUS LINK DETECTION HELPERS
// ======================================================
const URL_REGEX = /https?:\/\/[^\s'"]+/gi;
const APK_REGEX = /\.apk(\?.*)?$/i;
const DISGUISED_APK_REGEX = /\.(jpg|jpeg|png|pdf)\.apk$/i;

const SHORTENERS = ["bit.ly","t.co","tinyurl.com","goo.gl","is.gd","shorturl.at","buff.ly"];
const SUSPICIOUS_TLDS = [".xyz",".top",".club",".click",".info",".cyou"];

function extractUrls(text) {
  return (text.match(URL_REGEX) || []).map(u => u.replace(/[),.]+$/, ""));
}

function scoreLink(url) {
  let score = 0;
  const l = url.toLowerCase();

  if (APK_REGEX.test(l)) score += 3;
  if (DISGUISED_APK_REGEX.test(l)) score += 4;

  try {
    const host = new URL(l).hostname;
    if (SHORTENERS.includes(host)) score += 2;

    if (SUSPICIOUS_TLDS.some(tld => host.endsWith(tld))) score += 1;
  } catch {}

  return score;
}

function injectWarning(node, message) {
  if (node.parentElement.querySelector(".auto-url-warning")) return;

  const div = document.createElement("div");
  div.className = "auto-url-warning";

  div.style.cssText = `
    padding: 6px;
    margin-top: 5px;
    background: rgba(255, 0, 0, 0.15);
    border-left: 4px solid red;
    color: #b30000;
    font-size: 12px;
    border-radius: 4px;
  `;

  div.innerText = message;

  node.parentElement.appendChild(div);
}

// Call LLM only if suspicious
async function classifyViaLLM(text) {
  try {
    const response = await fetch("http://localhost:8000/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ text })
    });

    return await response.json();
  } catch {
    return { classification: { label: "UNKNOWN" }};
  }
}


// ======================================================
// AUTO DETECTION + BADGE INJECTION
// ======================================================
async function autoProcessMessage(innerSpan, text) {

  const urls = extractUrls(text);
  let suspicious = false;

  for (const url of urls) {
    const score = scoreLink(url);

    if (score > 0) {
      suspicious = true;
      injectWarning(innerSpan, `⚠️ Suspicious link detected: ${url}`);
    }
  }

  let label = "SAFE";
  if (suspicious) {
    const result = await classifyViaLLM(text);
    label = result?.classification?.label ?? "SAFE";
  }

  // Badge
  const badge = document.createElement("span");
  badge.style.cssText = `
    padding: 2px 6px;
    margin-left: 6px;
    font-size: 10px;
    font-weight: bold;
    border-radius: 6px;
    background: ${label === "SCAM" ? "red" : "green"};
    color: white;
  `;
  badge.innerText = label;

  innerSpan.parentElement.appendChild(badge);
}


// ======================================================
// MUTATION OBSERVER (100% COMPATIBLE WITH YOUR DOM)
// ======================================================
const observer = new MutationObserver(async (mutations) => {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {

      if (!node.querySelector) continue;

      const msgInner = getMessageInnerSpan(node);
      if (!msgInner) continue;

      const text = extractMessageText(msgInner);
      if (!text) continue;

      console.log("DETECTED MESSAGE:", text);

      await autoProcessMessage(msgInner, text);
    }
  }
});

observer.observe(document.body, { childList: true, subtree: true });

console.log("WhatsApp Auto Malware Scanner ACTIVE");
