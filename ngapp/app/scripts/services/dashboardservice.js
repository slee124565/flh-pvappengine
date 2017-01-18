'use strict';

/**
 * @ngdoc service
 * @name pvsApp.dashboardService
 * @description
 * # dashboardService
 * Service in the pvsApp.
 */
angular.module('pvsApp')
  .constant('apiBaseURL', '/')
  .service('dashboardService', ['$http','apiBaseURL',
    function ($http,apiBaseURL) {
	  var dashboardService = this;
	  
	  dashboardService.dbClean = function() {
		return $http.get(apiBaseURL + 'dbclean/');  
	  };
	  
	  dashboardService.dbInitialize = function() {
		  return $http.get(apiBaseURL + 'dbinit/');
	  };
  }]);

