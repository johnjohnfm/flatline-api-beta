const fileInput = document.getElementById("fileUpload");
const fileNameDisplay = document.getElementById("fileName");
const processBtn = document.getElementById("processBtn");
const downloadBtn = document.getElementById("downloadBtn");
const progressBar = document.getElementById("progressBar");
const progressFill = document.getElementById("progressFill");
const statusText = document.getElementById("statusText");

let selectedFile = null;
let processedBlob = null;

// Display filename when user selects a file
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    selectedFile = fileInput.files[0];
    fileNameDisplay.textContent = selectedFile.name;
  }
});

// Handle the "Neutralize" button click
processBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    alert("Please choose a file first.");
    return;
  }

  // Initialize UI
  progressBar.classList.remove("hidden");
  progressFill.style.width = "0%";
  statusText.textContent = "Processing...";
  processBtn.disabled = true;
  downloadBtn.classList.add("hidden");

  try {
    // Simulated progress animation (can be upgraded to reflect true progress)
    let progress = 0;
    const simulate = setInterval(() => {
      if (progress < 90) {
        progress += 10;
        progressFill.style.width = progress + "%";
      } else {
        clearInterval(simulate);
      }
    }, 200);

    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch("https://flatline-api-beta.onrender.com/process", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Processing failed");

    const blob = await response.blob();
    processedBlob = blob;

    // Update UI on success
    progressFill.style.width = "100%";
    statusText.textContent = "Done!";
    downloadBtn.classList.remove("hidden");
  } catch (error) {
    statusText.textContent = "Error: " + error.message;
  } finally {
    processBtn.disabled = false;
  }
});

// Download processed audio file
downloadBtn.addEventListener("click", () => {
  if (!processedBlob) return;
  const url = URL.createObjectURL(processedBlob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "neutralized.wav";
  a.click();
  URL.revokeObjectURL(url);
});
