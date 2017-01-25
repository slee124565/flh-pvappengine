'use strict';

describe('Controller: EngexportCtrl', function () {

  // load the controller's module
  beforeEach(module('pvsApp'));

  var EngexportCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    EngexportCtrl = $controller('EngexportCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(EngexportCtrl.awesomeThings.length).toBe(3);
  });
});
