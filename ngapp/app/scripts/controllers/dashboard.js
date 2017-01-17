'use strict';

/**
 * @ngdoc function
 * @name pvsApp.controller:DashboardCtrl
 * @description
 * # DashboardCtrl
 * Controller of the pvsApp
 */
angular.module('pvsApp')
  .controller('DashboardCtrl', function () {
    var dashboard = this;
    
    dashboard.title = 'PVStation Dashboard';
    dashboard.description = 'Your Solar Green Power Solution';
    dashboard.header = 'System Configurations';
    
  });
