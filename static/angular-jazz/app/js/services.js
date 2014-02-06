'use strict';

/* Services */


var services = angular.module('tabum.services', ['ngResource']);

services.factory('TurnData', ['$resource', '$location',
    function($resource, $location) {
        return $resource('http://' + $location.host() + '\\:8000/play/:id/ag/',
                        {id: '@id'},
                        {finish: {method:'POST', isArray:false}});
    }
]);





