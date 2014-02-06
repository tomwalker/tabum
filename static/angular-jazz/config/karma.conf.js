module.exports = function(config){
    config.set({
    basePath : '../',

    files : [
      'app/lib/angular/angular.js',
      'app/lib/angular/*.js',
      'test/lib/angular/angular-mocks.js',
      'app/js/services.js',
      'test/unit/servicesSpec.js',
	  // 'app/js/controllers_*.js',
      // 'test/unit/controllersSpec.js'
      // 'app/js/**/*.js',
      // 'test/unit/**/*.js'
    ],

    autoWatch : true,

    frameworks: ['jasmine'],

    browsers : ['Firefox'],

    plugins : [
            'karma-junit-reporter',
            'karma-chrome-launcher',
            'karma-firefox-launcher',
            'karma-jasmine'       
            ],

    junitReporter : {
      outputFile: 'test_out/unit.xml',
      suite: 'unit'
    }

})}
