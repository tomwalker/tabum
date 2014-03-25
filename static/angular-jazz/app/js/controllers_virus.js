google.setOnLoadCallback(function () {
    angular.bootstrap(document.body, ['tabum']);
});

google.load('visualization', '1', 
            {packages: ['geochart', 'orgchart']});


var app = app || angular.module('tabum', 
                                ['tabum.services', 'ngCookies', 
                                 'ui.bootstrap', 'google-chart']);

app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
});

app.config(['$routeProvider', '$httpProvider', 
            function ($routeProvider, $httpProvider) {
                $httpProvider.defaults.useXDomain = true;
                delete $httpProvider.defaults.headers.common['X-Requested-With'];
            }]);

app.run(function ($http, $cookies) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
});


app.controller('VirusController', ['$scope', '$location', '$q', '$timeout', 'TurnData', 
  function ($scope, $location, $q, $timeout, TurnData) {
                    
      $scope.loc = function() {
          var parts = $location.absUrl().split("/");
          return parts[parts.length - 2];
      };


      $scope.dataRetrieve = function() {
          TurnData.get({id: $scope.loc()}, function (data){
              var extracted = angular.fromJson(data.turn_data);
              $scope.countries = extracted.countries;
              $scope.virus = extracted.virus_player;
              $scope.health = extracted.health_player;
              $scope.first_turn = extracted.first_turn;
              $scope.virusTechTree = extracted.virus_tech_tree;
              $scope.healthTechTree = extracted.health_tech_tree;
              $scope.turn_question = extracted.turn_question;

              $scope.story = extracted.turn_question['story'];
              $scope.question = extracted.turn_question['question'];
              $scope.answer_choices = extracted.turn_question['choices'];
              $scope.answer_choices_value = extracted.turn_question['choice_values'];

              // after data has pulled, populate the map
              for (var key in $scope.countries) {
                  var obj = $scope.countries[key];
                  var infectedPercent = Math.round((obj.population.infected / 
                                                    (obj.population.infected + obj.population.healthy)) * 100);

                  var deadPercent = Math.round((obj.population.dead / 
                                                (obj.population.infected + obj.population.healthy + 
                                                 obj.population.dead)) * 100);
                  
                  $scope.mapDataInfectedPercent.push([key, infectedPercent, obj.population.dead]);
                  $scope.mapDataDead.push([key, deadPercent, obj.population.dead]);
                  $scope.mapDataInfected.push([key, obj.population.infected, obj.population.healthy]);
              }

              var i = 0;
              var treePositions = [];

              // create the virus tech tree for the first time
              for (var key in $scope.virusTechTree) {
                  var obj = $scope.virusTechTree[key];
                  
                  if (obj.parent === 0){
                      if (obj.active === true){
                          $scope.techTreeData.addRow([{v: obj.property, f: obj.display_active }, 
                                                      '', key]);
                          $scope.virusTechTree[key]['already-active'] = true;
                      } else{
                          $scope.techTreeData.addRow([{v: obj.property, f: obj.display_inactive }, 
                                                      '', key]);
                      }
                  } else {
                      if (obj.active === true){
                          $scope.techTreeData.addRow([{v: obj.property, f: obj.display_active }, 
                                                      obj.parent, key]);
                          $scope.virusTechTree[key]['already-active'] = true;
                      } else{
                          $scope.techTreeData.addRow([{v: obj.property, f: obj.display_inactive }, 
                                                      obj.parent, key]);
                      }
                  }
                  $scope.virusTechTree[key]['treePosition'] = i;
                  treePositions.push(obj.property);
                  i++;
              } // end of virus tech tree for loop

              $scope.virusTechTree['treePositions'] = treePositions;

          }); // end of the TurnData call

          
      };

      $scope.mapDataInfectedPercent = [
          ['Country', 'Infected %', 'dead']
      ];

      $scope.mapDataDead = [
          ['Country', 'Dead %', 'dead number']
      ];

      $scope.mapDataInfected = [
          ['Country', 'Infected', 'Healthy']
      ];

      $scope.techTreeData = new google.visualization.DataTable();
      $scope.techTreeData.addColumn('string', 'property');
      $scope.techTreeData.addColumn('string', 'parent');
      $scope.techTreeData.addColumn('string', 'toolTip');

      $scope.mapDisplayed = $scope.mapDataInfectedPercent;
      $scope.mapDisplayOptions = {colorAxis: 
                                  {colors: ['green','yellow', 'orange', 'red'], }
                                 };

      $scope.toggleMap = function () {
          var mapList = [$scope.mapDataDead, $scope.mapDataInfectedPercent, $scope.mapDataInfected];
          var optionsList =[
              {colorAxis: {minValue: 1, maxValue: 99, colors: ['white', 'yellow', '#FF0000', '#C00000', '#600000', 'black']}, legend: 'none'}, // dead
              {colorAxis: {colors: ['green','yellow', 'orange', 'red']}}, // percent infected
              {colorAxis: {colors: ['green','yellow', 'orange', 'red']}, legend: 'none'} // whole infected
          ];                    // ensure order of options is same as mapList
          
          var index = mapList.indexOf($scope.mapDisplayed);
          
          if (index == mapList.length - 1){
              $scope.mapDisplayed = mapList[0];
              $scope.mapDisplayOptions = optionsList[0];
          } else {
              $scope.mapDisplayed = mapList[index + 1];
              $scope.mapDisplayOptions = optionsList[index + 1];
          }
          
      };
      $scope.finalSpinner = false;

      $scope.endTurnFinal = function() {
          $scope.finalSpinner = true;         
          if ($scope.first_turn === true){
              TurnData.finish({id: parseInt($scope.loc(), 10),
                               "virus_player": angular.toJson($scope.virus),
                               "virus_tech": angular.toJson($scope.virusTechTree),
                               "health_player": angular.toJson($scope.health),
                               "health_tech": angular.toJson($scope.healthTechTree),
                               "starting_from": $scope.selected["firstTurnChoice"],
                               "choice_outcome": $scope.choice,
                               "change": angular.toJson($scope.effect_on_virus)
                              }, function(){
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
                               "change": angular.toJson($scope.effect_on_virus)
                              }, function(){
                                  $timeout(function() {
                                      window.location.reload();
                                  }, 3000);
                              });
          }
          
          
          
      };


      $scope.storechoice = function(ch) {
          $scope.choice = ch;
      };

      $scope.selected = '';

      // running total used when ending turn
      $scope.effect_on_virus = {
          infectivity: 0,
          lethality: 0,
          shift: 0,
          air_spread: 0,
          land_spread: 0,
          sea_spread: 0
      };

      $scope.$watchCollection('[deployFieldResearcher, deployControlTeam, deployCureTeam]', function(x) {
          if (x.indexOf(true) >= 0){
              $scope.mapBefore = $scope.mapDisplayedHealth;
              $scope.optionsBefore = $scope.healthMapDisplayOptions;
              $scope.healthMapDisplayOptions = $scope.healthMapDisplayOptionsPlain;
              $scope.mapDisplayedHealth = $scope.mapDataPlain;
          }
      }, true);

      $scope.loadData = $scope.dataRetrieve();

}]); // end of controller
