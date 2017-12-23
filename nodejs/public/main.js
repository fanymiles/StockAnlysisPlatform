$(function () {
	var socket = io();
	console.log('create socketio client');


	$("#chart").height($(window).height() - $("#header").height() * 2)
	var data_points = [];
	data_points.push({
		values: [],
		key : 'GOOG',
	});

	var chart = nv.models.lineChart()
		.interpolate('monotone')
		.margin({
			bottom:100
		})
		.useInteractiveGuideline(true)
		.showLegend(true)
		.color(d3.scale.category10().range());

	chart.yAxis.axisLabel('Price');
	chart.xAxis.axisLabel('Time').tickFormat(formatTick);


	nv.addGraph(loadGraph)

	function loadGraph() {
		d3.select('#chart svg')
			.datum(data_points)
			.transition()
			.duration(s)
			.call(chart);

		nv.utils.windowResize(chart.update);
		return chart;

	}

	function dataCallback(message) {
		
		// console.log(message);
		var parsed = JSON.parse(message);
		var timestamp = parsed['timestamp'];
		var average = parsed['average'];
		var symbol = parsed['symbol'];

		var point = {};
		point.x = timestamp;
		point.y = average;

		data_points[0].values.push(point);
		if (data_points[0].values.length > 120) {
			data_points[0].values.shift();
		}
		loadGraph();
	}

	function formatTick(time) {
		var date = new Date(time = 1000);
		return d3.time.format('%H:%M:%S')(date);
	}
	// register callback function
	socket.on('data',function (data) {
		//console.log(data);
		dataCallback(data);
	});

});