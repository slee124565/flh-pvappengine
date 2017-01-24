'use strict';

describe('Service: PvsService', function () {

  // load the service's module
  beforeEach(module('pvsApp'));

  // instantiate service
  var PvsService;
  beforeEach(inject(function (_PvsService_) {
    PvsService = _PvsService_;
  }));

  it('should do something', function () {
    expect(!!PvsService).toBe(true);
  });

});
