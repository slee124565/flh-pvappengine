'use strict';

/**
 * @ngdoc function
 * @name pvsApp.controller:SiteCtrl
 * @description
 * # SiteCtrl
 * Controller of the pvsApp
 */
angular.module('pvsApp')
  .controller('SiteCtrl', ['siteMeta', 'AmchartsService', function (siteMeta,AmchartsService) {
	var site = this;
	site.meta = siteMeta.data;
	site.meta.title = '太陽能發電系統';
	site.meta.header = '即時資訊';
	site.currentEng = 12.34;
	site.pyrheliometer = 11.2;
	//console.log(site.meta);
	
	site.makeHourlyChart = function(){
		AmchartsService.makeHourlyChart(site.meta.amchart_hourly_data);
	};
	
	site.makeDailyChart = function() {
		AmchartsService.makeDailyChart(site.meta.amchart_daily_data);
	};
	
	site.makeMonthlyChart = function() {
		AmchartsService.makeMonthlyChart(site.meta.amchart_monthly_data);
	};

	site.makeHourlyChart();
  }]);
