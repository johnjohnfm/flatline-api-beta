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
    fileNameDisplay.textContent = file ? file.name : "No file selected";
    downloadBtn.disabled = true;
    downloadBtn.style.opacity = 0.5;
  });

  uploadBtn.addEventListener("click", () => {
    const file = fileInput.files[0];
    if (!file) {
      alert("Choose a file first...");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    progressBar.style.display = "block";
    progressFill.style.width = "0%";

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "https://flatline-api-beta.onrender.com/process", true);

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percentComplete = (event.loaded / event.total) * 100;
        progressFill.style.width = `${percentComplete.toFixed(1)}%`;
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        progressFill.style.width = "100%";
        const blob = xhr.response;
        downloadUrl = URL.createObjectURL(blob);
        downloadBtn.disabled = false;
        downloadBtn.style.opacity = 1;
      } else {
        handleError("Processing Failed.");
      }
    };

    xhr.onerror = () => {
      handleError("An error occurred during upload.");
    };

    xhr.responseType = "blob";
    xhr.send(formData);
  });

  downloadBtn.addEventListener("click", () => {
    if (downloadUrl) {
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = "neutralized.wav";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  });

  function handleError(message) {
    progressBar.style.display = "none";
    progressFill.style.width = "0%";
    alert(message);
  }
});
