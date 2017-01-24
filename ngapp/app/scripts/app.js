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
	    })
	    .state({
	    	name: 'site',
	    	url: '/site',
	    	templateUrl: 'views/site.html',
	    	controller: 'SiteCtrl as site',
	        resolve: {
	            siteMeta: ['PvsService', function(PvsService) {
	                return PvsService.getSiteMeta();
	            }]
	        }
	    });
	
	    $urlRouterProvider.otherwise('/site');
	});
