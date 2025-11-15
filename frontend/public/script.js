import { fetchSimulate } from "./services/apiService.js";

const btn = document.getElementById("simulateBtn");
const totalProfitEl = document.getElementById("totalProfit");
const tableBody = document.querySelector("#stepsTable tbody");

let priceChart = null;
let rewardChart = null;

btn.addEventListener("click", async () => {
  try {
    btn.disabled = true;
    btn.textContent = "Loading...";
    
    const data = await fetchSimulate();

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
    btn.disabled = false;
    btn.textContent = "Run Simulation";
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
