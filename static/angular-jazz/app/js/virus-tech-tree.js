"use strict";

var googleChart = googleChart || angular.module("google-chart",[]),
    google;

googleChart.directive("virusTechTree",function(){
    return{
        restrict : "A",
        scope : {
            data: '=data',
            vtech: '=vtech',
            points: '=points',
            effectOn: '=effect'
            
        },
        link: function($scope, $elem, $attr){
            var googleOrgChart = new google.visualization.OrgChart($elem[0]);
            var activatedThisTurn = [];
            var activatedDict = {};
            
            google.visualization.events.addListener(googleOrgChart, 'select', selectHandler);

            function removeNode(node, nodeKey, nodeRowNumber) {
                var node_index = activatedThisTurn.indexOf(nodeKey);
                activatedThisTurn.splice(node_index, 1);

                $scope.vtech[nodeKey.toLowerCase()]['active'] = false;

                $scope.effectOn.infectivity = $scope.effectOn.infectivity - 
                    $scope.vtech[nodeKey]['effect_on_infectivity'];
                $scope.effectOn.lethality = $scope.effectOn.lethality - 
                    $scope.vtech[nodeKey]['effect_on_lethality'];
                $scope.effectOn.land_spread = $scope.effectOn.land_spread - 
                    $scope.vtech[nodeKey]['effect_on_land_spread'];
                $scope.effectOn.sea_spread = $scope.effectOn.sea_spread - 
                    $scope.vtech[nodeKey]['effect_on_sea_spread'];
                $scope.effectOn.air_spread = $scope.effectOn.air_spread - 
                    $scope.vtech[nodeKey]['effect_on_air_spread'];
                $scope.effectOn.shift = $scope.effectOn.shift - 
                    $scope.vtech[nodeKey]['effect_on_shift'];

                $scope.points = $scope.points + $scope.vtech[nodeKey]['cost'];

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
                googleOrgChart.setSelection();
                //console.log($scope.data);
            }
            
            function requiredCheck(selectedNode, allNodes) {
                // console.log(activatedDict);
                // console.log(activatedThisTurn);
                // console.log(selectedNode.property);
                for (var i = 0, ln = activatedThisTurn.length; i < ln; i++){
                    //console.log(allNodes[activatedThisTurn[i]]);
                    // console.log(allNodes[activatedThisTurn[i]]['requires']);
                    // if item requires currently selected node
                    if (allNodes[activatedThisTurn[i]]['requires'] !== '') {
                        if (allNodes[activatedThisTurn[i]]['requires'].indexOf(selectedNode.property) >= 0){
                            // console.log(allNodes[activatedThisTurn[i]]['property']);
                            var nodeToRemove = allNodes[activatedThisTurn[i]];
                            removeNode(allNodes[activatedThisTurn[i]],
                                       activatedThisTurn[i], activatedDict[activatedThisTurn[i]]);
                            requiredCheck(nodeToRemove, allNodes);
                        }
                    }
                }
            } // end of requiredCheck

            function selectHandler() {

                if (googleOrgChart.getSelection().length !== 0){
                    var nodeRowNumber = googleOrgChart.getSelection()[0]['row'];
                    var allNodes = $scope.vtech;
		    var nodeKey = allNodes['treePositions'][nodeRowNumber];
                    var selectedNode = allNodes[nodeKey.toLowerCase()];

                    if (selectedNode['selectable'] === true && selectedNode['already-active'] != true) {

                        // if it is, check if its in list of nodes activated during this turn and
                        // deactivate it by removing it from list, setting active false, removing
                        // points from effectOn, adding cost back to point and redrawing node

                        if (activatedThisTurn.indexOf(selectedNode['property']) >= 0) {
                            
                            removeNode(selectedNode, nodeKey, nodeRowNumber);
                            //console.log(selectedNode);
                            // for each item in activatedThisTurn
                            requiredCheck(selectedNode, allNodes);
                            // change to inactive, refund points, remove effect_on

                        } else {
                            // if not, check if required nodes are active
                            var requiredNodes = selectedNode.requires;  // list of required
                            var allBelowActive = 0;
                            for (var i = 0, ln = requiredNodes.length; i < ln; i++) {
                                var x = requiredNodes[i];
                                if ($scope.vtech[x]['active'] === false){
                                    allBelowActive++;
                                };
                            }
                            // if all necessary are active, check if enough points are
                            // available
                            if (allBelowActive === 0){ 
                                var cost = $scope.vtech[nodeKey]['cost'];
                                
                                // if enough points are available, remove cost from points,
                                // set node as active, add points to effectOn, add to the
                                // activatedThisTurn list, set it to active then change node
                                // to display active
                                if (cost <= $scope.points){
                                    $scope.points = $scope.points - cost;
                                    $scope.vtech[nodeKey]['active'] = true;

                                    //console.log($scope.effectOn);
                                    $scope.effectOn.infectivity = $scope.effectOn.infectivity + 
                                        $scope.vtech[nodeKey]['effect_on_infectivity'];
                                    $scope.effectOn.lethality = $scope.effectOn.lethality + 
                                        $scope.vtech[nodeKey]['effect_on_lethality'];
                                    $scope.effectOn.land_spread = $scope.effectOn.land_spread + 
                                        $scope.vtech[nodeKey]['effect_on_land_spread'];
                                    $scope.effectOn.sea_spread = $scope.effectOn.sea_spread + 
                                        $scope.vtech[nodeKey]['effect_on_sea_spread'];
                                    $scope.effectOn.air_spread = $scope.effectOn.air_spread + 
                                        $scope.vtech[nodeKey]['effect_on_air_spread'];
                                    $scope.effectOn.shift = $scope.effectOn.shift + 
                                        $scope.vtech[nodeKey]['effect_on_shift'];
                                    //console.log($scope.effectOn);

                                    activatedThisTurn.push(nodeKey);
                                    //console.log(activatedThisTurn);
                                    activatedDict[selectedNode['property']] = nodeRowNumber;

                                    $scope.vtech[nodeKey]['active'] = true;

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
                                    googleOrgChart.setSelection(); 
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
                googleOrgChart.draw(v, options);
            }, true);

        }
    };
});






