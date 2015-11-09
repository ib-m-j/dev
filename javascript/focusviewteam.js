google.setOnLoadCallback(drawVisualization);
  
function drawVisualization() {
  var playData = new google.visualization.DataTable({
      cols: [{ label: 'rang', type: 'number'},
	      {label: 'spil', type: 'number'},
	    {label: 'ann', type: 'string', role:'annotation'}],
      rows: ¤playrows¤ 
  });

  var defData = new google.visualization.DataTable({
      cols: [{ label: 'rang', type: 'number'},
	     {label: 'forsvar', type: 'number'},
	    {label: 'ann', type: 'string', role:'annotation'}],
      rows: ¤defrows¤ 
  });
  
  var optionsPlay = {
  chart: {
  legend:{position:'top'}},
  hAxis:{baseline: 'none', baselineColor : 'white', ticks : ¤ticks¤, 
	 gridlines : {color:'white'}},
  vAxis: {gridlines:{color:'white'}, textPosition: 'none' },
			bar:{groupWidth:'85%'},
			fontSize: '32',
      height : '500',
		  chartArea : {left: 20, top: 15, width: '70%', height: '80%'}
  };
  
  var optionsDef = {
  chart: {
  legend:{position:'top'}},
  hAxis:{baseline: 'none', baselineColor : 'white', ticks : ¤ticks¤, 
	 gridlines : {color:'white'}},
			vAxis: {gridlines:{color:'white'}, textPosition: 'none' },
			bar:{groupWidth:'85%'},
			colors : ['red'],
			fontSize: '32',
      height : '500',
		  chartArea : {left: 20, top: 15, width: '70%', height: '80%'} 
  };
  
  var playWrap = new google.visualization.ChartWrapper({
  'chartType':'ColumnChart',
  'containerId':¤playdivtag¤,
  'options': optionsPlay
  })
  playWrap.setDataTable(playData);
  playWrap.draw();

  var defWrap = new google.visualization.ChartWrapper({
  'chartType':'ColumnChart',
  'containerId':¤defdivtag¤,
  'options': optionsDef
  })
  defWrap.setDataTable(defData);
  defWrap.draw();
  }

