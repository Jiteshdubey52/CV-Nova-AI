lucide.createIcons();

const chart = document.getElementById("scoreChart");
if (chart) {
  const scores = (chart.dataset.scores || "0").split(",").filter(Boolean).map(Number);
  new Chart(chart, {
    type: "line",
    data: { labels: scores.map((_, i) => `Resume ${i + 1}`), datasets: [{ label: "ATS", data: scores, borderColor: "#0891b2", backgroundColor: "rgba(8,145,178,.12)", fill: true, tension: .35 }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100 } } }
  });
}

document.querySelectorAll("[data-ai-action]").forEach((button) => {
  button.addEventListener("click", async () => {
    const output = document.getElementById("ai-output");
    button.disabled = true;
    output.textContent = "Generating...";
    const form = new FormData();
    form.append("csrf_token", document.querySelector("meta[name='csrf-token']")?.content || "");
    try {
      const response = await fetch(`/ai/resume/${button.dataset.resume}/${button.dataset.aiAction}`, { method: "POST", body: form, credentials: "same-origin" });
      const contentType = response.headers.get("content-type") || "";
      const data = contentType.includes("application/json") ? await response.json() : { error: await response.text() };
      output.textContent = data.output || data.error || "No output returned.";
    } catch (error) {
      output.textContent = `AI request failed: ${error.message}`;
    } finally {
      button.disabled = false;
    }
  });
});
