const fileInput = document.getElementById("fileUpload");
const fileNameDisplay = document.getElementById("fileName");
const processBtn = document.getElementById("processBtn");
const progressBar = document.getElementById("progressBar");
const progressFill = document.getElementById("progressFill");
const statusText = document.getElementById("statusText");
const downloadBtn = document.getElementById("downloadBtn");

let selectedFile = null;
let flattenedBlob = null;

fileInput.addEventListener("change", () => {
  selectedFile = fileInput.files[0];
  fileNameDisplay.textContent = selectedFile ? selectedFile.name : "No file selected";
  resetUI();
});

processBtn.addEventListener("click", () => {
  if (!selectedFile) {
    statusText.textContent = "Please select a file.";
    return;
  }

  progressBar.classList.remove("hidden");
  statusText.textContent = "Processing...";
  progressFill.style.width = "0%";

  const formData = new FormData();
  formData.append("file", selectedFile);

  fetch("https://flatline-api-beta.onrender.com/", {
    method: "POST",
    body: formData
  })
    .then(async (response) => {
      if (!response.ok) throw new Error("Processing failed.");
      const blob = await response.blob();
      flattenedBlob = blob;
      statusText.textContent = "Neutralization complete.";
      downloadBtn.classList.remove("hidden");
    })
    .catch((err) => {
      statusText.textContent = "Error: " + err.message;
    })
    .finally(() => {
      progressFill.style.width = "100%";
    });
});

downloadBtn.addEventListener("click", () => {
  if (!flattenedBlob) return;
  const url = URL.createObjectURL(flattenedBlob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "flatlined.wav";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
});

function resetUI() {
  downloadBtn.classList.add("hidden");
  progressBar.classList.add("hidden");
  progressFill.style.width = "0%";
  statusText.textContent = "";
  flattenedBlob = null;
}
