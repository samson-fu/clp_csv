docker build -t hkclp-powermeter .
docker image save hkclp-powermeter -o hkclp-powermeter.tar

if exist \\FuNas1\download\ (
    copy hkclp-powermeter.tar \\FuNas1\download
)

docker image rm hkclp-powermeter
