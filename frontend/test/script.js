// ---------------------- Topics ---------------------- //
const topics = {
  Backpropagation: {
    summary:
      "Backpropagation is the process of updating weights in a neural network by calculating the gradient of the loss function with respect to each weight using the chain rule.",
    keyPoints: [
      "Used in training neural networks",
      "Calculates gradient via chain rule",
      "Updates weights to minimize loss",
    ],
  },
  "Adam Optimizer": {
    summary:
      "Adam is an adaptive learning rate optimization algorithm that combines RMSProp and momentum. It's widely used for training deep learning models.",
    keyPoints: [
      "Combines momentum and RMSProp",
      "Maintains running averages of gradients",
      "Popular choice in DL frameworks",
    ],
  },
};

// ---------------------- State ---------------------- //
let uploadMode = "file";
let currentSection = null;
let resources = JSON.parse(localStorage.getItem("resources")) || [];

// ---------------------- Upload Mode Toggle ---------------------- //
function toggleUploadMode() {
  const fileInput = document.getElementById("fileInput");
  const linkInput = document.getElementById("linkInput");
  const slider = document.getElementById("onoffSlider");
  const toggle = document.getElementById("onoffToggle");

  if (uploadMode === "file") {
    uploadMode = "link";
    slider.style.left = "46px";
    toggle.classList.remove("file-active");
    toggle.classList.add("link-active");
    fileInput.style.display = "none";
    linkInput.style.display = "block";
  } else {
    uploadMode = "file";
    slider.style.left = "2px";
    toggle.classList.remove("link-active");
    toggle.classList.add("file-active");
    fileInput.style.display = "block";
    linkInput.style.display = "none";
  }
}

// ---------------------- Ingest File/Link ---------------------- //
function ingest() {
  const file = document.getElementById("fileInput").files[0];
  const link = document.getElementById("linkInput").value.trim();

  if (!file && !link) return alert("Please upload a file or paste a link.");

  const newResource = {
    id: Date.now(),
    name: file ? file.name : link,
    type: file ? "file" : "link",
    url: file ? URL.createObjectURL(file) : link,
    tag: "untagged",
    addedAt: new Date().toISOString(),
    lastReviewed: null,
    nextReview: null,
  };

  resources.unshift(newResource);
  saveAndRenderResources();
  alert("Resource added!");
  document.getElementById("fileInput").value = "";
  document.getElementById("linkInput").value = "";
}

// ---------------------- Save Quick Note ---------------------- //
function saveQuickNote() {
  const text = document.getElementById("quickNote").value.trim();
  if (!text) return;

  const newNote = {
    id: Date.now(),
    name: text.split("\n")[0].slice(0, 30) + "...",
    type: "note",
    content: text,
    tag: "quick-note",
    addedAt: new Date().toISOString(),
    lastReviewed: null,
    nextReview: null,
  };

  resources.unshift(newNote);
  saveAndRenderResources();
  document.getElementById("quickNote").value = "";
}

// ---------------------- Render Resource List ---------------------- //
function renderResources() {
  const list = document.getElementById("resourceList");
  const search = document.getElementById("searchInput").value.toLowerCase();
  const tag = document.getElementById("tagFilter").value;

  list.innerHTML = "";
  const filtered = resources.filter((r) => {
    const matchesTag = !tag || r.tag === tag;
    const matchesSearch = r.name.toLowerCase().includes(search);
    return matchesTag && matchesSearch;
  });

  filtered.forEach((res) => {
    const li = document.createElement("li");
    li.innerHTML = `
        <strong>${res.name}</strong> (${res.type})
        <br><small>Tag: ${res.tag} | Added: ${new Date(
      res.addedAt
    ).toLocaleDateString()}</small>
        <br>
        ${
          res.type === "link"
            ? `<a href="${res.url}" target="_blank">Open Link</a><br>`
            : ""
        }
        <button onclick="markReviewed(${res.id})">Mark for Review</button>
      `;
    list.appendChild(li);
  });

  populateTagFilter();
}

