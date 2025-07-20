function ingest() {
  const file = document.getElementById("fileInput").files[0];
  const link = document.getElementById("linkInput").value.trim();
  if (file || link) {
    alert("Simulated: Resource added.");
    // In production, call backend ingest API here
  } else {
    alert("Please upload a file or paste a link.");
  }
}

async function loadTopic() {
  const selector = document.getElementById("topicSelector");
  const topic = selector.value;

  try {
    const res = await fetch(
      `http://localhost:5000/api/topic/${encodeURIComponent(topic)}`
    );
    if (!res.ok) throw new Error("Topic fetch failed");

    const data = await res.json();

    // Set title and summary
    document.getElementById("topicTitle").innerText = topic;
    document.getElementById("topicSummary").innerText = data.summary;

    // Populate key points
    const keyList = document.getElementById("keyPoints");
    keyList.innerHTML = "";
    (data.keyPoints || []).forEach((point) => {
      const li = document.createElement("li");
      li.innerText = point;
      keyList.appendChild(li);
    });

    // Show the summary section
    toggleSection("summary");
  } catch (err) {
    console.error("Failed to load topic:", err);
    document.getElementById("topicTitle").innerText = topic;
    document.getElementById("topicSummary").innerText =
      "Summary could not be loaded.";
    document.getElementById("keyPoints").innerHTML = "";
  }
}

let currentSection = null;
function toggleSection(section) {
  const all = ["summarySection", "quizSection", "explainSection"];
  const btnMap = {
    summary: "Summary",
    explain: "Deep Explain",
    quiz: "Quiz",
  };
  // Always remove .active from all buttons first
  document
    .querySelectorAll(".controls-btn")
    .forEach((btn) => btn.classList.remove("active"));

  // If closing the current section
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

  // Add .active to the corresponding button
  document.querySelectorAll(".controls-btn").forEach((btn) => {
    if (btn.textContent.trim() === btnMap[section]) {
      btn.classList.add("active");
    }
  });

  // Close all sections except the one being opened
  all.forEach((id) => {
    const el = document.getElementById(id);
    if (el && id !== section + "Section") {
      el.classList.remove("active");
      el.style.maxHeight = "0";
    }
  });

  const target = document.getElementById(section + "Section");
  if (target) {
    target.classList.add("active");
    target.style.maxHeight = target.scrollHeight + "px";
  }
  currentSection = section;
}

// On window resize, update maxHeight for open sections
window.addEventListener("resize", () => {
  const all = ["summarySection", "quizSection", "explainSection"];
  all.forEach((id) => {
    const el = document.getElementById(id);
    if (el && el.classList.contains("active")) {
      el.style.maxHeight = el.scrollHeight + "px";
    }
  });
});

function showOnly(sectionId) {
  // Only used for graphSection now
  const all = ["graphSection"];
  all.forEach((id) => {
    document.getElementById(id).classList.add("hidden");
  });
  document.getElementById(sectionId + "Section").classList.remove("hidden");
}

// Populate topics
document.addEventListener("DOMContentLoaded", async () => {
  const selector = document.getElementById("topicSelector");

  if (!selector) {
    console.error("❌ topicSelector element not found.");
    return;
  }

  try {
    const res = await fetch("http://localhost:5000/api/topics");
    const topicList = await res.json();

    console.log("[✅] Topics received:", topicList);

    selector.innerHTML = ""; // Clear placeholder

    topicList.forEach((topic) => {
      const opt = document.createElement("option");
      opt.value = topic;
      opt.innerText = topic;
      selector.appendChild(opt);
    });

    if (topicList.length > 0) {
      selector.value = topicList[0];
      loadTopic(); // auto-load
    }
  } catch (err) {
    console.error("[✗] Failed to load topic list:", err);
  }
});

let uploadMode = "file"; // default

