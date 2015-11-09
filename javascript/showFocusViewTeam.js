google.setOnLoadCallback(drawVisualization);
  
function drawVisualization() {
  var data = new google.visualization.DataTable({
      cols: [{ label: 'rang', type: 'number'},{ label: 'spil', type: 'number'},
	     { label: 'forsvar', type: 'number'}],
      rows: ¤rows¤ 
  });
  
  var options = {
  chart: {
  legend:{position:'top'},
  hAxis:{baseline: 'none', baselineColor : 'white', ticks : ¤ticks¤, 
	 gridlines : {color:'white'}},
  vAxis: {gridlines:{color:'white'}, textPosition: 'none' },
  };
  
  var wrap = new google.visualization.ChartWrapper({
  'chartType':'ColumnChart',
  'containerId':¤container¤,
  'options': options
  })
  wrap.setDataTable(data);
  
  wrap.draw();
  }

