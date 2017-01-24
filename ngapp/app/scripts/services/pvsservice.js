'use strict';

/**
 * @ngdoc service
 * @name pvsApp.PvsService
 * @description
 * # PvsService
 * Service in the pvsApp.
 */
angular.module('pvsApp')
  .service('PvsService', ['$http', function ($http) {
    // AngularJS will instantiate a singleton by calling "new" on this function
	var pvs = this;
	
	pvs.getSiteMeta = function() {
		return $http.get('views/test_pvs_meta.json');
	};
	  
	  
  }]);
