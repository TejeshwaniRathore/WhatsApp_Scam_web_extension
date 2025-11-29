// ================== SAFE CONTEXT MENU CREATION ==================
chrome.runtime.onInstalled.addListener(() => {
  createMenuOnce();
});

chrome.runtime.onStartup.addListener(() => {
  createMenuOnce();
});

function createMenuOnce() {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "scan-msg",
      title: "Scan Message",
      contexts: ["selection"]
    });
  });
}


// ================== MANUAL RIGHT-CLICK SCAN ==================
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "scan-msg") return;

  const text = info.selectionText?.trim();
  if (!text) return;

  try {
    const res = await fetch("http://localhost:8000/classify", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json"
      },
      body: JSON.stringify({ text })
    });

    const data = await res.json();
    const label = data?.classification?.label || "UNKNOWN";

    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (label, text) => {
        // Select all WhatsApp messages reliably
        const allMsgs = document.querySelectorAll(
          "span.selectable-text.copyable-text span"
        );

        for (const msg of allMsgs) {
          if (msg.innerText.trim() === text.trim()) {

            if (msg.parentElement.querySelector(".scam-badge")) return;

            const badge = document.createElement("span");
            badge.className = "scam-badge";

            badge.innerText = label === "SCAM" ? "⚠️ SCAM" : "✅ SAFE";
            badge.style.cssText = `
              display: inline-block;
              padding: 2px 6px;
              margin-left: 6px;
              font-size: 11px;
              font-weight: bold;
              border-radius: 6px;
              background-color: ${label === "SCAM" ? "#ff4d4d" : "#28a745"};
              color: white;
              font-family: Arial, sans-serif;
            `;

            msg.parentElement.appendChild(badge);
            break;
          }
        }
      },
      args: [label, text]
    });

  } catch (err) {
    console.error("Manual scan error:", err);
  }
});
