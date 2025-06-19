const fileInput = document.getElementById("fileInput");
const filenameDisplay = document.getElementById("filenameDisplay");
const neutralizeBtn = document.getElementById("neutralizeBtn");
const progressBar = document.getElementById("progressFill");
const downloadBtn = document.getElementById("downloadBtn");

let selectedFile = null;
let downloadUrl = null;

// Show filename when user selects a file
fileInput.addEventListener("change", () => {
  selectedFile = fileInput.files[0];
  filenameDisplay.textContent = selectedFile ? selectedFile.name : "No file selected.";
  downloadBtn.style.display = "none";
  progressBar.style.width = "0%";
});

// Trigger processing
neutralizeBtn.addEventListener("click", () => {
  if (!selectedFile) {
    alert("Please choose a file first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);

  neutralizeBtn.disabled = true;
  neutralizeBtn.textContent = "Processing...";
  progressBar.style.transition = "width 0.3s ease-in-out";
  progressBar.style.width = "30%";

  fetch("https://flatline-api-beta.onrender.com/process", {
    method: "POST",
    body: formData,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error("Processing failed.");
      }
      progressBar.style.width = "70%";
      const blob = await response.blob();
      downloadUrl = URL.createObjectURL(blob);

      progressBar.style.width = "100%";
      downloadBtn.style.display = "inline-block";
      downloadBtn.href = downloadUrl;
      downloadBtn.download = "neutralized.wav";
    })
    .catch((err) => {
      alert(err.message);
      progressBar.style.width = "0%";
    })
    .finally(() => {
      neutralizeBtn.disabled = false;
      neutralizeBtn.textContent = "Neutralize";
    });
});
