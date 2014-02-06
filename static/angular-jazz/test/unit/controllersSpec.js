'use strict';

describe('Controllers', function(){
    var $scope, ctrl, x;
	var mockData = '{ "next_to_play": "V", "countries": { "china": { "population": { "healthy": 1400000000, "infected": 10, "dead": 1 }, "climate": "TEMPERATE", "healthcare": 4, "land_links": [ "india", "nepal", "thailand", "korea", "japan" ], "air_links": [ "USA", "japan", "spain" ], "sea_links": [ "australia", "britain", "germany" ] }, "paraguay": { "population": { "healthy": 1000000, "infected": 0, "dead": 0 }, "climate": "TROPICAL", "healthcare": 7, "land_links": [ "india", "nepal", "thailand", "korea", "japan" ], "air_links": [ "USA", "spain" ], "sea_links": [ "australia", "britain", "germany" ] }, "ireland": { "population": { "healthy": 432400, "infected": 488390, "dead": 90907930 }, "climate": "TEMPERATE", "healthcare": 7, "land_links": [ "UK" ], "air_links": [ "USA", "spain", "china" ], "sea_links": [ "australia", "britain", "germany" ] } }, "virus_player": { "agent": "HIV", "points": 5, "shift": 1, "infectivity": 4, "lethality": 7, "resistance": [ "hot", "drug", "exam" ], "infected_countries": [ "australia", "UK", "Indonesia" ], "air_spread": 3, "land_spread": 1, "sea_spread": 3 }, "health_player": { "points": 60, "field_researchers": { "africa": 1, "china": 3 }, "control_teams": { "UK": 1, "iceland": 3 }, "virus_understanding": 43, "cure_research": 20, "public_awareness": 70, "disease_control": 11 } }';
    beforeEach(module('tabum'));

    beforeEach(inject(function(_$httpBackend_, $rootScope, $controller) {
		this.addMatchers({
          toEqualData: function(expect) {
              return angular.equals(expect, this.actual);
          }
      });

    }));
	
	describe('get controllers', function(){
		var TD, mockBackend;
		beforeEach(inject(function(
			$rootScope, $location, $controller, _$httpBackend_, TurnData){
			TD = TurnData;
			mockBackend = _$httpBackend_;
			$scope = $rootScope.$new();
			mockBackend.expectGET(
				'http://' + $location.host() + ':8000' + '/play/2/ag')
				.respond({'data': mockData});
		}));

		beforeEach(inject(function($browser, $location){
			$browser.url("http://" + $location.host() + ":8000/play/2/");
			$location.path("http://" + $location.host() + ":8000/play/2/")
		}));
		
		it('should display the received data', 
		   inject(function($controller, $location) {

			   ctrl = $controller('RESTController', {
				   $scope: $scope,
			   });
			
			   mockBackend.flush();
			   expect($scope.data.next_to_play).toEqual("V");
		}));

	});

	describe('POST controllers', function(){
		var mockBackend;
		beforeEach(inject(function(
			$rootScope, $location, $controller, _$httpBackend_, TurnData){
			mockBackend = _$httpBackend_;
			$scope = $rootScope.$new();
			mockBackend.expectGET(
				'http://' + $location.host() + ':8000' + '/play/2/ag')
				.respond({"data": mockData});
		}));

		beforeEach(inject(function($browser, $location){
			$browser.url("http://127.0.0.1:8000/play/2/");
			$location.path("http://" + $location.host() + ":8000/play/2/")
		}));

		it('should post stuff', inject(function($controller, 
												$location, $rootScope) {
			mockBackend.expectPOST(
				'http://' + $location.host() + ':8000' + '/play/2/ag',
				{id: 2, 'property_changes': 'test', 'choice_outcome': 'test2'})
				.respond({status: 201, data: 'co'});
			ctrl = $controller('RESTController', {
				$scope: $scope,
			});
			mockBackend.flush();
			x = $scope.endTurn();
			mockBackend.flush();
			expect(x['data']).toBe('co');
		}));
		
	});

	describe('Point handlers', function(){
		var mockBackend;
		beforeEach(inject(function(
			$rootScope, $location, $controller, 
			_$httpBackend_, TurnData){
			mockBackend = _$httpBackend_;
			$scope = $rootScope.$new();
			mockBackend.expectGET(
				'http://' + $location.host() + ':8000' + '/play/2/ag')
				.respond({'data' : mockData});
		}));

		beforeEach(inject(function($browser, $location){
			$browser.url("http://127.0.0.1:8000/play/2/");
			$location.path("http://" + $location.host() + ":8000/play/2/")
		}));

		it('should have points', inject(function($controller, 
												$location, $rootScope) {

			ctrl = $controller('RESTController', {
				$scope: $scope,
			});
			mockBackend.flush();
			expect($scope.next_to_play).toEqual("V");
			expect($scope.virus.points).toEqual(5);
		}));

		it('should increase property, decrease points', 
		   inject(function($controller, $rootScope) {

               ctrl = $controller('RESTController', {
                   $scope: $scope,
               });
			   $scope.increasePoints("infectivity");
               mockBackend.flush();
               expect($scope.virus.points).toEqual(4);
			   expect($scope.virus.infectivity).toEqual(5);
           }));

		it('should + then - properties and points', 
		   inject(function($controller, $rootScope) {
			   ctrl = $controller('RESTController', {
                   $scope: $scope,
               });
               ctrl.increasePoints("infectivity");
               mockBackend.flush();
               expect($scope.virus.points).toEqual(4);
               expect($scope.virus.infectivity).toEqual(5);
			   ctrl.decreasePoints("infectivity");
			   mockBackend.flush();
               expect($scope.virus.points).toEqual(5);
               expect($scope.virus.infectivity).toEqual(4);
			   ctrl.decreasePoints("infectivity");
			   mockBackend.flush();
			   expect($scope.virus.points).toEqual(5);
               expect($scope.virus.infectivity).toEqual(4);
           }));
		
	});

});
