'use strict';

describe('Controller: BasicmetaCtrl', function () {

  // load the controller's module
  beforeEach(module('pvsApp'));

  var BasicmetaCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    BasicmetaCtrl = $controller('BasicmetaCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(BasicmetaCtrl.awesomeThings.length).toBe(3);
  });
});
