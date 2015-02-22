google.load("visualization", "1.1", {packages:["bar"]});
google.setOnLoadCallback(drawChart);
function drawChart() {
    var data = google.visualization.arrayToDataTable([¤rows;]);
    
    var options = {
        chart: {
            title: '¤title;',
            subtitle: '¤subtitle;',
        }
    };
    var chart = new google.charts.Bar(document.getElementById('¤divtag;'));
    chart.draw(data, options);

   function selectHandler() {
	var selectedItem = chart.getSelection()[0];
	if (selectedItem) {
	    var value = data.getValue(selectedItem.row, selectedItem.column);
	    alert('The user selected ' + value + selectedItem.row);
	}
    }

    // Listen for the 'select' event, and call my function selectHandler() when
    // the user selects something on the chart.
    google.visualization.events.addListener(chart, 'select', selectHandler);

};
