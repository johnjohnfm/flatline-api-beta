
// ✅ Updated FLATLINE UI Script with AUTHENTIC AUDIO enhancements

const fileUpload = document.getElementById("fileUpload");
const fileName = document.getElementById("fileName");
const processBtn = document.getElementById("processBtn");
const progressBar = document.getElementById("progressBar");
const progressFill = document.getElementById("progressFill");
const statusText = document.getElementById("statusText");
const downloadBtn = document.getElementById("downloadBtn");

const MAX_SIZE_MB = 100;

function resetState() {
  fileName.textContent = "No file selected";
  statusText.textContent = "";
  processBtn.disabled = true;
  progressFill.style.width = "0%";
  progressBar.classList.add("is-hidden");
  downloadBtn.classList.add("is-hidden");
  downloadBtn.onclick = null;
}

fileUpload.addEventListener("change", () => {
  resetState();
  const file = fileUpload.files[0];
  if (!file) return;

  if (!/^audio\/(wav|mpeg|flac|aiff)$/.test(file.type)) {
    statusText.textContent = "Invalid file type.";
    fileUpload.value = "";
    return;
  }

  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    statusText.textContent = `File exceeds ${MAX_SIZE_MB}MB.`;
    fileUpload.value = "";
    return;
  }

  fileName.textContent = file.name;
  statusText.textContent = "Ready to process.";
  processBtn.disabled = false;
});

processBtn.addEventListener("click", async () => {
  const file = fileUpload.files[0];
  if (!file) return;

  // UI Setup
  resetState();
  progressBar.classList.remove("is-hidden");
  document.querySelector(".aa-progress").setAttribute("aria-busy", "true");
  statusText.textContent = "Processing...";
  processBtn.disabled = true;

  // Animate fake progress to 90%
  let progress = 0;
  const progressInterval = setInterval(() => {
    progress += 1;
    progressFill.style.width = progress + "%";
    if (progress >= 90) clearInterval(progressInterval);
  }, 20);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://localhost:10000/neutralize/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Processing failed");

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    progressFill.style.width = "100%";
    statusText.textContent = "Processing complete.";
    document.querySelector(".aa-progress").removeAttribute("aria-busy");

    downloadBtn.classList.remove("is-hidden");
    downloadBtn.onclick = () => {
      const a = document.createElement("a");
      a.href = url;
      a.download = "flatlined.wav";
      a.click();
    };
  } catch (err) {
    clearInterval(progressInterval);
    progressFill.style.width = "0%";
    statusText.textContent = "An error occurred. Please try again.";
    console.error(err);
    document.querySelector(".aa-progress").removeAttribute("aria-busy");
  }
});
