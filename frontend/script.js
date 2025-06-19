// script.js

document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("fileInput");
  const uploadBtn = document.getElementById("uploadBtn");
  const progressBar = document.getElementById("progressBar");
  const progressFill = document.getElementById("progressFill");
  const downloadBtn = document.getElementById("downloadBtn");
  const fileNameDisplay = document.getElementById("fileName");

  let downloadUrl = null;

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) {
      fileNameDisplay.textContent = file.name;
      downloadBtn.disabled = true;
      downloadBtn.style.opacity = 0.5;
    } else {
      fileNameDisplay.textContent = "No file selected";
    }
  });

  uploadBtn.addEventListener("click", () => {
    const file = fileInput.files[0];

    if (!file) {
      alert("Choose file first...");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    progressBar.style.display = "block";
    progressFill.style.width = "0%";

    // Simulate progress while processing
    let progress = 0;
    const interval = setInterval(() => {
      if (progress < 90) {
        progress += 5;
        progressFill.style.width = `${progress}%`;
      }
    }, 200);

    fetch("https://flatline-api-beta.onrender.com/process", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Processing failed");
        }
        return response.blob();
      })
      .then((blob) => {
        clearInterval(interval);
        progressFill.style.width = "100%";

        downloadUrl = URL.createObjectURL(blob);
        downloadBtn.disabled = false;
        downloadBtn.style.opacity = 1;
      })
      .catch((error) => {
        clearInterval(interval);
        console.error("Error:", error);
        alert("Processing Failed.");
        progressBar.style.display = "none";
      });
  });

  downloadBtn.addEventListener("click", () => {
    if (!downloadUrl) return;

    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = "neutralized.wav";
    document.body.appendChild(a);
    a.click();
    a.remove();
  });
});
