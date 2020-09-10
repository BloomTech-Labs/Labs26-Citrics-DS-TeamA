const Dockerrun = require('./Dockerrun.aws.json')
const fs = require('fs');

var env = require('./env');

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

file.Image.Name = env.DOCKER_ID + "/" + env.DOCKER_IMAGE + ":" + env.DOCKER_IMAGE_TAG

// Function for overwriting data in the .json file
fs.writeFile(fileName, JSON.stringify(file, null, 2), function writeJSON(err) {
  if (err) return console.log(err);
  console.log(JSON.stringify(file));
  console.log('writing to ' + fileName);
});

jsonReader('./Dockerrun.aws.json', (err, data) => {
    if (err) {
        console.log(err);
    } else {
        console.log(data)
    }
});