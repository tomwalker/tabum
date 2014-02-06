"use strict";
 
var googleChart = googleChart || angular.module("google-chart",[]);
 
googleChart.directive("healthTechTree", function(){
    return{
        restrict : "A",
        scope : {
            data: '=data',
            htech: '=htech',
            points: '=points',
            effectOn: '=effect'
            
        },
        link: function($scope, $elem, $attr){
            var healthGoogleOrgChart = new google.visualization.OrgChart($elem[0]);
            var activatedThisTurnHealth = [];
            var activatedDict = {};
            
            google.visualization.events.addListener(healthGoogleOrgChart, 'select', selectHandlerHealth);

            function removeNode(node, nodeKey, nodeRowNumber) {
                var node_index = activatedThisTurnHealth.indexOf(nodeKey);
                activatedThisTurnHealth.splice(node_index, 1);

                $scope.htech[nodeKey.toLowerCase()]['active'] = false;

                $scope.effectOn.field_researchers = $scope.effectOn.field_researchers - 
                    $scope.htech[nodeKey]['effect_on_field_researchers'];
                $scope.effectOn.control_teams = $scope.effectOn.control_teams - 
                    $scope.htech[nodeKey]['effect_on_control_teams'];
                $scope.effectOn.cure_teams = $scope.effectOn.cure_teams - 
                    $scope.htech[nodeKey]['effect_on_cure_teams'];
                $scope.effectOn.virus_understanding = $scope.effectOn.virus_understanding - 
                    $scope.htech[nodeKey]['effect_on_virus_understanding'];
                $scope.effectOn.cure_research = $scope.effectOn.cure_research - 
                    $scope.htech[nodeKey]['effect_on_cure_research'];
                $scope.effectOn.public_awareness = $scope.effectOn.public_awareness - 
                    $scope.htech[nodeKey]['effect_on_public_awareness'];
                $scope.effectOn.disease_control = $scope.effectOn.disease_control - 
                    $scope.htech[nodeKey]['effect_on_disease_control'];

                $scope.points = $scope.points + $scope.htech[nodeKey]['cost'];

                $scope.data.removeRow(nodeRowNumber);

                if (node.parent === 0){
                    var rowData = [
                        [{v: node.property, f: node.display_inactive }, 
                         '', node.property]
                    ];                                      
                } else{
                    var rowData = [
                        [{v: node.property, f: node.display_inactive }, 
                         node.parent, 
                         node.property]
                    ];
                }
                $scope.data.insertRows(nodeRowNumber, rowData); 
                healthGoogleOrgChart.setSelection();
                //console.log($scope.data);
            }
            

            function requiredCheck(selectedNode, allNodes) {
                for (var i = 0; i < activatedThisTurnHealth.length; i++){
                    // console.log(allNodes[activatedThisTurnHealth[i]]['requires']);
                    // if item requires currently selected node
                    if (allNodes[activatedThisTurnHealth[i]]['requires'] !== '') {
                        if (allNodes[activatedThisTurnHealth[i]]['requires'].indexOf(selectedNode.property) >= 0){
                            var nodeToRemove = allNodes[activatedThisTurnHealth[i]];
                            removeNode(allNodes[activatedThisTurnHealth[i]],
                                       activatedThisTurnHealth[i], activatedDict[activatedThisTurnHealth[i]]);
                            requiredCheck(nodeToRemove, allNodes);
                        }
                    }
                }
            } // end of requiredCheck

            function selectHandlerHealth() {

                if (healthGoogleOrgChart.getSelection().length !== 0){
                    var nodeRowNumber = healthGoogleOrgChart.getSelection()[0]['row'];
                    var allNodes = $scope.htech;
					var nodeKey = allNodes['treePositions'][nodeRowNumber];
                    var selectedNode = allNodes[nodeKey.toLowerCase()];

                    if (selectedNode['selectable'] === true) {

                        // if it is, check if its in list of nodes activated during this turn and
                        // deactivate it by removing it from list, setting active false, removing
                        // points from effectOn, adding cost back to point and redrawing node

                        if (activatedThisTurnHealth.indexOf(selectedNode['property']) >= 0) {

                            removeNode(selectedNode, nodeKey, nodeRowNumber);
                            //console.log(selectedNode);
                            // for each item in activatedThisTurn
                            requiredCheck(selectedNode, allNodes);
                            // change to inactive, refund points, remove effect_on
                            
                        } else {
                            // if not, check if required nodes are active
                            var requiredNodes = selectedNode.requires;  // list of required
                            var allBelowActive = 0;
                            for (var i = 0; i < requiredNodes.length; i++) {
                                var x = requiredNodes[i];
                                if ($scope.htech[x]['active'] === false){
                                    allBelowActive++;
                                };
                            }
                            // if all necessary are active, check if enough points are
                            // available
                            if (allBelowActive === 0){ 
                                var cost = $scope.htech[nodeKey]['cost'];
                                // if enough points are available, remove cost from points,
                                // set node as active, add points to effectOn, add to the
                                // activatedThisTurnHealth list, set it to active then change node
                                // to display active
                                if (cost <= $scope.points){
                                    $scope.points = $scope.points - cost;
                                    $scope.htech[nodeKey]['active'] = true;

                                    $scope.effectOn.field_researchers = $scope.effectOn.field_researchers + 
                                        $scope.htech[nodeKey]['effect_on_field_researchers'];
                                    $scope.effectOn.control_teams = $scope.effectOn.control_teams + 
                                        $scope.htech[nodeKey]['effect_on_control_teams'];
                                    $scope.effectOn.cure_teams = $scope.effectOn.cure_teams + 
                                        $scope.htech[nodeKey]['effect_on_cure_teams'];
                                    $scope.effectOn.virus_understanding = $scope.effectOn.virus_understanding + 
                                        $scope.htech[nodeKey]['effect_on_virus_understanding'];
                                    $scope.effectOn.cure_research = $scope.effectOn.cure_research + 
                                        $scope.htech[nodeKey]['effect_on_cure_research'];
                                    $scope.effectOn.public_awareness = $scope.effectOn.public_awareness + 
                                        $scope.htech[nodeKey]['effect_on_public_awareness'];
                                    $scope.effectOn.disease_control = $scope.effectOn.disease_control + 
                                        $scope.htech[nodeKey]['effect_on_disease_control'];

                                    activatedThisTurnHealth.push(nodeKey);
                                    activatedDict[selectedNode['property']] = nodeRowNumber;

                                    $scope.htech[nodeKey]['active'] = true;

                                    $scope.data.removeRow(nodeRowNumber);

                                    if (selectedNode.parent === 0){
                                        var rowData = [
                                            [{v: selectedNode.property, f: selectedNode.display_active }, 
                                             '', selectedNode.property]
                                        ];                                      
                                    } else{
                                        var rowData = [
                                            [{v: selectedNode.property, f: selectedNode.display_active }, 
                                             selectedNode.parent, 
                                             selectedNode.property]
                                        ];
                                    }
                                    $scope.data.insertRows(nodeRowNumber, rowData);
                                    healthGoogleOrgChart.setSelection(); 
                                    // clears selection to prevent multiple clicks being
                                    // required to unselect it
                                }
                                
                            }

                        }
                        
                    }
                }


                $scope.$apply(); // update data, forcing $watch to fire
            }

            // watch the data and redraw if changes. Done so that map reloads after GET has completed
            $scope.$watch('data', function(v) {

                // var data = google.visualization.arrayToDataTable(v);
                var options = {allowHtml: true,
                               nodeClass: "techtreenode",
                               selectedNodeClass: "selectedtechtreenode",
                               size: "large"
                              };
                healthGoogleOrgChart.draw(v, options);
            }, true);

        }
    };
});
