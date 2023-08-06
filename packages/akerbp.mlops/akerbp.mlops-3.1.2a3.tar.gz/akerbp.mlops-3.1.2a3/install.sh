# install.sh
VERSION=$(git describe --tags --abbrev=0)

# Try to install (max 20 retries)
n=0
until [ "$n" -ge 19 ]
do
    pip install "akerbp.mlops[cdf]==$VERSION" && break
    n=$((n+1))
    sleep 15
done