// ---------------------- Render Revisions Due ---------------------- //
function renderRevisions() {
  const list = document.getElementById("revisionList");
  list.innerHTML = "";

  const today = new Date().toISOString().split("T")[0];

  resources
    .filter((r) => r.nextReview && r.nextReview <= today)
    .forEach((res) => {
      const li = document.createElement("li");
      li.innerHTML = `
          <strong>${res.name}</strong> - Review Due
          <br><small>Last Reviewed: ${res.lastReviewed || "Never"}</small>
        `;
      list.appendChild(li);
    });
}

// ---------------------- Mark Resource Reviewed ---------------------- //
function markReviewed(id) {
  const now = new Date();
  const next = new Date(now.getTime() + 2 * 24 * 60 * 60 * 1000); // +2 days

  const res = resources.find((r) => r.id === id);
  if (res) {
    res.lastReviewed = now.toISOString().split("T")[0];
    res.nextReview = next.toISOString().split("T")[0];
    saveAndRenderResources();
  }
}

// ---------------------- Save & Render ---------------------- //
function saveAndRenderResources() {
  localStorage.setItem("resources", JSON.stringify(resources));
  renderResources();
  renderRevisions();
}

// ---------------------- Populate Tags ---------------------- //
function populateTagFilter() {
  const dropdown = document.getElementById("tagFilter");
  const uniqueTags = new Set(resources.map((r) => r.tag));

  dropdown.innerHTML = `<option value="">All Tags</option>`;
  uniqueTags.forEach((tag) => {
    const opt = document.createElement("option");
    opt.value = tag;
    opt.innerText = tag;
    dropdown.appendChild(opt);
  });
}

// ---------------------- Topic Summary ---------------------- //
function loadTopic() {
  const selector = document.getElementById("topicSelector");
  const topic = selector.value;
  const data = topics[topic];

  document.getElementById("topicTitle").innerText = topic;
  document.getElementById("topicSummary").innerText = data.summary;
  const keyList = document.getElementById("keyPoints");
  keyList.innerHTML = "";
  data.keyPoints.forEach((point) => {
    const li = document.createElement("li");
    li.innerText = point;
    keyList.appendChild(li);
  });

  showOnly("summary");
}

// ---------------------- Toggle Sections ---------------------- //
function toggleSection(section) {
  const all = ["summarySection", "quizSection", "explainSection"];
  const btnMap = {
    summary: "Summary",
    explain: "Deep Explain",
    quiz: "Quiz",
  };

  document
    .querySelectorAll(".controls-btn")
    .forEach((btn) => btn.classList.remove("active"));

  if (currentSection === section) {
    all.forEach((id) => {
      const el = document.getElementById(id);
      if (el) {
        el.classList.remove("active");
        el.style.maxHeight = "0";
      }
    });
    currentSection = null;
    return;
  }

  document.querySelectorAll(".controls-btn").forEach((btn) => {
    if (btn.textContent.trim() === btnMap[section]) {
      btn.classList.add("active");
    }
  });

  all.forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.classList.remove("active");
      el.style.maxHeight = "0";
    }
  });

  const target = document.getElementById(section + "Section");
  if (target) {
    target.style.maxHeight = target.scrollHeight + "px";
    setTimeout(() => target.classList.add("active"), 700);
  }

  currentSection = section;
}

// ---------------------- Init ---------------------- //
window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("onoffSlider").style.left = "2px";
  document.getElementById("onoffToggle").classList.add("file-active");

  const selector = document.getElementById("topicSelector");
  for (let topic in topics) {
    const opt = document.createElement("option");
    opt.value = topic;
    opt.innerText = topic;
    selector.appendChild(opt);
  }

  renderResources();
  renderRevisions();

  document
    .getElementById("searchInput")
    .addEventListener("input", renderResources);
  document
    .getElementById("tagFilter")
    .addEventListener("change", renderResources);
});
