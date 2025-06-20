const $ = (id) => document.getElementById(id);

const fileInput = $("fileUpload");
const fileLabel = $("fileName");
const processBtn = $("processBtn");
const progressBar = $("progressBar");
const progressFill = $("progressFill");
const status = $("statusText");
const downloadBtn = $("downloadBtn");

const MAX_MB = 100;
const NEUTRALIZE_ENDPOINT = "http://localhost:10000/neutralize/";

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;

  const typeValid = /^audio\/(wav|mpeg|flac|aiff)$/.test(file.type);
  const sizeValid = file.size <= MAX_MB * 1024 * 1024;

  if (!typeValid) return showError("Unsupported file format.");
  if (!sizeValid) return showError(`File exceeds ${MAX_MB}MB limit.`);

  fileLabel.textContent = file.name;
  status.textContent = "Ready for neutralization.";
  processBtn.disabled = false;
});

processBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  setWorking(true);

  const data = new FormData();
  data.append("file", file);

  try {
    const res = await fetch(NEUTRALIZE_ENDPOINT, { method: "POST", body: data });
    if (!res.ok) throw new Error("Server error during processing.");

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    downloadBtn.classList.remove("is-hidden");
    downloadBtn.onclick = () => triggerDownload(url);

    progressFill.style.width = "100%";
    status.textContent = "Neutralization complete.";
  } catch (err) {
    showError(`Error: ${err.message}`);
  } finally {
    setWorking(false);
  }
});

function setWorking(isActive) {
  progressBar.classList.toggle("is-hidden", !isActive);
  progressFill.style.width = isActive ? "0%" : progressFill.style.width;
  status.textContent = isActive ? "Processing..." : "";
  processBtn.disabled = isActive;
}

function showError(message) {
  status.textContent = message;
  fileInput.value = "";
  fileLabel.textContent = "No file selected";
  processBtn.disabled = true;
}

function triggerDownload(url) {
  const a = document.createElement("a");
  a.href = url;
  a.download = "flatlined.wav";
  a.click();
}
