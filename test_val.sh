# Validate example data using jing and trang

trang xml/manifest.rnc /tmp/manifest.rng
for a in examples/*; do
    echo Validating: $a
    jing /tmp/manifest.rng $a/manifest.xml
done
