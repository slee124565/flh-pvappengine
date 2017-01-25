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
	    })
	    .state({
	    	name: 'basicmeta',
	    	url: '/basicmeta',
	    	templateUrl: 'views/basicmeta.html',
	    	controller: 'BasicMeta as meta'
//	        resolve: {
//	            siteMeta: ['PvsService', function(PvsService) {
//	                return PvsService.getBasicMeta();
//	            }]
//	        }
	    })
	    .state({
	    	name: 'engexport',
	    	url: '/engexport',
	    	templateUrl: 'views/engexport.html',
	    	controller: 'EngExport as export'
//	        resolve: {
//	            siteMeta: ['PvsService', function(PvsService) {
//	                return PvsService.getBasicMeta();
//	            }]
//	        }
	    })
	    .state({
	    	name: 'alarmsettings',
	    	url: '/alarmsettings',
	    	templateUrl: 'views/alarmsettings.html',
	    	controller: 'AlarmSettings as alarm'
//	        resolve: {
//	            siteMeta: ['PvsService', function(PvsService) {
//	                return PvsService.getSiteMeta();
//	            }]
//	        }
	    })
;
	
	    $urlRouterProvider.otherwise('/site');
	});
