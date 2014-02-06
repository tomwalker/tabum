"use strict";
 
var googleChart = googleChart || angular.module("google-chart",[]);
 
googleChart.directive("googleChart",function(){
    return{
        restrict : "A",
		scope : {
			data: '=data',
			options: '=mapoptions',
			selected: '=selected',
			first_turn: '=first',
			health_teams: '=hteams',
			deployFieldResearcher: '=dfr',
			deployControlTeam: '=dct',
			deployCureTeam: '=drt',
			hp: '=healthplayer',
			effect_on_health: '=eoh'
		},
        link: function($scope, $elem, $attr){
     
            var googleChart = new google.visualization.GeoChart($elem[0]);
			
			google.visualization.events.addListener(googleChart, 'select', selectHandler);

			function selectHandler() {
                var rowNumber = googleChart.getSelection()[0]['row'];
				
				if ($scope.first_turn === true){
					$scope.selected = {
						firstTurnChoice: $scope.data[rowNumber + 1][0]
					};
					$scope.$apply();
				}

				if ($scope.deployFieldResearcher === true){
					$scope.effect_on_health.field_researchers_deployed.push($scope.data[rowNumber + 1][0]);
					$scope.deployFieldResearcher = false;
					$scope.hp.field_researchers = $scope.hp.field_researchers - 1;
					$scope.$apply();
				}

				if ($scope.deployControlTeam === true){
					$scope.effect_on_health.control_teams_deployed.push($scope.data[rowNumber + 1][0]);
					$scope.deployControlTeam = false;
					$scope.hp.control_team = $scope.hp.control_team - 1;
					$scope.$apply();
				}

				if ($scope.deployCureTeam === true){
					$scope.effect_on_health.cure_teams_deployed.push($scope.data[rowNumber + 1][0]);
					$scope.deployCureTeam = false;
					$scope.hp.cure_teams = $scope.hp.cure_teams - 1;
					$scope.$apply();
				}				
                
            }

            // watch the data and redraw if changes. Done so that map reloads after GET has completed
            $scope.$watch('data', function(v) {

                var data = google.visualization.arrayToDataTable(v);

                googleChart.draw(data, $scope.options);

            }, true);

        }
    }
});



