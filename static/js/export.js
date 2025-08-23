document.addEventListener('DOMContentLoaded', function () {
  const canvas = document.getElementById('ecoChart');
  const exportBtn = document.querySelector('.export-btn');

  if (canvas && exportBtn) {
    exportBtn.addEventListener('click', function () {
      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/png');
      link.download = 'eco-chart.png';
      link.click();
    });
  }
});
