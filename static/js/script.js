document.addEventListener('DOMContentLoaded', function () {
  const canvas = document.getElementById('ecoChart');
  const chartTypeSelector = document.getElementById('chartTypeSelector');

  // Injected from Django template
  const username = typeof window.username !== 'undefined' ? window.username : 'User';

  if (!canvas || typeof chartLabels === 'undefined' || typeof chartData === 'undefined') {
    console.warn('Chart data not found or canvas missing.');
    return;
  }

  let chartInstance;

  const createChart = (type) => {
    const config = {
      type: type,
      data: {
        labels: chartLabels,
        datasets: [{
          label: 'Eco Actions',
          data: chartData,
          backgroundColor: 'rgba(25, 135, 84, 0.6)',
          borderColor: 'rgba(25, 135, 84, 1)',
          borderWidth: 1,
          fill: type === 'line' ? false : true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        animation: {
          duration: 1000,
          easing: 'easeOutBounce'
        },
        plugins: {
          legend: { display: false },
          tooltip: { enabled: true },
          title: {
            display: true,
            text: `${username}'s Weekly Eco Actions`,
            font: { size: 18 }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 }
          }
        }
      }
    };

    if (chartInstance) chartInstance.destroy();
    chartInstance = new Chart(canvas, config);
  };

  // Initial chart render
  createChart('bar');

  // Optional chart type toggle
  if (chartTypeSelector) {
    chartTypeSelector.addEventListener('change', function () {
      createChart(this.value);
    });
  }
});
