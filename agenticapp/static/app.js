const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("composer");
const inputEl = document.getElementById("input");
const sendEl = document.getElementById("send");
const statusEl = document.getElementById("status");
const docTypeEl = document.getElementById("docType");
const themeEl = document.getElementById("theme");
const dimensionEl = document.getElementById("dimension");
const topKEl = document.getElementById("topK");
const topKValueEl = document.getElementById("topKValue");
const historyListEl = document.getElementById("historyList");
const clearHistoryEl = document.getElementById("clearHistory");
const saveCurrentEl = document.getElementById("saveCurrent");
const exportHistoryEl = document.getElementById("exportHistory");
const importHistoryEl = document.getElementById("importHistory");
const importHistoryFileEl = document.getElementById("importHistoryFile");
const historySearchEl = document.getElementById("historySearch");

let busy = false;
let allThemes = [];
const relatedCache = new Map();
let currentChat = null;

const STORAGE_KEY = "logging_rag_saved_chats_v1";
const EMPTY_CHAT = `<div class="empty">
    <h2>Ask about logging practices</h2>
    <p>Answers are grounded in the consolidated guideline catalogue and cite
       the retrieved items by number.</p>
</div>`;

function clearPlaceholder() {
    messagesEl.querySelector(".empty")?.remove();
}

function getSavedChats() {
    try {
        const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

function setSavedChats(chats) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(chats.slice(0, 50)));
}

function pushSavedChat(question, answer, sources) {
    const chats = getSavedChats();
    chats.unshift({
        id: crypto.randomUUID(),
        at: new Date().toISOString(),
        question,
        answer,
        sources,
    });
    setSavedChats(chats);
    renderSavedChats();
}

function saveChat(question, answer, sources) {
    currentChat = { question, answer, sources };
    pushSavedChat(question, answer, sources);
}

function renderSavedChats() {
    const query = (historySearchEl.value || "").trim().toLowerCase();
    const chats = getSavedChats().filter((chat) => {
        if (!query) return true;
        return (chat.question || "").toLowerCase().includes(query)
            || (chat.answer || "").toLowerCase().includes(query);
    });
    historyListEl.innerHTML = "";
    if (!chats.length) {
        const empty = document.createElement("div");
        empty.className = "meta";
        empty.textContent = query ? "No matching saved chats." : "No saved chats yet.";
        historyListEl.appendChild(empty);
        return;
    }

    for (const chat of chats) {
        const row = document.createElement("div");
        row.className = "history-item";

        const openBtn = document.createElement("button");
        openBtn.type = "button";
        openBtn.className = "history-open";
        openBtn.textContent = chat.question;
        openBtn.title = chat.question;
        openBtn.addEventListener("click", () => openSavedChat(chat.id));

        const deleteBtn = document.createElement("button");
        deleteBtn.type = "button";
        deleteBtn.className = "history-delete";
        deleteBtn.textContent = "x";
        deleteBtn.title = "Remove saved chat";
        deleteBtn.addEventListener("click", () => {
            const next = getSavedChats().filter((item) => item.id !== chat.id);
            setSavedChats(next);
            renderSavedChats();
        });

        row.append(openBtn, deleteBtn);
        historyListEl.appendChild(row);
    }
}

function openSavedChat(chatId) {
    const chat = getSavedChats().find((item) => item.id === chatId);
    if (!chat) return;
    messagesEl.innerHTML = "";
    addMessage("user", chat.question);
    const { wrap, body } = addMessage("assistant", "");
    body.innerHTML = renderInline(chat.answer || "");
    if (Array.isArray(chat.sources) && chat.sources.length) {
        renderSources(wrap, chat.sources);
    }
}

function clearConversation() {
    messagesEl.innerHTML = EMPTY_CHAT;
}

function addMessage(role, text) {
    clearPlaceholder();
    const wrap = document.createElement("div");
    wrap.className = `msg ${role}`;
    wrap.innerHTML = `<div class="role">${role === "user" ? "You" : "Assistant"}</div>`;
    const body = document.createElement("div");
    body.className = "body";
    body.textContent = text;
    wrap.appendChild(body);
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return { wrap, body };
}

function extractGuidelineId(hit) {
    return hit.metadata?.consolidated_id || hit.metadata?.example_id || "n/a";
}

