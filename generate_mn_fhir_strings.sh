# usage: generate_mn_fhir_strings.sh < en_fhir.json > mn_fhir.json
sed 's/": "/": "⠿⠿/g' | sed 's/",/~~",/g' | sed 's/"$/~~"/g'
