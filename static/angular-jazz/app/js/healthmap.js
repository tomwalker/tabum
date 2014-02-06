"use strict";

var googleChart = googleChart || angular.module("google-chart",[]);

googleChart.directive("healthGoogleChart",function(){
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
            removeTeam: '=remt',
            hp: '=healthplayer',
            mapBefore: '=mapbefore',
            optionsBefore: '=obefore',
            teams: '=teams',
            effect_on_health: '=eoh'
        },
        link: function($scope, $elem, $attr){
        
            var googleChart = new google.visualization.GeoChart($elem[0]);
            
            google.visualization.events.addListener(googleChart, 'select', selectHandler);

            function selectHandler() {
                var rowNumber = googleChart.getSelection()[0]['row'];
                var countrySelected = $scope.data[rowNumber + 1][0];

                if ($scope.deployFieldResearcher === true){
                    if ($scope.effect_on_health.field_researchers_deployed.indexOf(countrySelected) === -1){
                        $scope.effect_on_health.field_researchers_deployed.push(countrySelected);
                        $scope.teams.push([countrySelected, 0]);
                        $scope.deployFieldResearcher = false;
                        $scope.hp.field_researchers = $scope.hp.field_researchers - 1;
                        $scope.options = $scope.optionsBefore;
                        $scope.data = $scope.mapBefore;
                        $scope.$apply();
                    }
                }

                if ($scope.deployControlTeam === true){
                    if ($scope.effect_on_health.control_teams_deployed.indexOf(countrySelected) === -1){
                        $scope.effect_on_health.control_teams_deployed.push(countrySelected);
                        $scope.teams.push([countrySelected, 1]);
                        $scope.deployControlTeam = false;
                        $scope.hp.control_team = $scope.hp.control_team - 1;
                        $scope.options = $scope.optionsBefore;
                        $scope.data = $scope.mapBefore;
                        $scope.$apply();
                    }
                }

                if ($scope.deployCureTeam === true){
                    if ($scope.effect_on_health.cure_teams_deployed.indexOf(countrySelected) === -1){
                        $scope.effect_on_health.cure_teams_deployed.push(countrySelected);
                        $scope.teams.push([countrySelected, 2]);
                        $scope.deployCureTeam = false;
                        $scope.hp.cure_teams = $scope.hp.cure_teams - 1;
                        $scope.options = $scope.optionsBefore;
                        $scope.data = $scope.mapBefore;
                        $scope.$apply();
                    }
                }

                if ($scope.removeTeam === true){
                    var cureLoc = $scope.effect_on_health.cure_teams_deployed.indexOf(countrySelected);
                    var controlLoc = $scope.effect_on_health.control_teams_deployed.indexOf(countrySelected);
                    var fieldLoc = $scope.effect_on_health.field_researchers_deployed.indexOf(countrySelected);

                    if (cureLoc >= 0){
                        $scope.effect_on_health.cure_teams_deployed.splice(cureLoc, 1);
                        for (var i = 0; i < $scope.teams.length; i++){
                            if ($scope.teams[i][0] === countrySelected && $scope.teams[i][1] == 2){
                                var teamCureIndex = i;
                            }
                        }
                        $scope.teams.splice(teamCureIndex, 1);
                        $scope.removeTeam = false;
                        $scope.hp.cure_teams = $scope.hp.cure_teams + 1;
                        googleChart.clearChart();
                        $scope.$apply();
                    }

                    if (controlLoc >= 0){
                        $scope.effect_on_health.control_teams_deployed.splice(controlLoc, 1);
                        for (var i = 0; i < $scope.teams.length; i++){
                            if ($scope.teams[i][0] === countrySelected && $scope.teams[i][1] == 1){
                                var teamControlIndex = i;
                            }
                        }
                        $scope.teams.splice(teamControlIndex, 1);
                        $scope.removeTeam = false;
                        $scope.hp.control_team = $scope.hp.control_team + 1;
                        googleChart.clearChart();
                        $scope.$apply();
                    }

                    if (fieldLoc >= 0){
                        $scope.effect_on_health.field_researchers_deployed.splice(fieldLoc, 1);
                        for (var i = 0; i < $scope.teams.length; i++){
                            if ($scope.teams[i][0] === countrySelected && $scope.teams[i][1] == 0){
                                var teamFieldIndex = i;
                            }
                        }
                        $scope.teams.splice(teamFieldIndex, 1);
                        $scope.removeTeam = false;
                        $scope.hp.field_researchers = $scope.hp.field_researchers + 1;
                        googleChart.clearChart();
                        $scope.$apply();
                    }

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
