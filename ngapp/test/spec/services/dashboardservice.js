'use strict';

describe('Service: dashboardService', function () {

  // load the service's module
  beforeEach(module('pvsApp'));

  // instantiate service
  var dashboardService;
  beforeEach(inject(function (_dashboardService_) {
    dashboardService = _dashboardService_;
  }));

  it('should do something', function () {
    expect(!!dashboardService).toBe(true);
  });

});
