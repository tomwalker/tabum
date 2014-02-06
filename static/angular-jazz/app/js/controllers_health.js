google.setOnLoadCallback(function () {    
    angular.bootstrap(document.body, ['tabum']);
});

google.load('visualization', '1', {packages: ['geochart', 'orgchart']});


var app = app || angular.module('tabum', 
                                ['tabum.services', 'ngCookies', 
                                 'ui.bootstrap', 'google-chart']);

app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
});

app.config(['$httpProvider', function ($httpProvider) {
    $httpProvider.defaults.useXDomain = true;
    delete $httpProvider.defaults.headers.common['X-Requested-With'];
}]);

app.run(function ($http, $cookies) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
});


app.controller('RESTController', ['$scope', '$location', '$timeout', 'TurnData', 
  function ($scope, $location, $timeout, TurnData) {
      
      $scope.loc = function() {
          var parts = $location.absUrl().split("/");
          return parts[parts.length - 2];
      };

      $scope.news = [];

      $scope.mapDataPlain = [
        ['Country']
      ];

      $scope.healthMapDisplayOptionsPlain = {
        region: 'world',
        displayMode: 'regions',
        colorAxis: {colors: ['green', 'blue', 'red']}  // colours for markers
      };

      $scope.mapDataHealthPlayerTeams = [
          ['Country', ''],
          ['', 0],
          ['', 1],
          ['', 2]
      ];

      $scope.mapDetectedInfection = [
          ['Country', 'Infected %', 'Dead %'],
          ['', 0, 0]
      ];

      $scope.healthMapDisplayOptionsTeams = {
          region: 'world',
          displayMode: 'markers',
          sizeAxis: {minSize:'9', maxSize:'16', minValue:'0', maxValue:'2'},
          enableRegionInteractivity: false,
          legend: 'none',
          tooltip: {trigger: 'none'},
          colorAxis: {colors: ['green', 'blue', 'red']}  // colours for markers
      };

      $scope.healthMapDisplayOptionsDetected = {
          region: 'world',
          displayMode: 'regions',
          enableRegionInteractivity: true,
          legend: 'none',
          tooltip: {trigger: 'focus'},
          colorAxis: {colors: ['green','yellow', 'orange', 'red']}
      };


      $scope.mapDisplayedHealth = $scope.mapDataPlain;

      $scope.healthTechTreeData = new google.visualization.DataTable();
      $scope.healthTechTreeData.addColumn('string', 'property');
      $scope.healthTechTreeData.addColumn('string', 'parent');
      $scope.healthTechTreeData.addColumn('string', 'toolTip');


      $scope.dataRetrieve = function() {
          TurnData.get({id: $scope.loc()}, function (data){
              var extracted = angular.fromJson(data.turn_data);
              $scope.next_to_play = extracted.next_to_play;
              $scope.countries = extracted.countries;
              $scope.virus = extracted.virus_player;
              $scope.health = extracted.health_player;
              $scope.first_turn = extracted.first_turn;
              $scope.virusTechTree = extracted.virus_tech_tree;
              $scope.healthTechTree = extracted.health_tech_tree;
              $scope.turn_question = extracted.turn_question;
              $scope.news = extracted.news;
              $scope.detected_infection = extracted.detected_infection;

              $scope.story = extracted.turn_question['story'];
              $scope.question = extracted.turn_question['question'];
              $scope.answer_choices = extracted.turn_question['choices'];
              $scope.answer_choices_value = extracted.turn_question['choice_values']

              // after data has pulled, populate the map
              for (var key in $scope.countries) {
                  var obj = $scope.countries[key];
                  var infectedPercent = Math.round((obj.population.infected / 
                                         (obj.population.infected + obj.population.healthy)) * 100);

                  var deadPercent = Math.round((obj.population.dead / 
                                                (obj.population.infected + obj.population.healthy + 
                                                obj.population.dead)) * 100);
                  
                  $scope.mapDataPlain.push([key]);
                  if ($scope.detected_infection.indexOf(key) >= 0) {
                      $scope.mapDetectedInfection.push([key, infectedPercent, deadPercent]);
                  }
              }
              
              var i = 0;
              var treePositions = [];
              // create the health tech tree for the first time
              for (var key in $scope.healthTechTree) {
                  var obj = $scope.healthTechTree[key];
                  if (obj.parent === 0){
                      if (obj.active === true){
                          $scope.healthTechTreeData.addRow([{v: obj.property, f: obj.display_active }, 
                                                            '', key]);
                          $scope.healthTechTree[key]['already-active'] = true;
                      } else{
                          $scope.healthTechTreeData.addRow([{v: obj.property, f: obj.display_inactive }, 
                                                            '', key]);
                      }
                  } else {
                      if (obj.active === true){
                          $scope.healthTechTreeData.addRow([{v: obj.property, f: obj.display_active }, 
                                                            obj.parent, key]);
                          $scope.healthTechTree[key]['already-active'] = true;
                      } else{
                          $scope.healthTechTreeData.addRow([{v: obj.property, f: obj.display_inactive }, 
                                                            obj.parent, key]);
                      }
                  }
                  $scope.healthTechTree[key]['treePosition'] = i;
                  treePositions.push(obj.property);
                  i++;
              } // end of tech tree for loop

              $scope.healthTechTree['treePositions'] = treePositions;

              $scope.mapDisplayedHealth = $scope.mapDataHealthPlayerTeams;
              $scope.healthMapDisplayOptions = $scope.healthMapDisplayOptionsTeams;

          }); // end of the TurnData call

    
      }; // end of dataRetrieve


      // when other maps are ready, reveal - known infected, plain, teams etc.
      // Maybe combine teams with known and remove toggle all together?
      $scope.toggleMap = function () {
          var mapList = [$scope.mapDetectedInfection, $scope.mapDataHealthPlayerTeams];
          var optionsList =[ // ensure order of options is same as mapList
              $scope.healthMapDisplayOptionsDetected,
              $scope.healthMapDisplayOptionsTeams
          ];

          var index = mapList.indexOf($scope.mapDisplayedHealth);

          if (index == mapList.length - 1){
              $scope.mapDisplayedHealth = mapList[0];
              $scope.healthMapDisplayOptions = optionsList[0];
          } else {
              $scope.mapDisplayedHealth = mapList[index + 1];
              $scope.healthMapDisplayOptions = optionsList[index + 1];
          }
          
      };


      $scope.storechoice = function(ch) {
          $scope.choice = ch;
      };

      $scope.selected = '';

      $scope.healthTeams = '';

      $scope.deployFieldResearcher = false;
      $scope.deployControlTeam = false;
      $scope.deployCureTeam = false;
      $scope.removeTeam = false;
	  $scope.finalSpinner = false;

      $scope.buyTeam = function(type) {
          if ($scope.health.points > 0){
              $scope.health.points--;
              $scope.health[type]++;
          }
      };

      $scope.effect_on_health = {
          field_researchers: 0,
          field_researchers_deployed: [],
          control_teams: 0,
          control_teams_deployed: [],
          cure_teams: 0,
          cure_teams_deployed: [],
          virus_understanding: 0,
          cure_research: 0,
          public_awareness: 0,
          disease_control: 0
      };

      $scope.$watchCollection('[deployFieldResearcher, deployControlTeam, deployCureTeam]',
                  function(newCollection) {
                      if (newCollection.indexOf(true) >= 0){
                          $scope.mapBefore = $scope.mapDataHealthPlayerTeams;
                          $scope.optionsBefore = $scope.healthMapDisplayOptionsTeams;
                          $scope.healthMapDisplayOptions = $scope.healthMapDisplayOptionsPlain;
                          $scope.mapDisplayedHealth = $scope.mapDataPlain;
                      } else {              // if player changes mind, show where teams are
                          $scope.mapDisplayedHealth = $scope.mapDataHealthPlayerTeams;
                          $scope.healthMapDisplayOptions = $scope.healthMapDisplayOptionsTeams;
                      }
      }, true);

      $scope.ticker = 0;

      $scope.tickingOver = function () {
          step = $timeout(function() {
              var newsLength = $scope.news.length;
              if ($scope.ticker == (newsLength - 1)){
                  $scope.ticker = 0;
              } else{
                  $scope.ticker = $scope.ticker + 1;
              }
              $scope.tickingOver();
          }, 8500);
      };

      $scope.tickingOver();

      $scope.endTurnFinal = function() {
		  $scope.finalSpinner = true;
          if ($scope.first_turn === true){
              TurnData.finish({id: parseInt($scope.loc()),
                               "virus_player": angular.toJson($scope.virus),
                               "virus_tech": angular.toJson($scope.virusTechTree),
                               "health_player": angular.toJson($scope.health),
                               "health_tech": angular.toJson($scope.healthTechTree),
                               "starting_from": $scope.selected["firstTurnChoice"],
                               "choice_outcome": $scope.choice,
                               "change": angular.toJson($scope.effect_on_health)
                              }, function(u, getResponseHeaders){
                                  $timeout(function() {
                                      window.location.reload();
                                  }, 3000);
                              });
          } else {
              TurnData.finish({id: parseInt($scope.loc()),
                               "virus_player": angular.toJson($scope.virus),
                               "virus_tech": angular.toJson($scope.virusTechTree),
                               "health_player": angular.toJson($scope.health),
                               "health_tech": angular.toJson($scope.healthTechTree),
                               "choice_outcome": angular.toJson($scope.choice),
                               "change": angular.toJson($scope.effect_on_health)
                              }, function(u, getResponseHeaders){
                                  $timeout(function() {
                                      window.location.reload();
                                  }, 3000);
                              });
          }  
      
      };

      $scope.loadData = $scope.dataRetrieve();

}]); // end of controller


