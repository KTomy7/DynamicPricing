import { fetchSimulate, fetchAnalysis } from "./services/apiService.js";

const simulateBtn = document.getElementById("simulateBtn");
const totalProfitEl = document.getElementById("totalProfit");
const tableBody = document.querySelector("#stepsTable tbody");
const analyzeBtn = document.getElementById("analyzeBtn");
const analysisSummaryCard = document.getElementById("analysisSummaryCard");
const simulationContent = document.getElementById("simulationContent");

let priceChart = null;
let rewardChart = null;

simulateBtn.addEventListener("click", async () => {
  try {
    simulateBtn.disabled = true;
    simulateBtn.textContent = "Loading...";
    
    const data = await fetchSimulate();

    analysisSummaryCard.classList.add("hidden");
    simulationContent.classList.remove("hidden");

    totalProfitEl.textContent = Number(data.total_profit).toFixed(2);

    tableBody.innerHTML = "";
    const steps = data.steps || [];

    steps.forEach(s => {
      const row = `
        <tr>
          <td>${s.step}</td>
          <td>${s.action}</td>
          <td>${Number(s.new_price).toFixed(2)}</td>
          <td>${s.quantity}</td>
          <td>${Number(s.reward).toFixed(2)}</td>
        </tr>`;
      tableBody.insertAdjacentHTML("beforeend", row);
    });

    renderCharts(steps);
  } catch (error) {
    console.error("Error fetching simulation data:", error);
    alert("Failed to load simulation data. Check console for details.");
  } finally {
    simulateBtn.disabled = false;
    simulateBtn.textContent = "Run Simulation";
  }
});

analyzeBtn.addEventListener("click", async () => {
  try {
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing... (this may take a while)";
    analysisSummaryCard.style.display = "none";

    const summary = await fetchAnalysis();

    simulationContent.classList.add("hidden");
    analysisSummaryCard.classList.remove("hidden");

    document.getElementById("avgProfit").textContent = `$${summary.average_profit}`;
    document.getElementById("avgSteps").textContent = summary.average_steps_taken;
    document.getElementById("avgIncrease").textContent = summary.average_action_increase;
    document.getElementById("avgMaintain").textContent = summary.average_action_maintain;
    document.getElementById("avgDecrease").textContent = summary.average_action_decrease;
    
    analysisSummaryCard.style.display = "block";

  } catch (error) {
    console.error("Error fetching analysis data:", error);
    alert("Failed to load analysis data. Check console for details.");
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Run 100-Run Analysis";
  }
});

function renderCharts(steps) {
  const labels = steps.map(s => s.step);
  const prices = steps.map(s => s.new_price);
  const rewards = steps.map(s => s.reward);

  if (priceChart) priceChart.destroy();
  if (rewardChart) rewardChart.destroy();

  priceChart = new Chart(document.getElementById("priceChart"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Price Evolution",
          data: prices,
          borderWidth: 2,
          borderColor: "#007bff",
          backgroundColor: "rgba(0,123,255,0.08)",
          fill: true,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Price Evolution Over Steps",
          color: "#222",
          font: { size: 16, weight: "600" },
          padding: { top: 8, bottom: 8 },
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: "Step",
            color: "#444",
            font: { size: 12, weight: "600" }
          }
        },
        y: {
          title: {
            display: true,
            text: "Price",
            color: "#444",
            font: { size: 12, weight: "600" }
          }
        }
      }
    },
  });

  rewardChart = new Chart(document.getElementById("rewardChart"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Reward per Step",
          data: rewards,
          backgroundColor: "rgba(0,123,255,0.7)",
          borderColor: "#007bff",
          borderWidth: 1,
        },
      ],
    },
    options: { 
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Reward per Step",
          color: "#222",
          font: { size: 16, weight: "600" },
          padding: { top: 8, bottom: 8 },
        },
      }, 
      scales: {
        x: {
          title: {
            display: true,
            text: "Step",
            color: "#444",
            font: { size: 12, weight: "600" }
          }
        },
        y: {
          title: {
            display: true,
            text: "Reward",
            color: "#444",
            font: { size: 12, weight: "600" }
          }
        }
      }
    },
  });
}
