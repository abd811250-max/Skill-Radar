document.querySelectorAll(".flash").forEach((flash) => {
  setTimeout(() => flash.remove(), 5000);
});

window.SkillRadar = {
  radarChart(canvasId, labels, current, target) {
    if (!window.Chart || !document.getElementById(canvasId)) return;
    new Chart(document.getElementById(canvasId), {
      type: "radar",
      data: {
        labels,
        datasets: [
          {label: "Current", data: current, borderColor: "#4f46e5", backgroundColor: "rgba(79,70,229,.15)"},
          {label: "Target", data: target, borderColor: "#94a3b8", backgroundColor: "rgba(148,163,184,.08)"}
        ]
      },
      options: {responsive:true, maintainAspectRatio:false, scales:{r:{beginAtZero:true,max:5,ticks:{stepSize:1}}}}
    });
  },
  barChart(canvasId, labels, current, target) {
    if (!window.Chart || !document.getElementById(canvasId)) return;
    new Chart(document.getElementById(canvasId), {
      type: "bar",
      data: {labels, datasets:[
        {label:"Current",data:current,backgroundColor:"#4f46e5"},
        {label:"Target",data:target,backgroundColor:"#cbd5e1"}
      ]},
      options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,max:5,ticks:{stepSize:1}}}}
    });
  },
  doughnutChart(canvasId, labels, values) {
    if (!window.Chart || !document.getElementById(canvasId)) return;
    new Chart(document.getElementById(canvasId), {
      type:"doughnut",
      data:{labels,datasets:[{data:values,backgroundColor:["#4f46e5","#22c55e","#f59e0b","#64748b","#ec4899"]}]},
      options:{responsive:true,maintainAspectRatio:false}
    });
  },
  lineChart(canvasId, labels, values) {
    if (!window.Chart || !document.getElementById(canvasId)) return;
    new Chart(document.getElementById(canvasId), {
      type:"line",
      data:{labels,datasets:[{label:"Skill level",data:values,borderColor:"#4f46e5",backgroundColor:"rgba(79,70,229,.12)",fill:true,tension:.3}]},
      options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,max:5,ticks:{stepSize:1}}}}
    });
  }
};
