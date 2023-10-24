trang xml/manifest.rnc xml/manifest.rng
for a in examples/*; do
    echo Validating: $a
    jing xml/manifest.rng $a/manifest.xml
done
