const API_BASE = "http://127.0.0.1:8000";
const DATE_REGEX = /^\d{2}-\d{2}-\d{4}$/;

function showLoading() {
  document.getElementById("loading").classList.remove("hidden");
  document.getElementById("result").classList.add("hidden");
  document.getElementById("downloadBtn").disabled = true;
}

function hideLoading() {
  document.getElementById("loading").classList.add("hidden");
  document.getElementById("downloadBtn").disabled = false;
}

function showResult(content, isError = false) {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = content;
  resultDiv.className = `result ${isError ? 'error' : 'success'}`;
  resultDiv.classList.remove("hidden");
}

async function downloadAllCauseLists() {
  const dateInput = document.getElementById("date").value.trim();

  // Validate date format
  if (!dateInput || !DATE_REGEX.test(dateInput)) {
    showResult("❌ Please enter a valid date in <b>DD-MM-YYYY</b> format (e.g., 17-10-2025).", true);
    return;
  }

  showLoading();

  try {
    const response = await fetch(`${API_BASE}/api/download_all_cause_lists`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date: dateInput })
    });

    const data = await response.json();

    if (response.ok && data.downloaded_files && data.downloaded_files.length > 0) {
      const links = data.downloaded_files.map(file => {
        const filename = file.split("/").pop();
        return `<a href="${API_BASE}/download/${encodeURIComponent(filename)}" target="_blank">📄 ${filename}</a>`;
      }).join("");
      showResult(`<b>✅ Downloaded ${data.downloaded_files.length} PDF(s):</b><br>${links}`);
    } else {
      showResult("⚠️ No cause lists found for this date. Try a recent or future date.", true);
    }
  } catch (err) {
    console.error("Fetch error:", err);
    showResult(`❌ Failed to connect to backend. Make sure FastAPI is running on port 8000.`, true);
  } finally {
    hideLoading();
  }
}

// Optional: Allow Enter key to trigger download
document.getElementById("date").addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    downloadAllCauseLists();
  }
});