'use strict';

/**
 * @ngdoc service
 * @name pvsApp.AmchartsService
 * @description
 * # AmchartsService
 * Service in the pvsApp.
 */
angular.module('pvsApp')
  .service('AmchartsService', ['$window', function ($window) {
    // AngularJS will instantiate a singleton by calling "new" on this function
	  var service = this;
	  service.getChartGraphs = function(chartData){
		  var chartGraphs = [];
		  for (var key in chartData[chartData.length-1]) {
			  if (key !== 'date' && key !== 'lux') {
				  chartGraphs.push({
			          //alphaField: 'alpha',
			          balloonText: '<span style="font-size:12px;">[[title]] in [[category]]<br><span style="font-size:20px;">[[value]]</span> [[additional]]</span>',
			          fillAlphas: 0.6,
			          lineAlpha: 0.4,
			          //type: 'column',
			          title: 'PVI(' + key + ')',
			          valueField: key,
			          valueAxis: 'energyAxis',
			          dashLengthField: 'dashLengthColumn',
			          type: 'smoothedLine',
			      });
			  }
			  if (key === 'lux') {
				  chartGraphs.push({
			          //alphaField: 'alpha',
					  bullet: 'round',
			          balloonText: '<span style="font-size:12px;">[[title]] in [[category]]<br><span style="font-size:20px;">[[value]]</span> [[additional]]</span>',
			          fillAlphas: 0,
			          lineAlpha: 0.4,
			          //type: 'line',
			          title: 'LUX',
			          valueField: key,
			          valueAxis: 'luxAxis',
			          dashLengthField: 'dashLengthColumn',
			          type: 'smoothedLine',
			      });
			  }
		  }
		  return chartGraphs;
	  };
	  
	  service.getValueAxes = function(){
		  return [{
	          id: 'energyAxis',           
	          axisAlpha: 0,
	          gridAlpha:0,
	          position: 'left',
	          title: '每小時發電量(kWh)',
	          stackType: 'regular', 
	      },{
	    	  id: 'luxAxis',
	    	  axisAlpha: 0,
	          gridAlpha:0,
	          position: 'right',
	          title: '每小時日照值(W/m2)',
	      }];
	  };
	  
	  service.makeHourlyChart = function(chartData) {
		  var chartGraphs = service.getChartGraphs(chartData);
//		  var chartGraphs = [];
//		  for (var key in chartData[chartData.length-1]) {
//			  if (key !== 'date' && key !== 'lux') {
//				  chartGraphs.push({
//			          //alphaField: 'alpha',
//			          balloonText: '<span style="font-size:12px;">[[title]] in [[category]]<br><span style="font-size:20px;">[[value]]</span> [[additional]]</span>',
//			          fillAlphas: 0.6,
//			          lineAlpha: 0.4,
//			          //type: 'column',
//			          title: 'PVI(' + key + ')',
//			          valueField: key,
//			          valueAxis: 'energyAxis',
//			          dashLengthField: 'dashLengthColumn',
//			          type: 'smoothedLine',
//			      });
//			  }
//			  if (key === 'lux') {
//				  chartGraphs.push({
//			          //alphaField: 'alpha',
//					  bullet: 'round',
//			          balloonText: '<span style="font-size:12px;">[[title]] in [[category]]<br><span style="font-size:20px;">[[value]]</span> [[additional]]</span>',
//			          fillAlphas: 0,
//			          lineAlpha: 0.4,
//			          //type: 'line',
//			          title: 'LUX',
//			          valueField: key,
//			          valueAxis: 'luxAxis',
//			          dashLengthField: 'dashLengthColumn',
//			          type: 'smoothedLine',
//			      });
//			  }
//		  }

		  //var chart = $window.AmCharts.makeChart('amchart1', {
		  $window.AmCharts.makeChart('amchart1', {
			  type: 'serial',
			  addClassNames: true,
			  theme: 'light',
			  legend: {
			          equalWidths: false,
			          useGraphSettings: true,
			          valueAlign: 'left',
			          valueWidth: 120
			      },
			  balloon: {
			          adjustBorderColor: false,
			          horizontalPadding: 10,
			          verticalPadding: 8,
			          color: '#ffffff'
			      },
			  balloonDateFormat : 'JJ:NN',

			  dataProvider: chartData,
			  valueAxes: service.getValueAxes(),
//			  valueAxes: [{
//			          id: 'energyAxis',           
//			          axisAlpha: 0,
//			          gridAlpha:0,
//			          position: 'left',
//			          title: '每小時發電量(kWh)',
//			          stackType: 'regular', 
//			      },{
//			    	  id: 'luxAxis',
//			    	  axisAlpha: 0,
//			          gridAlpha:0,
//			          position: 'right',
//			          title: '每小時日照值(W/m2)',
//			      }],
			  startDuration: 1,
			  graphs: chartGraphs,
			  chartCursor: {
			          cursorAlpha: 0,
			          zoomable: false,
			          categoryBalloonDateFormat: 'JJ:NN',
			      },
			  dataDateFormat: 'YYYY-MM-DD JJ:NN:SS',
			  categoryField: 'date',
			  categoryAxis: {
			      dateFormats: [{
			          period:'hh', 
			          format:'JJ:NN'
			      }, {
			          period: 'JJ', 
			          format: 'JJ:NN'
			      }, {
			          period: 'DD',
			          format: 'MMM DD'
			      }, {
			          period: 'WW',
			          format: 'MMM DD'
			      }, {
			          period: 'MM',
			          format: 'MMM'
			      }, {
			          period: 'YYYY',
			          format: 'YYYY'
			      }],
				      parseDates: true,
				      minPeriod : 'hh',
				      gridPosition: 'start',
				      axisAlpha: 0,
				      tickLength: 0
			      },
			  panEventsEnabled: false,
		  });
		  //console.log('chartData length ' + chartData.length);
		  //console.log('last entry: ' + JSON.stringify(chartData[chartData.length-1]));
	  };
	  
	  this.makeDailyChart = function(chartData) {
		  var chartGraphs = service.getChartGraphs(chartData);
//		  var chartGraphs = [];
//		  for (var key in chartData[chartData.length-1]) {
//			  if (key !== 'date') {
//				  chartGraphs.push({
//			          alphaField: 'alpha',
//			          balloonText: '<span style="font-size:12px;">[[title]] in [[category]]:<br><span style="font-size:20px;">[[value]]</span> [[additional]]</span>',
//			          fillAlphas: 1,
//			          type: 'column',
//			          title: 'PVI(' + key + ')',
//			          valueField: key,
//			          valueAxis: 'energyAxis',
//			          dashLengthField: 'dashLengthColumn'
//			      });
//			  }
//		  }

		  //var chart = $window.AmCharts.makeChart('amchart1', {
		  $window.AmCharts.makeChart('amchart1', {
			  type: 'serial',
			  addClassNames: true,
			  theme: 'light',
			  legend: {
			          equalWidths: false,
			          useGraphSettings: true,
			          valueAlign: 'left',
			          valueWidth: 120
			      },
			  balloon: {
			          adjustBorderColor: false,
			          horizontalPadding: 10,
			          verticalPadding: 8,
			          color: '#ffffff'
			      },
			  dataProvider: chartData,
			  valueAxes: service.getValueAxes(),
			  startDuration: 1,
			  graphs: chartGraphs,
			  chartCursor: {
			          cursorAlpha: 0,
			          zoomable: false,
			          categoryBalloonDateFormat: 'MMM-DD',
			      },
			  dataDateFormat: 'YYYY-MM-DD',
			  categoryField: 'date',
			  categoryAxis: {
			          dateFormats: [{
			              period: 'DD',
			              format: 'DD'
			              }, {
			              period: 'WW',
			              format: 'MMM DD'
			              }, {
			              period: 'MM',
			              format: 'MMM'
			              }, {
			              period: 'YYYY',
			              format: 'YYYY'
			          }],
			          parseDates: true,
			          gridPosition: 'start',
			          axisAlpha: 0,
			          tickLength: 0
			      },
			  panEventsEnabled: false,
		  });
	  };
	  
	  service.makeMonthlyChart = function(chartData) {
		  var chartGraphs = service.getChartGraphs(chartData);
//		  var chartGraphs = [];
//		  for (var key in chartData[chartData.length-1]) {
//			  if (key !== 'date') {
//				  chartGraphs.push({
//			          alphaField: 'alpha',
//			          balloonText: '<span style="font-size:12px;">[[title]] in [[category]]:<br><span style="font-size:20px;">[[value]]</span> [[additional]]</span>',
//			          fillAlphas: 1,
//			          type: 'column',
//			          title: 'PVI(' + key + ')',
//			          valueField: key,
//			          valueAxis: 'energyAxis',
//			          dashLengthField: 'dashLengthColumn'
//			      });
//			  }
//		  }
		  //var chart = $window.AmCharts.makeChart('amchart1', {
		  $window.AmCharts.makeChart('amchart1', {
			  type: 'serial',
			  addClassNames: true,
			  theme: 'light',
			  legend: {
			          equalWidths: false,
			          useGraphSettings: true,
			          valueAlign: 'left',
			          valueWidth: 120
			      },
			  balloon: {
			          adjustBorderColor: false,
			          horizontalPadding: 10,
			          verticalPadding: 8,
			          color: '#ffffff'
			      },
			  dataProvider: chartData,
			  valueAxes: service.getValueAxes(),
			  startDuration: 1,
			  graphs: chartGraphs,
			  chartCursor: {
			          cursorAlpha: 0,
			          zoomable: false,
			          categoryBalloonDateFormat: 'YYYY-MM',
			      },
			  dataDateFormat: 'YYYY-MM',
			  categoryField: 'date',
			  categoryAxis: {
		          dateFormats: [{
			              period: 'DD',
			              format: 'DD'
		              }, {
			              period: 'WW',
			              format: 'MMM DD'
		              }, {
			              period: 'MM',
			              format: 'MMM'
		              }, {
			              period: 'YYYY',
			              format: 'YYYY'
			          }],
		          parseDates: true,
		          gridPosition: 'start',
		          axisAlpha: 0,
		          tickLength: 0,
		          minPeriod: 'MM'
			      },
			  panEventsEnabled: false,
		  });
	  };

  }]);
