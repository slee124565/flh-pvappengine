'use strict';

/**
 * @ngdoc overview
 * @name pvsApp
 * @description
 * # pvsApp
 *
 * Main module of the application.
 */
angular
  .module('pvsApp', [
    'ngResource',
    'ui.router'
	]).config(function($stateProvider, $urlRouterProvider){
	    $stateProvider
	    .state({
	        name: 'dashboard',
	        url: '/dashboard',
	        templateUrl: 'views/dashboard.html',
	        controller: 'DashboardCtrl as dashboard',
//	        resolve: {
//	            configObj: ['SettingsService', function(SettingsService) {
//	                return SettingsService.getSiteConfig();
//	            }]
//	        }
	    });
	
	    $urlRouterProvider.otherwise('/dashboard');
	});
