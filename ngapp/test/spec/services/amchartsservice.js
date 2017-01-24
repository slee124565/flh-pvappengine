'use strict';

describe('Service: AmchartsService', function () {

  // load the service's module
  beforeEach(module('pvsApp'));

  // instantiate service
  var AmchartsService;
  beforeEach(inject(function (_AmchartsService_) {
    AmchartsService = _AmchartsService_;
  }));

  it('should do something', function () {
    expect(!!AmchartsService).toBe(true);
  });

});