function ensureOnlyOnePanel(li, keepClass) {
    [".related", ".source-box"].forEach((selector) => {
        const node = li.querySelector(selector);
        if (node && !node.classList.contains(keepClass)) {
            node.remove();
        }
    });
}

async function fetchRelated(consolidatedId) {
    if (relatedCache.has(consolidatedId)) {
        return relatedCache.get(consolidatedId);
    }
    const response = await fetch(`/related/${encodeURIComponent(consolidatedId)}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch related data (${response.status})`);
    }
    const data = await response.json();
    relatedCache.set(consolidatedId, data);
    return data;
}

function addExamplesToggleIfAvailable(li, consolidatedId) {
    fetchRelated(consolidatedId)
        .then((data) => {
            if (!data.examples?.length || li.querySelector(".examples-box")) {
                return;
            }

            const examplesToggle = document.createElement("details");
            examplesToggle.className = "examples-box";
            const examplesSummary = document.createElement("summary");
            examplesSummary.textContent = "Examples (click to expand)";
            examplesToggle.appendChild(examplesSummary);

            for (const item of data.examples.slice(0, 5)) {
                const row = document.createElement("details");
                const rowSummary = document.createElement("summary");
                rowSummary.textContent = item.example_id || "Example";
                const content = document.createElement("pre");
                content.className = "example-content";
                content.textContent = item.snippet || "(empty example)";
                const sub = document.createElement("div");
                sub.className = "meta";
                sub.textContent = [item.repository, item.source_file].filter(Boolean).join(" / ") || "example metadata";
                row.append(rowSummary, content, sub);
                if (item.url) {
                    const link = document.createElement("a");
                    link.href = item.url;
                    link.textContent = "Open source link";
                    link.target = "_blank";
                    link.rel = "noopener noreferrer";
                    row.appendChild(link);
                }
                examplesToggle.appendChild(row);
            }

            li.appendChild(examplesToggle);
        })
        .catch(() => {
            /* Ignore missing related data for optional examples panel. */
        });
}

