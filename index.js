var jsonMap = require("json-source-map");
var source = process.argv[2];
var result = jsonMap.parse(source);
console.log(result.pointers);
