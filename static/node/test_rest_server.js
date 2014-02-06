var express = require('express');
var app = express();

var fake_session_database = [
  { id : 1, turn_data : {
    "next_to_play": "V",
    "countries": {
        "china": {
            "population": {
                "healthy": 1400000000,
                "infected": 10,
                "dead": 1
            },
            "climate": "TEMPERATE",
            "healthcare": 4,
            "land_links": [
                "india",
                "nepal",
                "thailand",
                "korea",
                "japan"
            ],
            "air_links": [
                "USA",
                "japan",
                "spain"
            ],
            "sea_links": [
                "australia",
                "britain",
                "germany"
            ]
        },
        "paraguay": {
            "population": {
                "healthy": 1000000,
                "infected": 0,
                "dead": 0
            },
            "climate": "TROPICAL",
            "healthcare": 7,
            "land_links": [
                "india",
                "nepal",
                "thailand",
                "korea",
                "japan"
            ],
            "air_links": [
                "USA",
                "spain"
            ],
            "sea_links": [
                "australia",
                "britain",
                "germany"
            ]
        },
        "ireland": {
            "population": {
                "healthy": 432400,
                "infected": 488390,
                "dead": 90907930
            },
            "climate": "TEMPERATE",
            "healthcare": 7,
            "land_links": [
                "UK"
            ],
            "air_links": [
                "USA",
                "spain",
                "china"
            ],
            "sea_links": [
                "australia",
                "britain",
                "germany"
            ]
        }
    },
    "virus_player": {
        "agent": "HIV",
        "points": 50,
        "shift": 0.16,
        "infectivity": 4,
        "lethality": 7,
        "resistance": [
            "hot",
            "drug",
            "exam"
        ],
        "infected_countries": [
            "australia",
            "UK",
            "Indonesia"
        ],
        "air_spread": 3,
        "land_spread": 1,
        "sea_spread": 3
    },
    "health_player": {
        "points": 60,
        "field_researchers": {
            "africa": 1,
            "china": 3
        },
        "control_teams": {
            "UK": 1,
            "iceland": 3
        },
        "virus_understanding": 43,
        "cure_research": 20,
        "public_awareness": 70,
        "disease_control": 11
    }
}
},
  { id : 2, turn_data : {
    "next_to_play": "H",
    "countries": {
        "china": {
            "population": {
                "healthy": 1400000000,
                "infected": 10,
                "dead": 1
            },
            "climate": "TEMPERATE",
            "healthcare": 4,
            "land_links": [
                "india",
                "nepal",
                "thailand",
                "korea",
                "japan"
            ],
            "air_links": [
                "USA",
                "japan",
                "spain"
            ],
            "sea_links": [
                "australia",
                "britain",
                "germany"
            ]
        },
        "Bolivia": {
            "population": {
                "healthy": 4300000,
                "infected": 0,
                "dead": 100
            },
            "climate": "TROPICAL",
            "healthcare": 8,
            "land_links": [
                "india",
                "nepal",
                "thailand",
                "korea",
                "japan"
            ],
            "air_links": [
                "USA",
				"Argentina",
                "spain"
            ],
            "sea_links": [
                "australia",
                "britain",
				"Brazil",
                "germany"
            ]
        },
        "Belgium": {
            "population": {
                "healthy": 4322400,
                "infected": 488390,
                "dead": 90907930
            },
            "climate": "TEMPERATE",
            "healthcare": 7,
            "land_links": [
                "UK"
            ],
            "air_links": [
                "USA",
                "spain",
                "china"
            ],
            "sea_links": [
                "australia",
                "britain",
                "germany"
            ]
        }
    },
    "virus_player": {
        "agent": "the shits",
        "points": 10,
        "shift": 0.56,
        "infectivity": 2,
        "lethality": 10,
        "resistance": [
            "hot",
            "exam"
        ],
        "infected_countries": [
            "australia",
            "Indonesia"
        ],
        "air_spread": 3,
        "land_spread": 1,
        "sea_spread": 3
    },
    "health_player": {
        "points": 60,
        "field_researchers": {
            "africa": 1,
            "china": 3
        },
        "control_teams": {
            "UK": 1,
            "iceland": 3
        },
        "virus_understanding": 43,
        "cure_research": 20,
        "public_awareness": 70,
        "disease_control": 11
    }
}
},
];

app.use(express.bodyParser());

app.all('/*', function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "X-Requested-With");
  next();
});

app.get('/', function(req, res) {
  res.json(fake_session_database);
});

app.get('/random', function(req, res) {
  var id = Math.floor(Math.random() * fake_session_database.length);
  var q = fake_session_database[id];
  res.json(q);
});


app.get('/play/:id/ag', function(req, res) {
  if(fake_session_database.length < req.params.id || req.params.id < 0) {
    res.statusCode = 404;
    return res.send('Error 404: Nothing found');
  }
  console.log('the game');
  var q = fake_session_database[req.params.id - 1];
  res.json(q);
});


app.post('/play/:id/ag', function(req, res) {
  if(!req.body.hasOwnProperty('property_changes') 
	 || !req.body.hasOwnProperty('choice_outcome')) {
    res.statusCode = 400;
    return res.send('Error 400: Post syntax incorrect.');
  }

  var newDBentry = {
    id : req.body.property_changes,
    turn_data : req.body.choice_outcome
  };

  fake_session_database.push(newDBentry);
  res.send('complete');
});

app.delete('/quote/:id', function(req, res) {
  if(fake_session_database.length <= req.params.id) {
    res.statusCode = 404;
    return res.send('Error 404: No quote found');
  }

  fake_session_database.splice(req.params.id, 1);
  res.json(true);
});

app.listen(process.env.PORT || 3412);






