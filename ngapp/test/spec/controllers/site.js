'use strict';

describe('Controller: SiteCtrl', function () {

  // load the controller's module
  beforeEach(module('pvsApp'));

  var SiteCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    SiteCtrl = $controller('SiteCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(SiteCtrl.awesomeThings.length).toBe(3);
  });
});