function toggleUploadMode() {
  const onoffToggle = document.getElementById("onoffToggle");
  const onoffSlider = document.getElementById("onoffSlider");
  const fileInput = document.getElementById("fileInput");
  const linkInput = document.getElementById("linkInput");

  if (uploadMode === "file") {
    uploadMode = "link";
    onoffSlider.style.left = "46px";
    onoffToggle.classList.remove("file-active");
    onoffToggle.classList.add("link-active");
    fileInput.style.display = "none";
    linkInput.style.display = "block";
  } else {
    uploadMode = "file";
    onoffSlider.style.left = "2px";
    onoffToggle.classList.remove("link-active");
    onoffToggle.classList.add("file-active");
    fileInput.style.display = "block";
    linkInput.style.display = "none";
  }
}

// Set initial toggle state on load
window.addEventListener("DOMContentLoaded", () => {
  const onoffToggle = document.getElementById("onoffToggle");
  const onoffSlider = document.getElementById("onoffSlider");
  onoffSlider.style.left = "2px";
  onoffToggle.classList.add("file-active");
  document.getElementById("fileInput").style.display = "block";
  document.getElementById("linkInput").style.display = "none";
  uploadMode = "file";
});

// 3D Brain Model beside heading using three.js
window.addEventListener("DOMContentLoaded", () => {
  // 3D Brain Model
  const container = document.getElementById("brain-3d-container");
  if (container && window.THREE) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
    camera.position.set(0, 0, 2.5);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setClearColor(0xffffff, 0); // fallback: white bg, fully transparent
    renderer.setSize(48, 48);
    container.appendChild(renderer.domElement);

    // Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 1.1);
    scene.add(ambient);
    const directional = new THREE.DirectionalLight(0xffffff, 0.7);
    directional.position.set(2, 2, 2);
    scene.add(directional);

    // Load a CORS-friendly GLB brain model
    const loader = new THREE.GLTFLoader();
    loader.load(
      // Free brain model from Poly Pizza (CC0):
      // https://poly.pizza/m/3Qw1Qw1Qw1Qw1Qw1Qw1Qw1
      "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/BrainStem/glTF-Binary/BrainStem.glb",
      function (gltf) {
        const model = gltf.scene;
        model.scale.set(1.1, 1.1, 1.1);
        model.position.set(0, -0.2, 0);
        scene.add(model);
        animate();
        // Interactivity: rotate on drag
        let isDragging = false,
          prevX = 0;
        renderer.domElement.addEventListener("mousedown", (e) => {
          isDragging = true;
          prevX = e.clientX;
        });
        window.addEventListener("mouseup", () => {
          isDragging = false;
        });
        window.addEventListener("mousemove", (e) => {
          if (isDragging) {
            const dx = e.clientX - prevX;
            model.rotation.y += dx * 0.01;
            prevX = e.clientX;
          }
        });
      },
      undefined,
      function (error) {
        console.error("3D brain model failed to load:", error);
        container.innerHTML =
          '<span style="color:#888;font-size:10px;">(3D brain failed to load)</span>';
      }
    );
    function animate() {
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }
  }
});

// Profile menu toggle logic
window.addEventListener("DOMContentLoaded", () => {
  const profilePicWrapper = document.querySelector(".profile-pic-wrapper");
  const profileMenu = document.getElementById("profile-menu");
  if (profilePicWrapper && profileMenu) {
    let menuOpen = false;
    function closeMenu(e) {
      // Only close if click is outside menu and not on any element inside
      if (
        !profileMenu.contains(e.target) &&
        !profilePicWrapper.contains(e.target)
      ) {
        profileMenu.style.display = "none";
        menuOpen = false;
        document.removeEventListener("mousedown", closeMenu);
      }
    }
    profilePicWrapper.addEventListener("click", (e) => {
      e.stopPropagation();
      menuOpen = !menuOpen;
      profileMenu.style.display = menuOpen ? "flex" : "none";
      if (menuOpen) {
        setTimeout(() => document.addEventListener("mousedown", closeMenu), 0);
      } else {
        document.removeEventListener("mousedown", closeMenu);
      }
    });
    // Prevent menu from closing when clicking any element inside
    profileMenu.addEventListener("mousedown", (e) => {
      if (profileMenu.contains(e.target)) {
        e.stopPropagation();
      }
    });
  }
});

