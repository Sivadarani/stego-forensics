async function encode() {
  const file = fileInput.files[0];
  const message = messageInput.value;
  if (!file || !message) {
    output.textContent = "⚠ Please select a file and enter a message.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("message", message);

  try {
    const response = await fetch("http://127.0.0.1:8000/encode", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      output.textContent = "Error: " + (err.detail || "Unknown error");
      return;
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    // ✅ Show encoded image in preview
    const img = document.createElement("img");
    img.src = url;
    img.style.maxWidth = "100%";
    img.style.borderRadius = "10px";
    preview.innerHTML = "<h4>Encoded Preview:</h4>";
    preview.appendChild(img);

    // ✅ Trigger download
    const a = document.createElement("a");
    a.href = url;
    a.download = "encoded.png";
    document.body.appendChild(a);
    a.click();
    a.remove();

    // ❌ Do NOT revoke immediately → wait until image is loaded
    img.onload = () => {
      URL.revokeObjectURL(url);
    };

    output.textContent = "✅ Encoded image previewed and downloaded!";
  } catch (error) {
    console.error(error);
    output.textContent = "⚠ Something went wrong!";
  }
}
