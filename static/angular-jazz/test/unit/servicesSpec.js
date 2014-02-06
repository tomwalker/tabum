'use strict';

/* jasmine specs for services go here */

describe('service', function() {

  var mockBackend, outcome, $TD, outcome2;

  beforeEach(module('tabum.services'));
  beforeEach(inject(function(_$httpBackend_, TurnData){
      $TD = TurnData;
      mockBackend = _$httpBackend_;

      this.addMatchers({
          // we need to use toEqualData because the Resource hase extra properties 
          // which make simple .toEqual not work.
          toEqualData: function(expect) {
              return angular.equals(expect, this.actual);
          }
      });

  }));

  // afterEach(function() {
  //   mockBackend.verifyNoOutstandingExpectation();
  //   mockBackend.verifyNoOutstandingRequest();
  // });

  it('should return turn data on GET request with game ID', 
	 inject(function($location) {
      mockBackend.expectGET(
		  'http://' + $location.host() + ':8000' + '/play/2/ag').
          respond({"id": 2});
      outcome = $TD.get({id: 2});
      mockBackend.flush();
      expect(outcome).toEqualData({"id": 2});
  }));

  it('should return "complete" on POST request with game ID and data', 
	 inject(function($location) {
      mockBackend.expectPOST(
		  'http://' + $location.host() + ':8000' + '/play/2/ag', 
          {id: 2, "property_changes": "dog", 
           "choice_outcome": "cat"}).respond(201, '');

      outcome2 = $TD.finish(
          {}, {id: 2, "property_changes": "dog", "choice_outcome": "cat"});
      mockBackend.flush();
      expect(outcome2).
          toEqualData({id: 2, "property_changes": "dog", "choice_outcome": "cat"});

  }));

});