function renderSources(wrap, sources) {
    const details = document.createElement("details");
    details.className = "sources";
    const summary = document.createElement("summary");
    summary.textContent = `${sources.length} retrieved items`;
    details.appendChild(summary);

    const list = document.createElement("ol");
    for (const hit of sources) {
        const li = document.createElement("li");
        const id = document.createElement("div");
        id.className = "source-id";
        id.textContent = `Guideline/item number: ${extractGuidelineId(hit)}`;

        const title = document.createElement("div");
        title.textContent = hit.title;

        const meta = document.createElement("div");
        meta.className = "meta";
        const bits = [hit.source, `distance ${hit.distance.toFixed(3)}`, hit.metadata.doc_type || "item"];
        if (hit.metadata.theme) bits.push(hit.metadata.theme);
        meta.textContent = bits.join(" · ");

        const actions = document.createElement("div");
        actions.className = "actions";

        if (hit.metadata.consolidated_id) {
            const relatedBtn = document.createElement("button");
            relatedBtn.type = "button";
            relatedBtn.className = "tiny";
            relatedBtn.textContent = "Related guideline";
            relatedBtn.addEventListener("click", async () => {
                if (li.querySelector(".related")) {
                    li.querySelector(".related").remove();
                    return;
                }
                ensureOnlyOnePanel(li, "related");
                const box = document.createElement("div");
                box.className = "related";
                box.textContent = "Loading related guideline…";
                li.appendChild(box);
                try {
                    const data = await fetchRelated(hit.metadata.consolidated_id);
                    if (!data.guideline) {
                        box.textContent = "No consolidated guideline text found.";
                        return;
                    }
                    const repo = data.guideline_repository || hit.metadata.repositories || "n/a";
                    const sourceFile = data.guideline_source_file || hit.metadata.source_file || "n/a";
                    box.innerHTML = `<strong>Related guideline</strong><br>${data.consolidated_id}: ${data.guideline}<br>Repository: ${repo}`;
                    const linkUrl = data.guideline_url || hit.metadata.url;
                    const sourceLine = document.createElement("div");
                    sourceLine.innerHTML = "Source file: ";
                    if (linkUrl) {
                        const fileLink = document.createElement("a");
                        fileLink.href = linkUrl;
                        fileLink.textContent = sourceFile;
                        fileLink.target = "_blank";
                        fileLink.rel = "noopener noreferrer";
                        sourceLine.appendChild(fileLink);
                    } else {
                        sourceLine.append(sourceFile);
                    }
                    box.appendChild(document.createElement("br"));
                    box.appendChild(sourceLine);
                    if (linkUrl) {
                        const link = document.createElement("a");
                        link.href = linkUrl;
                        link.textContent = "Open related repository source";
                        link.target = "_blank";
                        link.rel = "noopener noreferrer";
                        box.appendChild(document.createElement("br"));
                        box.appendChild(link);
                    } else if (data.references?.length) {
                        const head = document.createElement("div");
                        head.className = "meta";
                        head.textContent = "Multiple related references:";
                        box.appendChild(document.createElement("br"));
                        box.appendChild(head);
                        const refs = document.createElement("ul");
                        refs.className = "refs-list";
                        for (const ref of data.references.slice(0, 5)) {
                            const item = document.createElement("li");
                            const label = [ref.repository, ref.source_file].filter(Boolean).join(" / ") || "reference";
                            if (ref.url) {
                                const a = document.createElement("a");
                                a.href = ref.url;
                                a.textContent = label;
                                a.target = "_blank";
                                a.rel = "noopener noreferrer";
                                item.appendChild(a);
                            } else {
                                item.textContent = label;
                            }
                            refs.appendChild(item);
                        }
                        box.appendChild(refs);
                    } else {
                        const noRef = document.createElement("div");
                        noRef.className = "meta";
                        noRef.textContent = "No direct source file is stored for this consolidated guideline.";
                        box.appendChild(document.createElement("br"));
                        box.appendChild(noRef);
                    }
                } catch {
                    box.textContent = "Failed to load related guideline references.";
                }
            });
            actions.appendChild(relatedBtn);
            addExamplesToggleIfAvailable(li, hit.metadata.consolidated_id);
        }

        const sourceBtn = document.createElement("button");
        sourceBtn.type = "button";
        sourceBtn.className = "tiny";
        sourceBtn.textContent = "Open-source info";
        sourceBtn.addEventListener("click", () => {
            if (li.querySelector(".source-box")) {
                li.querySelector(".source-box").remove();
                return;
            }
            ensureOnlyOnePanel(li, "source-box");
            const box = document.createElement("div");
            box.className = "source-box";
            const repo = hit.metadata.repositories || "n/a";
            const sourceFile = hit.metadata.source_file || "n/a";
            const codeFlag = hit.metadata.code_involved || "n/a";
            box.innerHTML = `<strong>Open-source info</strong><br>Repository: ${repo}<br>Source file: ${sourceFile}<br>Code involved: ${codeFlag}`;
            if (hit.metadata.url) {
                const link = document.createElement("a");
                link.href = hit.metadata.url;
                link.textContent = "Open source link";
                link.target = "_blank";
                link.rel = "noopener noreferrer";
                box.appendChild(document.createElement("br"));
                box.appendChild(link);
            }
            li.appendChild(box);
        });
        actions.appendChild(sourceBtn);

        li.append(id, title, meta, actions);
        list.appendChild(li);
    }
    details.appendChild(list);
    wrap.appendChild(details);
}

