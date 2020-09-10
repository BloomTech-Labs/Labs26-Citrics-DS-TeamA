const fs = require('fs');

// Function for Reading the .json file
function jsonReader(filePath, cb) {
    fs.readFile(filePath, 'utf-8', (err, fileData) => {
        if (err) {
            return cb && cb(err)
        }
        try {
            const object = JSON.parse(fileData);
            return cb && cb(null, object);
        } catch (err) {
            return cb && cb(err);
        }
    });
}

const fileName = './Dockerrun.aws.json';
const file = require(fileName);

// Taking command line input
var standard_input = process.stdin;
standard_input.setEncoding('utf-8');

console.log("Docker ID")
console.log("---------")

standard_input.on('data', function(data) {
    if (data == 'exit\n') {
        console.log("Exiting program...");
        process.exit();
    } else {
        // Overwriting existing Image Name in Dockerrun.aws.json
        file.Image.Name = data.slice(0, data.length - 1) + "/labs26-citrics-ds-teama_web:latest"
        fs.writeFile(fileName, JSON.stringify(file, null, 2), function writeJSON(err) {
            if (err) return console.log(err);
            console.log(JSON.stringify(file, null, 2));
            console.log('writing to ' + fileName);
            process.exit();
        });
    }
});
