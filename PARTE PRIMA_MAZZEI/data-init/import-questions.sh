#!/bin/bash
echo "Importing questions into MongoDB..."
mongoimport --db Lara_challange --collection Questions --file /tmp/Questions.json --jsonArray
echo "Import questions completed."