// Escapes HTML first, so only our own <code> markup reaches innerHTML.
function renderInline(text) {
    const escaped = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    return escaped.replace(/`([^`]+)`/g, "<code>$1</code>");
}

async function ask(question) {
    if (busy || !question.trim()) return;
    busy = true;
    sendEl.disabled = true;

    addMessage("user", question);
    const { wrap, body } = addMessage("assistant", "");
    body.classList.add("pending");
    body.textContent = "Retrieving and generating… this takes a moment on CPU.";

    const payload = {
        query: question,
        n_results: Number(topKEl.value),
        stream: true,
    };
    if (docTypeEl.value) payload.doc_type = docTypeEl.value;
    if (themeEl.value) payload.theme = themeEl.value;
    if (dimensionEl.value) payload.dimension = dimensionEl.value;

    let answer = "";
    let sources = [];
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const detail = await response.json().catch(() => ({}));
            throw new Error(detail.detail || `Request failed (${response.status})`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });

            const lines = buffer.split("\n");
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.trim()) continue;
                const event = JSON.parse(line);
                if (event.type === "sources") {
                    sources = event.sources || [];
                } else if (event.type === "token") {
                    if (body.classList.contains("pending")) {
                        body.classList.remove("pending");
                        body.textContent = "";
                    }
                    answer += event.text;
                    body.innerHTML = renderInline(answer);
                    messagesEl.scrollTop = messagesEl.scrollHeight;
                }
            }
        }

        if (sources.length) {
            renderSources(wrap, sources);
        }

        if (!answer) {
            body.classList.remove("pending");
            body.textContent = "The model returned an empty answer.";
        } else {
            saveChat(question, answer, sources);
        }
    } catch (error) {
        body.classList.remove("pending");
        body.textContent = `Error: ${error.message}`;
    } finally {
        busy = false;
        sendEl.disabled = false;
        inputEl.focus();
    }
}

formEl.addEventListener("submit", (event) => {
    event.preventDefault();
    const question = inputEl.value;
    inputEl.value = "";
    inputEl.style.height = "auto";
    ask(question);
});

inputEl.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        formEl.requestSubmit();
    }
});

inputEl.addEventListener("input", () => {
    inputEl.style.height = "auto";
    inputEl.style.height = `${inputEl.scrollHeight}px`;
});

topKEl.addEventListener("input", () => {
    topKValueEl.textContent = topKEl.value;
});

function refreshThemeOptions() {
    const selectedDimension = dimensionEl.value;
    const previous = themeEl.value;
    const filtered = selectedDimension
        ? allThemes.filter((entry) => entry.dimension === selectedDimension)
        : allThemes;

    themeEl.innerHTML = "";
    const base = document.createElement("option");
    base.value = "";
    base.textContent = "All themes";
    themeEl.appendChild(base);

    for (const entry of filtered) {
        if (!entry.theme) continue;
        const option = document.createElement("option");
        option.value = entry.theme;
        option.textContent = selectedDimension
            ? entry.theme
            : (entry.dimension ? `${entry.theme} — ${entry.dimension}` : entry.theme);
        themeEl.appendChild(option);
    }

    if ([...themeEl.options].some((opt) => opt.value === previous)) {
        themeEl.value = previous;
    } else {
        themeEl.value = "";
    }
}

dimensionEl.addEventListener("change", refreshThemeOptions);

document.querySelectorAll(".example").forEach((button) => {
    button.addEventListener("click", () => ask(button.textContent));
});

document.getElementById("clear").addEventListener("click", () => {
    clearConversation();
});

clearHistoryEl.addEventListener("click", () => {
    setSavedChats([]);
    renderSavedChats();
});

saveCurrentEl.addEventListener("click", () => {
    if (!currentChat || !currentChat.answer) return;
    pushSavedChat(currentChat.question, currentChat.answer, currentChat.sources || []);
});

historySearchEl.addEventListener("input", renderSavedChats);

exportHistoryEl.addEventListener("click", () => {
    const chats = getSavedChats();
    const blob = new Blob([JSON.stringify(chats, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `saved_chats_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
});

importHistoryEl.addEventListener("click", () => importHistoryFileEl.click());
importHistoryFileEl.addEventListener("change", async () => {
    const file = importHistoryFileEl.files?.[0];
    if (!file) return;
    try {
        const text = await file.text();
        const incoming = JSON.parse(text);
        if (!Array.isArray(incoming)) return;
        const normalized = incoming
            .filter((item) => item && typeof item.question === "string")
            .map((item) => ({
                id: item.id || crypto.randomUUID(),
                at: item.at || new Date().toISOString(),
                question: item.question,
                answer: typeof item.answer === "string" ? item.answer : "",
                sources: Array.isArray(item.sources) ? item.sources : [],
            }));
        setSavedChats([...normalized, ...getSavedChats()]);
        renderSavedChats();
    } catch {
        /* Ignore malformed import file. */
    } finally {
        importHistoryFileEl.value = "";
    }
});

(async function init() {
    try {
        const health = await (await fetch("/health")).json();
        statusEl.textContent = `${health.model}`;
        statusEl.classList.add("ok");
    } catch {
        statusEl.textContent = "API unreachable";
    }
    try {
        const data = await (await fetch("/themes")).json();
        allThemes = data.themes || [];
        refreshThemeOptions();
    } catch {
        /* theme filter stays on "All themes" */
    }
    renderSavedChats();
})();
