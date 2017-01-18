'use strict';

/**
 * @ngdoc function
 * @name pvsApp.controller:DashboardCtrl
 * @description
 * # DashboardCtrl
 * Controller of the pvsApp
 */
angular.module('pvsApp')
  .controller('DashboardCtrl', ['dashboardService',
                                function (dashboardService) {
    var dashboard = this;
    
    dashboard.title = 'PVStation Dashboard';
    dashboard.description = 'Your Solar Green Power Solution';
    dashboard.header = 'System Configurations';
    
    dashboard.dbClean = function() {
    	dashboardService.dbClean().then(
    		function(response) {
    			console.log('dbClean success', response.data);
    		}, function(error) {
    			console.log('dbClean fail', error.status, error.statusText );
    		}
    	).catch(function(exception) {
    		console.log('dbClean exception', exception);
    	});
    	
    };
    
    dashboard.dbInit = function() {
    	dashboardService.dbInit().then(
    		function(response){
    			console.log('dbInit success', response.data);
    		},function(error){
    			console.log('dbInit fail', error.status, error.statusText);
    		}
    		
    	).catch(function(exception){
    		console.log('dbInit exception', exception);
    	});
    };
    
  }]);
