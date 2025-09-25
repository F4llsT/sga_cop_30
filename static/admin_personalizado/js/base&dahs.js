const getJsonData = (id) => {
    const el = document.getElementById(id);
    if (!el) return [];
    try { return JSON.parse(el.textContent || '[]'); } catch (e) { return []; }
  };
  
  const eventosCanvas = document.getElementById('eventosChart');
  let eventosChartInstance = null;
  
  const renderCharts = () => {
    if (eventosChartInstance) { try { eventosChartInstance.destroy(); } catch (e) {} }
    const isMobile = window.innerWidth < 768;
  
    if (eventosCanvas && typeof Chart !== 'undefined') {
      const fullLabels = getJsonData('eventos-labels');
      const values = getJsonData('eventos-values');
      const shortLabels = fullLabels.map(l =>
        (typeof l === 'string' && l.length > 22) ? (l.slice(0, 22) + '…') : l
      );
  
      const ctx = eventosCanvas.getContext('2d');
      eventosChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: shortLabels,
          datasets: [{
            label: 'Favoritações',
            data: values,
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          indexAxis: isMobile ? 'x' : 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            datalabels: { display: false },
            tooltip: {
              callbacks: {
                title: (items) => {
                  if (!items || !items.length) return '';
                  const idx = items[0].dataIndex;
                  return fullLabels[idx] || '';
                }
              }
            }
          },
          scales: {
            y: { beginAtZero: true },
            x: {
              ticks: {
                autoSkip: false,
                maxRotation: isMobile ? 45 : 0,
                minRotation: isMobile ? 45 : 0
              }
            }
          }
        }
      });
    }
  };
  
  // Init once + resize debounce
  renderCharts();
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(renderCharts, 250);
  });