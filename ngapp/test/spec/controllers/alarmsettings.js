'use strict';

describe('Controller: AlarmsettingsCtrl', function () {

  // load the controller's module
  beforeEach(module('pvsApp'));

  var AlarmsettingsCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    AlarmsettingsCtrl = $controller('AlarmsettingsCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(AlarmsettingsCtrl.awesomeThings.length).toBe(3);
  });
});
