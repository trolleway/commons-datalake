docker build --tag commons-datalake:2024.02 .

docker run --rm -v "${PWD}:/opt/commons-datalake" -it commons-datalake:2024.02