// Fullscreen button for graph card
window.addEventListener("DOMContentLoaded", () => {
  const fsBtn = document.getElementById("fullscreen-btn");
  const graphContainer = document.getElementById("graph-container");
  if (fsBtn && graphContainer) {
    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        if (graphContainer.requestFullscreen)
          graphContainer.requestFullscreen();
        else if (graphContainer.webkitRequestFullscreen)
          graphContainer.webkitRequestFullscreen();
        else if (graphContainer.msRequestFullscreen)
          graphContainer.msRequestFullscreen();
      } else {
        if (document.exitFullscreen) document.exitFullscreen();
        else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
        else if (document.msExitFullscreen) document.msExitFullscreen();
      }
    }
    fsBtn.addEventListener("click", toggleFullscreen);
    fsBtn.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        toggleFullscreen();
      }
    });
  }
});

// Theme toggle logic for minimal button
window.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("footerThemeToggle");
  const icon = document.getElementById("themeIcon");
  if (!btn || !icon) return;
  function setIcon() {
    if (document.body.classList.contains("dark")) {
      icon.innerHTML =
        '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M16.5 13.5A7 7 0 0 1 6.5 3.5a7 7 0 1 0 10 10z" fill="#111"/></svg>';
    } else {
      icon.innerHTML =
        '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="5" fill="#fff"/></svg>';
    }
  }
  setIcon();
  btn.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    setIcon();
  });
});

// Resource Finder logic
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("resourceFinderForm");
  const input = document.getElementById("resourceQuery");
  const results = document.getElementById("resourceResults");

  if (form && input && results) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const query = input.value.trim();
      if (!query) {
        results.innerHTML =
          '<span style="color:#888">Enter a search term.</span>';
        return;
      }

      try {
        const res = await fetch(
          `http://localhost:5000/api/resources?q=${encodeURIComponent(query)}`
        );
        if (!res.ok) throw new Error("Resource search failed");

        const found = await res.json();

        if (found.length === 0) {
          results.innerHTML =
            '<span style="color:#888">No resources found.</span>';
        } else {
          results.innerHTML = found
            .map(
              (res) =>
                `<div style="margin-bottom:0.5em;"><strong>${res.name}</strong> <span style="color:#aaa;font-size:0.95em;">(${res.type})</span></div>`
            )
            .join("");
        }
      } catch (err) {
        console.error("Failed to search resources:", err);
        results.innerHTML =
          '<span style="color:#d9534f">Error searching for resources.</span>';
      }
    });
  }
});

function addResource() {
  const formData = new FormData();
  const endpoint = "http://localhost:5000/api/ingest";

  if (uploadMode === "file") {
    const file = document.getElementById("fileInput").files[0];
    if (!file) {
      alert("Please select a file.");
      return;
    }
    formData.append("file", file);
    formData.append("type", "file");
  } else {
    const link = document.getElementById("linkInput").value.trim();
    if (!link) {
      alert("Please paste a valid link.");
      return;
    }
    formData.append("link", link);
    formData.append("type", "link");
  }

  fetch(endpoint, {
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      alert("✅ Resource added: " + (data.filename || data.link));

      // Display the summary (if returned)
      if (data.summary) {
        const summaryBox = document.getElementById("topicSummary");
        summaryBox.innerText = data.summary;
        summaryBox.scrollIntoView({ behavior: "smooth" });
      } else {
        alert("No summary available for this resource.");
      }
    })
    .catch((err) => {
      console.error(err);
      alert("❌ Failed to add resource");
    });
}
