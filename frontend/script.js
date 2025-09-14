const fileInput = document.getElementById("fileInput");
const messageInput = document.getElementById("message");
const output = document.getElementById("output");
const preview = document.getElementById("preview");
const fileNameDisplay = document.getElementById("fileName");


fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  fileNameDisplay.textContent = file ? file.name : "No file selected";
});

async function encode() {
    const fileInput = document.getElementById('fileInput');
    const message = document.getElementById('message').value;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('message', message);

    fetch('http://127.0.0.1:8000/encode', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'encoded_image.png'; // name of downloaded file
        document.body.appendChild(a);
        a.click();
        a.remove();
    })
    .catch(err => console.error(err));
}


async function decode() {
  const file = fileInput.files[0];
  if (!file) {
    output.textContent = "⚠ Please select a file first.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://127.0.0.1:8000/decode", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      output.textContent = "Error: " + (err.detail || "Unknown error");
      return;
    }

    const result = await response.json();
    output.textContent = "💬 Hidden message: " + result.message;

  } catch (error) {
    console.error(error);
    output.textContent = "⚠ Something went wrong!";
  }
}

async function detect() {
  const file = fileInput.files[0];
  if (!file) {
    output.textContent = "⚠ Please select a file first.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://127.0.0.1:8000/detect", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      output.textContent = "Error: " + (err.detail || "Unknown error");
      return;
    }

    const result = await response.json();
    let text = `🤖 Detection result: ${result.result} (${result.mode})`;
    if (result.probability) {
      text += ` — Probability: ${result.probability}`;
    }
    output.textContent = text;

  } catch (error) {
    console.error(error);
    output.textContent = "⚠ Something went wrong!";
  }
}
